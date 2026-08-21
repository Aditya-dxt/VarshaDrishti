"""
VarshaDrishti — Multi-Temporal Preprocessing Core
Processes N matched L1B/L2B pairs into spatially-consistent temporal sequences.
"""

import sys
import json
import h5py
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.calibration import calibrate_channel
from src.data.geolocation import decode_geolocation
from src.data.rainfall import load_rainfall
from src.data.patching import generate_patches, classify_patch_rainfall
from src.data.sequence_builder import build_temporal_sequences


def _load_one_timestamp(
    l1b_path: str,
    l2b_path: str,
    channels: List[str],
    l1b_fill: int,
    l2b_fill: float,
    geo_fill: int,
    geo_scale: float,
    use_gsics: bool = False
) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray, Tuple[int, int]]:
    """
    Opens one L1B + L2B pair and returns:
      channel_data  : {ch_name: float64 radiance array [H, W]}
      imc           : float64 rainfall [H, W]  (NaN where invalid)
      global_mask   : bool [H, W] — pixel valid across all channels + geo + rain
      lat           : float64 decoded latitude [H, W]
      grid_shape    : (H, W)
    """
    with h5py.File(l1b_path, "r") as fl, h5py.File(l2b_path, "r") as fr:
        # Geolocation
        lat, lon = decode_geolocation(
            fl["Latitude"], fl["Longitude"],
            fill_value=geo_fill, scale_factor=geo_scale
        )
        valid_geo = ~np.isnan(lat) & ~np.isnan(lon)
        shape = lat.shape

        # Channels
        channel_data = {}
        for ch in channels:
            rad, _ = calibrate_channel(fl[ch], fill_value=l1b_fill, use_gsics=use_gsics)
            channel_data[ch] = rad

        # Rainfall
        imc = load_rainfall(fr["IMC"], fill_value=l2b_fill)
        valid_rain = ~np.isnan(imc)

        # Global mask
        gmask = valid_geo & valid_rain
        for ch in channels:
            gmask &= ~np.isnan(channel_data[ch])

    return channel_data, imc, gmask, lat, shape


