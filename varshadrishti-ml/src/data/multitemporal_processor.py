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
    Computes the intersection of global validity masks across ALL timestamps.
    A pixel is valid only if it is valid in every single timestamp.
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


def dry_run_multitemporal(
    matched_pairs: List[Dict[str, Any]],
    config: dict
) -> Dict[str, Any]:
    """
    Dry-run: reports statistics and candidate patch counts WITHOUT writing data.
    """
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    seq_cfg = config.get("sequencing", {})
    channels = data_cfg["channels"]

    P = print  # alias for readability

    P("=" * 70)
    P("VarshaDrishti -- Multi-Temporal Preprocessing DRY RUN")
    P("=" * 70)
    P(f"Timestamps        : {len(matched_pairs)}")
    P(f"Sequence Length   : {seq_cfg.get('sequence_length', len(matched_pairs))}")
    P(f"Temporal Step     : {seq_cfg.get('temporal_step_minutes', 30)} min")
    P(f"Channels          : {channels}")
    P(f"Patch Size        : {patch_cfg['size']}x{patch_cfg['size']}")
    P(f"Stride            : {patch_cfg['stride']}")
    P(f"Min Valid Pixels  : {patch_cfg['min_valid_pixels_pct']}%")
    P()

    for pair in matched_pairs:
        P(f"  {pair['timestamp'].isoformat()}  L1B={Path(pair['l1b_path']).name}  L2B={Path(pair['l2b_path']).name}")

    P()
    P("--- Computing Intersection Validity Mask ---")
    intersection_mask, grid_shape = compute_intersection_mask(
        matched_pairs, channels,
        data_cfg["l1b_fill_value"], data_cfg["l2b_fill_value"],
        data_cfg["geo_fill_value"], data_cfg["geo_scale_factor"]
    )

    valid_pct = 100.0 * np.sum(intersection_mask) / intersection_mask.size
    P(f"Common Grid Shape       : {grid_shape}")
    P(f"Intersection Valid Px   : {np.sum(intersection_mask):,} ({valid_pct:.2f}%)")
    P()

    # Generate patches on the intersection mask
    patches = generate_patches(
        image_shape=grid_shape,
        patch_size=patch_cfg["size"],
        stride=patch_cfg["stride"],
        valid_mask=intersection_mask,
        min_valid_pct=patch_cfg["min_valid_pixels_pct"]
    )

    P("--- Candidate Patches ---")
    P(f"Candidate patches (intersection mask, min {patch_cfg['min_valid_pixels_pct']}% valid): {len(patches)}")

    # Per-timestamp rainfall stats for final timestamp (target)
    last_pair = matched_pairs[-1]
    with h5py.File(last_pair["l2b_path"], "r") as fr:
        last_imc = load_rainfall(fr["IMC"], fill_value=data_cfg["l2b_fill_value"])

    valid_rain = last_imc[intersection_mask]
    P()
    P("--- Rainfall Statistics (Final Timestamp) ---")
    P(f"Valid Rain Pixels : {valid_rain.size:,}")
    P(f"Min               : {np.nanmin(valid_rain):.4f} mm/hr")
    P(f"Max               : {np.nanmax(valid_rain):.4f} mm/hr")
    P(f"Mean              : {np.nanmean(valid_rain):.4f} mm/hr")
    P(f"Std               : {np.nanstd(valid_rain):.4f} mm/hr")

    # Rainfall class distribution across all patches
    no_rain_dominated = rainy = heavy = 0
    for r1, r2, c1, c2 in patches:
        rain_patch = last_imc[r1:r2, c1:c2]
        counts = classify_patch_rainfall(rain_patch, rain_cfg)
        if counts["total_valid"] == 0:
            continue
        no_rain_pct = 100.0 * counts["no_rain"] / counts["total_valid"]
        if no_rain_pct > 95.0:
            no_rain_dominated += 1
        else:
            rainy += 1
        if counts["heavy"] > 0 or counts["high_impact"] > 0:
            heavy += 1

    P()
    P("--- Patch Rainfall Classes (Final Timestamp) ---")
    if patches:
        P(f"No-rain dominated (>95%): {no_rain_dominated} ({100*no_rain_dominated/len(patches):.1f}%)")
        P(f"Rainy (>5% rain)        : {rainy} ({100*rainy/len(patches):.1f}%)")
        P(f"Heavy+ rain patches     : {heavy} ({100*heavy/len(patches):.1f}%)")

    # Expected output shape
    C = len(channels)
    T = len(matched_pairs)
    H = W = patch_cfg["size"]
    n_patches = len(patches)
    seq_shape = f"[{n_patches}, {C}, {T}, {H}, {W}]"
    expected_bytes = n_patches * C * T * H * W * 4  # float32
    expected_mb = expected_bytes / (1024 ** 2)

    P()
    P("--- Expected Output ---")
    P(f"sequences.npy shape : {seq_shape}")
    P(f"targets.npy shape   : [{n_patches}, {H}, {W}]")
    P(f"labels.npy shape    : [{n_patches}]")
    P(f"Estimated disk usage: {expected_mb:.1f} MB")
    P()
    P("DRY RUN COMPLETE -- No data written.")

    return {
        "n_timestamps": len(matched_pairs),
        "grid_shape": grid_shape,
        "n_candidate_patches": len(patches),
        "patches": patches,
        "intersection_mask": intersection_mask,
        "seq_shape": (n_patches, C, T, H, W),
    }