def compute_intersection_mask(
    matched_pairs: List[Dict[str, Any]],
    channels: List[str],
    l1b_fill: int,
    l2b_fill: float,
    geo_fill: int,
    geo_scale: float
) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Computes the intersection of validity masks across the timestamps of ONE
    temporal sequence. Independent events must not share this mask.
    """
    intersection = None
    grid_shape = None

    for pair in matched_pairs:
        _, _, gmask, _, shape = _load_one_timestamp(
            pair["l1b_path"], pair["l2b_path"],
            channels, l1b_fill, l2b_fill, geo_fill, geo_scale
        )
        if intersection is None:
            intersection = gmask.copy()
            grid_shape = shape
        else:
            if shape != grid_shape:
                raise ValueError(
                    f"Grid shape mismatch: {shape} vs {grid_shape} at {pair['l1b_path']}"
                )
            intersection &= gmask

    return intersection, grid_shape


def resolve_temporal_sequences(
    matched_pairs: List[Dict[str, Any]],
    config: dict
) -> Tuple[List[List[Dict[str, Any]]], int, int]:
    """
    Split chronologically ordered matched pairs into independent seq_length-frame
    sequences. Never concatenates across timestamp gaps.
    """
    seq_cfg = config.get("sequencing", {})
    sequence_length = int(seq_cfg.get("sequence_length", 6))
    step_minutes = int(seq_cfg.get("temporal_step_minutes", 30))

    sequences = build_temporal_sequences(
        matched_pairs,
        sequence_length=sequence_length,
        step_minutes=step_minutes,
    )
    if not sequences:
        raise RuntimeError(
            f"No valid {sequence_length}-frame temporal sequences were found. "
            "Matched L1B/L2B pairs must not be stacked across continuity gaps."
        )
    for seq in sequences:
        if len(seq) != sequence_length:
            raise RuntimeError(
                f"Internal error: sequence length {len(seq)} != configured {sequence_length}."
            )
    return sequences, sequence_length, step_minutes


def _assign_labels(targets: np.ndarray, masks: np.ndarray, thresholds: dict) -> np.ndarray:
    n = targets.shape[0]
    labels = np.zeros((n,), dtype=np.int64)
    for p_idx in range(n):
        valid_px = targets[p_idx][masks[p_idx]]
        max_rain = float(np.nanmax(valid_px)) if valid_px.size > 0 else 0.0
        if max_rain <= thresholds["no_rain"]:
            labels[p_idx] = 0
        elif max_rain <= thresholds["moderate"]:
            labels[p_idx] = 1
        elif max_rain <= thresholds["heavy"]:
            labels[p_idx] = 2
        else:
            labels[p_idx] = 3
    return labels


def _process_one_temporal_sequence(
    seq_pairs: List[Dict[str, Any]],
    config: dict,
    sequence_length: int,
) -> Dict[str, Any]:
    """
    Materialize one continuous seq_length-frame event.
    Intersection mask, patches, and normalization are computed inside this
    sequence only — never across independent events.
    """
    if len(seq_pairs) != sequence_length:
        raise ValueError(
            f"Refusing to materialize a {len(seq_pairs)}-frame tensor. "
            f"Configured sequence_length is {sequence_length}."
        )
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    channels = data_cfg["channels"]
    T = sequence_length

    intersection_mask, grid_shape = compute_intersection_mask(
        seq_pairs, channels,
        data_cfg["l1b_fill_value"], data_cfg["l2b_fill_value"],
        data_cfg["geo_fill_value"], data_cfg["geo_scale_factor"]
    )

    patches = generate_patches(
        image_shape=grid_shape,
        patch_size=patch_cfg["size"],
        stride=patch_cfg["stride"],
        valid_mask=intersection_mask,
        min_valid_pct=patch_cfg["min_valid_pixels_pct"]
    )
    if not patches:
        raise RuntimeError("No valid patches found for a temporal sequence.")

    N = len(patches)
    C = len(channels)
    H = W = patch_cfg["size"]

    sequences = np.zeros((N, C, T, H, W), dtype=np.float32)
    targets = np.zeros((N, H, W), dtype=np.float32)
    masks = np.zeros((N, H, W), dtype=bool)
    norm_stats = {ch: {"sum": 0.0, "sum_sq": 0.0, "count": 0} for ch in channels}

    for t_idx, pair in enumerate(seq_pairs):
        channel_data, imc, _, _, _ = _load_one_timestamp(
            pair["l1b_path"], pair["l2b_path"],
            channels, data_cfg["l1b_fill_value"], data_cfg["l2b_fill_value"],
            data_cfg["geo_fill_value"], data_cfg["geo_scale_factor"]
        )

        for ch in channels:
            valid_px = channel_data[ch][intersection_mask]
            norm_stats[ch]["sum"] += float(np.nansum(valid_px))
            norm_stats[ch]["sum_sq"] += float(np.nansum(valid_px ** 2))
            norm_stats[ch]["count"] += int(np.sum(~np.isnan(valid_px)))

        for p_idx, (r1, r2, c1, c2) in enumerate(patches):
            for c_idx, ch in enumerate(channels):
                sequences[p_idx, c_idx, t_idx] = channel_data[ch][r1:r2, c1:c2].astype(np.float32)
            if t_idx == T - 1:
                targets[p_idx] = imc[r1:r2, c1:c2].astype(np.float32)
                masks[p_idx] = intersection_mask[r1:r2, c1:c2]

    final_norm = {}
    for ch in channels:
        n = norm_stats[ch]["count"]
        s = norm_stats[ch]["sum"]
        sq = norm_stats[ch]["sum_sq"]
        mean = s / n if n > 0 else 0.0
        std = np.sqrt(sq / n - mean ** 2) if n > 0 else 1.0
        final_norm[ch] = {"mean": float(mean), "std": float(std)}

    for c_idx, ch in enumerate(channels):
        m = final_norm[ch]["mean"]
        s = final_norm[ch]["std"] + 1e-8
        channel = sequences[:, c_idx, :, :, :]
        # Patches may include <10% invalid pixels; fill with the sequence
        # channel mean so standardized invalid pixels become 0, never NaN.
        channel = np.where(np.isnan(channel), m, channel)
        sequences[:, c_idx, :, :, :] = (channel - m) / s

    labels = _assign_labels(targets, masks, rain_cfg)
    timestamps = [pair["timestamp"] for pair in seq_pairs]

    return {
        "sequences": sequences,
        "targets": targets,
        "labels": labels,
        "masks": masks,
        "patches": patches,
        "intersection_mask": intersection_mask,
        "grid_shape": grid_shape,
        "normalization_statistics": final_norm,
        "timestamps": timestamps,
        "source_l1b_files": [Path(pair["l1b_path"]).name for pair in seq_pairs],
        "source_l2b_files": [Path(pair["l2b_path"]).name for pair in seq_pairs],
    }


def dry_run_multitemporal(
    matched_pairs: List[Dict[str, Any]],
    config: dict
) -> Dict[str, Any]:
    """
    Dry-run: reports statistics and candidate patch counts WITHOUT writing data.
    Independent temporal events are processed separately. T is sequence_length.
    """
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    channels = data_cfg["channels"]
    temporal_seqs, sequence_length, step_minutes = resolve_temporal_sequences(matched_pairs, config)

    P = print

    P("=" * 70)
    P("VarshaDrishti -- Multi-Temporal Preprocessing DRY RUN")
    P("=" * 70)
    P(f"Matched timestamps : {len(matched_pairs)}")
    P(f"Temporal sequences : {len(temporal_seqs)}")
    P(f"Sequence Length T  : {sequence_length}")
    P(f"Temporal Step      : {step_minutes} min")
    P(f"Channels           : {channels}")
    P(f"Patch Size         : {patch_cfg['size']}x{patch_cfg['size']}")
    P(f"Stride             : {patch_cfg['stride']}")
    P(f"Min Valid Pixels   : {patch_cfg['min_valid_pixels_pct']}%")
    P()
    P("NOTE: Timestamp gaps are NOT treated as continuous. Each valid")
    P(f"{sequence_length}-frame run is an independent sample group.")
    P()

    C = len(channels)
    H = W = patch_cfg["size"]
    total_samples = 0
    per_seq_patches = []
    last_grid_shape = None
    last_intersection = None
    last_patches = []

    for seq_idx, seq_pairs in enumerate(temporal_seqs):
        P(f"--- Temporal sequence {seq_idx} ({len(seq_pairs)} frames) ---")
        for pair in seq_pairs:
            P(f"  {pair['timestamp'].isoformat()}  L1B={Path(pair['l1b_path']).name}  L2B={Path(pair['l2b_path']).name}")

        intersection_mask, grid_shape = compute_intersection_mask(
            seq_pairs, channels,
            data_cfg["l1b_fill_value"], data_cfg["l2b_fill_value"],
            data_cfg["geo_fill_value"], data_cfg["geo_scale_factor"]
        )
        last_grid_shape = grid_shape
        last_intersection = intersection_mask
        valid_pct = 100.0 * np.sum(intersection_mask) / intersection_mask.size
        P(f"  Grid shape            : {grid_shape}")
        P(f"  Intersection valid px : {np.sum(intersection_mask):,} ({valid_pct:.2f}%)")

        patches = generate_patches(
            image_shape=grid_shape,
            patch_size=patch_cfg["size"],
            stride=patch_cfg["stride"],
            valid_mask=intersection_mask,
            min_valid_pct=patch_cfg["min_valid_pixels_pct"]
        )
        last_patches = patches
        per_seq_patches.append(len(patches))
        total_samples += len(patches)
        P(f"  Candidate patches     : {len(patches)}")

        last_pair = seq_pairs[-1]
        with h5py.File(last_pair["l2b_path"], "r") as fr:
            last_imc = load_rainfall(fr["IMC"], fill_value=data_cfg["l2b_fill_value"])
        valid_rain = last_imc[intersection_mask]
        P(f"  Target rainfall min/max/mean: "
          f"{np.nanmin(valid_rain):.4f} / {np.nanmax(valid_rain):.4f} / {np.nanmean(valid_rain):.4f} mm/hr")

        no_rain_dominated = rainy = heavy = 0
        for r1, r2, c1, c2 in patches:
            counts = classify_patch_rainfall(last_imc[r1:r2, c1:c2], rain_cfg)
            if counts["total_valid"] == 0:
                continue
            no_rain_pct = 100.0 * counts["no_rain"] / counts["total_valid"]
            if no_rain_pct > 95.0:
                no_rain_dominated += 1
            else:
                rainy += 1
            if counts["heavy"] > 0 or counts["high_impact"] > 0:
                heavy += 1
        if patches:
            P(f"  No-rain dominated     : {no_rain_dominated}")
            P(f"  Rainy patches         : {rainy}")
            P(f"  Heavy+ patches        : {heavy}")
        P()

    seq_shape = (total_samples, C, sequence_length, H, W)
    expected_mb = (total_samples * C * sequence_length * H * W * 4) / (1024 ** 2)

    P("--- Expected Output ---")
    P(f"Independent temporal events : {len(temporal_seqs)}")
    P(f"Patches per event           : {per_seq_patches}")
    P(f"sequences.npy shape         : {list(seq_shape)}")
    P(f"targets.npy shape           : [{total_samples}, {H}, {W}]")
    P(f"T dimension                 : {sequence_length}  (NOT {len(matched_pairs)})")
    P(f"Estimated disk usage        : {expected_mb:.1f} MB")
    P()
    P("DRY RUN COMPLETE -- No data written.")

    return {
        "n_timestamps": len(matched_pairs),
        "n_temporal_sequences": len(temporal_seqs),
        "sequence_length": sequence_length,
        "grid_shape": last_grid_shape,
        "n_candidate_patches": total_samples,
        "patches_per_sequence": per_seq_patches,
        "patches": last_patches,
        "intersection_mask": last_intersection,
        "seq_shape": seq_shape,
    }


def materialize_multitemporal(
    matched_pairs: List[Dict[str, Any]],
    config: dict,
    out_dir: Path
) -> Dict[str, Any]:
    """
    Materialize independent seq_length-frame events, then stack along the sample axis.

    Output contract: [N, C, T, H, W] with T = sequencing.sequence_length.
    A 21-hour gap does not become a 12-frame tensor.
    """
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    channels = data_cfg["channels"]
    temporal_seqs, sequence_length, step_minutes = resolve_temporal_sequences(matched_pairs, config)

    processed = []
    for seq_pairs in temporal_seqs:
        processed.append(_process_one_temporal_sequence(seq_pairs, config, sequence_length))

    sequences = np.concatenate([p["sequences"] for p in processed], axis=0)
    targets = np.concatenate([p["targets"] for p in processed], axis=0)
    labels = np.concatenate([p["labels"] for p in processed], axis=0)
    masks = np.concatenate([p["masks"] for p in processed], axis=0)

    if sequences.shape[2] != sequence_length:
        raise RuntimeError(
            f"Temporal axis is {sequences.shape[2]}, expected T={sequence_length}. "
            "Independent events must not be concatenated along time."
        )

    N = sequences.shape[0]
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata").mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest").mkdir(parents=True, exist_ok=True)
    (out_dir / "masks").mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "data" / "sequences.npy", sequences)
    np.save(out_dir / "data" / "targets.npy", targets)
    np.save(out_dir / "data" / "labels.npy", labels)
    np.save(out_dir / "masks" / "masks.npy", masks)

    label_vals, label_counts = np.unique(labels, return_counts=True)
    class_dist = {int(lv): int(lc) for lv, lc in zip(label_vals, label_counts)}

    all_timestamps = []
    all_l1b = []
    all_l2b = []
    temporal_sequence_meta = []
    seq_manifest = []
    sample_offset = 0
    patches_per_sequence = []

    for seq_idx, item in enumerate(processed):
        n_patches = item["sequences"].shape[0]
        patches_per_sequence.append(n_patches)
        ts_iso = [t.isoformat() + "Z" for t in item["timestamps"]]
        all_timestamps.extend(ts_iso)
        all_l1b.extend(item["source_l1b_files"])
        all_l2b.extend(item["source_l2b_files"])
        temporal_sequence_meta.append({
            "sequence_id": seq_idx,
            "timestamps": ts_iso,
            "n_patches": n_patches,
            "sample_index_start": sample_offset,
            "sample_index_end": sample_offset + n_patches,
            "source_l1b_files": item["source_l1b_files"],
            "source_l2b_files": item["source_l2b_files"],
            "normalization_statistics": item["normalization_statistics"],
            "validity_statistics": {
                "intersection_valid_pixels": int(np.sum(item["intersection_mask"])),
                "total_pixels": int(item["intersection_mask"].size),
                "valid_pct": float(100.0 * np.sum(item["intersection_mask"]) / item["intersection_mask"].size),
            },
        })
        for local_idx, (r1, r2, c1, c2) in enumerate(item["patches"]):
            global_idx = sample_offset + local_idx
            valid_t = targets[global_idx][masks[global_idx]]
            seq_manifest.append({
                "patch_idx": global_idx,
                "temporal_sequence_id": seq_idx,
                "row_start": r1, "row_end": r2,
                "col_start": c1, "col_end": c2,
                "label": int(labels[global_idx]),
                "rainfall_mean": float(np.nanmean(valid_t)) if valid_t.size > 0 else 0.0,
                "rainfall_max": float(np.nanmax(valid_t)) if valid_t.size > 0 else 0.0,
                "timestamps": ts_iso,
            })
        sample_offset += n_patches

    n_events = len(temporal_seqs)
    metadata = {
        "WARNING": (
            "THIS IS A DEVELOPMENT ARTIFACT. Independent temporal events are stacked "
            "along the sample axis only. It MUST NOT be used for scientific model "
            "training, validation, testing, or performance claims."
        ),
        "artifact_type": "development_multitemporal_real_data",
        "scientific_training_ready": False,
        "training_ready_for_scientific_training": False,
        "training_not_ready_reason": (
            f"Only {n_events} independent temporal event(s) are available; additional "
            "independent weather events are required for a leakage-safe train/validation/test split."
        ),
        "source_timestamps": all_timestamps,
        "temporal_sequences": temporal_sequence_meta,
        "channels": channels,
        "channel_order": channels,
        "sequence_length": sequence_length,
        "temporal_step_minutes": step_minutes,
        "patch_size": patch_cfg["size"],
        "stride": patch_cfg["stride"],
        "calibration_method": "LAB_STANDARD_QUADRATIC",
        "normalization_method": "development_only_per_sequence_standard_scaling",
        "normalization_statistics": [p["normalization_statistics"] for p in processed],
        "rainfall_units": "mm/hr",
        "rainfall_fill_value": data_cfg["l2b_fill_value"],
        "l1b_fill_value": data_cfg["l1b_fill_value"],
        "input_shape": list(sequences.shape),
        "target_shape": list(targets.shape),
        "number_of_sequences": n_events,
        "number_of_temporal_sequences": n_events,
        "number_of_samples": N,
        "number_of_spatial_patches": N,
        "patches_per_temporal_sequence": patches_per_sequence,
        "rainfall_class_thresholds": rain_cfg,
        "source_l1b_files": all_l1b,
        "source_l2b_files": all_l2b,
        "class_distribution": class_dist,
        "validity_statistics": temporal_sequence_meta[0]["validity_statistics"],
        "created_at": datetime.utcnow().isoformat(),
    }

    with open(out_dir / "metadata" / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    with open(out_dir / "manifest" / "sequence_manifest.json", "w") as f:
        json.dump(seq_manifest, f, indent=2)

    print(f"Temporal sequences : {n_events}")
    print(f"Sequence length T  : {sequence_length}")
    print(f"Patches per event  : {patches_per_sequence}")
    print(f"Total samples      : {N}")

    return metadata