def materialize_multitemporal(
    matched_pairs: List[Dict[str, Any]],
    config: dict,
    out_dir: Path
) -> Dict[str, Any]:
    """
    Materializes the multi-temporal artifact to disk.
    Returns metadata dict.
    """
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    channels = data_cfg["channels"]

    # --- Intersection Mask ---
    intersection_mask, grid_shape = compute_intersection_mask(
        matched_pairs, channels,
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
        raise RuntimeError("No valid patches found across all timestamps.")

    N = len(patches)
    C = len(channels)
    T = len(matched_pairs)
    H = W = patch_cfg["size"]

    sequences = np.zeros((N, C, T, H, W), dtype=np.float32)
    targets   = np.zeros((N, H, W), dtype=np.float32)
    labels    = np.zeros((N,), dtype=np.int64)
    masks     = np.zeros((N, H, W), dtype=bool)

    # Collect per-timestamp normalization stats (development only)
    norm_stats = {ch: {"sum": 0.0, "sum_sq": 0.0, "count": 0} for ch in channels}

    # Load each timestamp
    for t_idx, pair in enumerate(matched_pairs):
        channel_data, imc, gmask, _, _ = _load_one_timestamp(
            pair["l1b_path"], pair["l2b_path"],
            channels, data_cfg["l1b_fill_value"], data_cfg["l2b_fill_value"],
            data_cfg["geo_fill_value"], data_cfg["geo_scale_factor"]
        )

        # Accumulate stats for normalization
        for ch in channels:
            valid_px = channel_data[ch][intersection_mask]
            norm_stats[ch]["sum"]    += float(np.nansum(valid_px))
            norm_stats[ch]["sum_sq"] += float(np.nansum(valid_px ** 2))
            norm_stats[ch]["count"]  += int(np.sum(~np.isnan(valid_px)))

        # Fill patch arrays for this timestamp
        for p_idx, (r1, r2, c1, c2) in enumerate(patches):
            for c_idx, ch in enumerate(channels):
                sequences[p_idx, c_idx, t_idx] = channel_data[ch][r1:r2, c1:c2].astype(np.float32)

            # Target and mask are taken from FINAL timestamp only
            if t_idx == T - 1:
                targets[p_idx] = imc[r1:r2, c1:c2].astype(np.float32)
                masks[p_idx]   = intersection_mask[r1:r2, c1:c2]

    # Finalize normalization stats
    final_norm = {}
    for ch in channels:
        n  = norm_stats[ch]["count"]
        s  = norm_stats[ch]["sum"]
        sq = norm_stats[ch]["sum_sq"]
        mean = s / n if n > 0 else 0.0
        std  = np.sqrt(sq / n - mean ** 2) if n > 0 else 1.0
        final_norm[ch] = {"mean": float(mean), "std": float(std)}

    # Apply normalization in-place
    for c_idx, ch in enumerate(channels):
        m = final_norm[ch]["mean"]
        s = final_norm[ch]["std"] + 1e-8
        sequences[:, c_idx, :, :, :] = (sequences[:, c_idx, :, :, :] - m) / s

    # Assign labels (dominant class of final-timestamp rainfall max in patch)
    thresholds = rain_cfg
    for p_idx in range(N):
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

    # Save arrays
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata").mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest").mkdir(parents=True, exist_ok=True)
    (out_dir / "masks").mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "data" / "sequences.npy", sequences)
    np.save(out_dir / "data" / "targets.npy", targets)
    np.save(out_dir / "data" / "labels.npy", labels)
    np.save(out_dir / "masks" / "masks.npy", masks)

    # Class distribution
    label_vals, label_counts = np.unique(labels, return_counts=True)
    class_dist = {int(lv): int(lc) for lv, lc in zip(label_vals, label_counts)}

    # Metadata
    metadata = {
        "WARNING": "THIS IS A SINGLE-TEMPORAL-SEQUENCE DEVELOPMENT ARTIFACT. IT MUST NOT BE USED FOR SCIENTIFIC MODEL TRAINING, VALIDATION, TESTING, OR PERFORMANCE CLAIMS.",
        "artifact_type": "development_multitemporal_real_data",
        "scientific_training_ready": False,
        "training_ready_for_scientific_training": False,
        "training_not_ready_reason": "Only one temporal sequence is currently available; additional independent temporal observations/events are required for leakage-safe train/validation/test evaluation.",
        "source_timestamps": [pair["timestamp"].isoformat() + "Z" for pair in matched_pairs],
        "channels": channels,
        "channel_order": channels,
        "sequence_length": T,
        "temporal_step_minutes": config.get("sequencing", {}).get("temporal_step_minutes", 30),
        "patch_size": patch_cfg["size"],
        "stride": patch_cfg["stride"],
        "calibration_method": "LAB_STANDARD_QUADRATIC",
        "normalization_method": "development_only_standard_scaling",
        "normalization_statistics": final_norm,
        "rainfall_units": "mm/hr",
        "rainfall_fill_value": data_cfg["l2b_fill_value"],
        "l1b_fill_value": data_cfg["l1b_fill_value"],
        "input_shape": list(sequences.shape),
        "target_shape": list(targets.shape),
        "number_of_sequences": 1,
        "number_of_spatial_patches": N,
        "rainfall_class_thresholds": rain_cfg,
        "source_l1b_files": [Path(pair["l1b_path"]).name for pair in matched_pairs],
        "source_l2b_files": [Path(pair["l2b_path"]).name for pair in matched_pairs],
        "class_distribution": class_dist,
        "validity_statistics": {
            "intersection_valid_pixels": int(np.sum(intersection_mask)),
            "total_pixels": int(intersection_mask.size),
            "valid_pct": float(100.0 * np.sum(intersection_mask) / intersection_mask.size)
        },
        "created_at": datetime.utcnow().isoformat()
    }

    with open(out_dir / "metadata" / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    # Sequence manifest (per-patch rain stats)
    seq_manifest = []
    for p_idx, (r1, r2, c1, c2) in enumerate(patches):
        valid_t = targets[p_idx][masks[p_idx]]
        entry = {
            "patch_idx": p_idx,
            "row_start": r1, "row_end": r2,
            "col_start": c1, "col_end": c2,
            "label": int(labels[p_idx]),
            "rainfall_mean": float(np.nanmean(valid_t)) if valid_t.size > 0 else 0.0,
            "rainfall_max":  float(np.nanmax(valid_t))  if valid_t.size > 0 else 0.0,
        }
        seq_manifest.append(entry)

    with open(out_dir / "manifest" / "sequence_manifest.json", "w") as f:
        json.dump(seq_manifest, f, indent=2)

    return metadata
