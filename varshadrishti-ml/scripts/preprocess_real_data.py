"""
VarshaDrishti — Real Data Preprocessing

Modes:
  --dry-run                         Single-timestamp dry run (original behaviour)
  --multitemporal --manifest <path> Multi-temporal mode using temporal manifest
  --multitemporal --manifest <path> --dry-run   Multi-temporal dry run only
"""

import sys
import io
import json
import yaml
import h5py
import numpy as np
from pathlib import Path
from datetime import datetime
import argparse

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.calibration import calibrate_channel
from src.data.geolocation import decode_geolocation
from src.data.rainfall import load_rainfall
from src.data.patching import generate_patches, classify_patch_rainfall
from src.data.multitemporal_processor import dry_run_multitemporal, materialize_multitemporal


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_manifest(manifest_path: str) -> list:
    """Loads matched pairs from the temporal manifest JSON."""
    with open(manifest_path, "r") as f:
        raw = json.load(f)

    pairs = []
    for entry in raw["matched_pairs"]:
        pairs.append({
            "timestamp": datetime.fromisoformat(entry["timestamp"]),
            "l1b_path": str(BASE_DIR / entry["l1b_path"]),
            "l2b_path": str(BASE_DIR / entry["l2b_path"]),
            "l1b_filename": Path(entry["l1b_path"]).name,
            "l2b_filename": Path(entry["l2b_path"]).name,
            "time_diff_minutes": entry["time_diff_minutes"]
        })

    return sorted(pairs, key=lambda x: x["timestamp"])


# ──────────────────────────────────────────────────────────
#  ORIGINAL SINGLE-TIMESTAMP PIPELINE (preserved unchanged)
# ──────────────────────────────────────────────────────────

def run_single_timestamp_pipeline(config: dict, dry_run: bool = True):
    print("=" * 70)
    print("VarshaDrishti -- Preprocessing Dry Run (Single Timestamp)")
    print("=" * 70)

    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg  = config["rainfall_classes"]
    calib_cfg = config["calibration"]

    l1b_path = BASE_DIR / data_cfg["l1b_path"]
    l2b_path = BASE_DIR / data_cfg["l2b_path"]

    if not l1b_path.exists() or not l2b_path.exists():
        print("ERROR: Real HDF5 files not found.")
        sys.exit(1)

    print(f"L1B: {l1b_path.name}")
    print(f"L2B: {l2b_path.name}")
    print()

    with h5py.File(l1b_path, "r") as f_l1b, h5py.File(l2b_path, "r") as f_l2b:

        print("--- Geolocation ---")
        l1b_lat_ds = f_l1b["Latitude"]
        l1b_lon_ds = f_l1b["Longitude"]
        l2b_lat_ds = f_l2b["Latitude"]

        if l1b_lat_ds.shape != l2b_lat_ds.shape:
            print("ERROR: Spatial dimension mismatch.")
            sys.exit(1)

        shape = l1b_lat_ds.shape
        print(f"Common Grid Shape: {shape}")

        lat, lon = decode_geolocation(
            l1b_lat_ds, f_l1b["Longitude"],
            fill_value=data_cfg["geo_fill_value"],
            scale_factor=data_cfg["geo_scale_factor"]
        )

        valid_geo = ~np.isnan(lat) & ~np.isnan(lon)
        print(f"Valid Geolocation: {100.0*np.sum(valid_geo)/valid_geo.size:.2f}% of pixels")
        print(f"Latitude Range:  {np.nanmin(lat):.2f} to {np.nanmax(lat):.2f} degrees")
        print(f"Longitude Range: {np.nanmin(lon):.2f} to {np.nanmax(lon):.2f} degrees")
        print()

        print("--- Calibrated Input Channels ---")
        channel_data = {}
        use_gsics = (calib_cfg["method"] == "gsics")

        for ch in data_cfg["channels"]:
            ds = f_l1b[ch]
            rad, meta = calibrate_channel(ds, fill_value=data_cfg["l1b_fill_value"], use_gsics=use_gsics)
            channel_data[ch] = rad
            valid_ch_pct = 100.0 * np.sum(~np.isnan(rad)) / rad.size
            print(f"{ch}:  Valid={valid_ch_pct:.2f}%  Min={np.nanmin(rad):.4f}  Max={np.nanmax(rad):.4f}")

        print()
        print("--- Rainfall Target ---")
        imc = load_rainfall(f_l2b["IMC"], fill_value=data_cfg["l2b_fill_value"])
        print(f"Valid Rainfall Px: {100.0*np.sum(~np.isnan(imc))/imc.size:.2f}%")
        print(f"Rainfall Range:  {np.nanmin(imc):.4f} to {np.nanmax(imc):.4f} mm/hr")
        print()

        global_mask = valid_geo & ~np.isnan(imc)
        for ch in data_cfg["channels"]:
            global_mask &= ~np.isnan(channel_data[ch])

        print("--- Global Data Mask ---")
        print(f"Globally valid: {100.0*np.sum(global_mask)/global_mask.size:.2f}%")
        print()

        patches = generate_patches(
            image_shape=shape,
            patch_size=patch_cfg["size"],
            stride=patch_cfg["stride"],
            valid_mask=global_mask,
            min_valid_pct=patch_cfg["min_valid_pixels_pct"]
        )

        print("--- Patch Generation ---")
        print(f"Patch Size: {patch_cfg['size']}x{patch_cfg['size']}")
        print(f"Candidate Patches: {len(patches)}")

        no_rain = rainy = heavy = 0
        for r1, r2, c1, c2 in patches:
            counts = classify_patch_rainfall(imc[r1:r2, c1:c2], rain_cfg)
            if counts["total_valid"] == 0:
                continue
            nr_pct = 100.0 * counts["no_rain"] / counts["total_valid"]
            if nr_pct > 95.0:
                no_rain += 1
            else:
                rainy += 1
            if counts["heavy"] > 0 or counts["high_impact"] > 0:
                heavy += 1

        if patches:
            print(f"No-rain dominated: {no_rain} ({100*no_rain/len(patches):.1f}%)")
            print(f"Rainy patches    : {rainy} ({100*rainy/len(patches):.1f}%)")
            print(f"Heavy+ patches   : {heavy} ({100*heavy/len(patches):.1f}%)")

        print()
        print("WARNING: Only one temporal observation is currently available;")
        print("additional timestamps are required for a meaningful ML train/validation/test split.")
        print()

        if dry_run:
            print("DRY RUN COMPLETE. No data was written to disk.")
        else:
            print("Data serialization not yet implemented for single-timestamp mode.")


# ──────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VarshaDrishti Real-Data Preprocessing")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Report statistics without writing data.")
    parser.add_argument("--multitemporal", action="store_true", default=False,
                        help="Use multi-temporal mode (requires --manifest).")
    parser.add_argument("--manifest", type=str, default=None,
                        help="Path to temporal_manifest.json (required for --multitemporal).")
    args = parser.parse_args()

    config_path = BASE_DIR / "configs" / "preprocessing.yaml"
    config = load_config(str(config_path))

    # ── Multi-temporal mode ──
    if args.multitemporal:
        if not args.manifest:
            print("ERROR: --multitemporal requires --manifest <path>")
            sys.exit(1)

        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            # Try relative to CWD first, then BASE_DIR
            if manifest_path.exists():
                pass
            elif (BASE_DIR / args.manifest).exists():
                manifest_path = BASE_DIR / args.manifest
            else:
                manifest_path = Path(args.manifest)  # let the exists() check fail naturally

        if not manifest_path.exists():
            print(f"ERROR: Manifest not found: {manifest_path}")
            sys.exit(1)

        matched_pairs = load_manifest(str(manifest_path))
        print(f"Loaded {len(matched_pairs)} matched pairs from manifest.")

        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            if args.dry_run:
                dry_run_multitemporal(matched_pairs, config)
                report_filename = "multitemporal_dry_run.txt"
            else:
                out_dir = BASE_DIR / "data" / "processed" / "multitemporal_dev"
                meta = materialize_multitemporal(matched_pairs, config, out_dir)
                print(f"\nArtifact written to: {out_dir}")
                print(f"Sequences shape   : {meta['input_shape']}")
                print(f"Patches           : {meta['number_of_spatial_patches']}")
                report_filename = "multitemporal_preprocessing_report.txt"
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            report_filename = "multitemporal_error.txt"
        finally:
            sys.stdout = old_stdout

        report = new_stdout.getvalue()
        print(report)
        report_path = BASE_DIR / "reports" / report_filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

    # ── Original single-timestamp mode ──
    else:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            run_single_timestamp_pipeline(config, dry_run=(args.dry_run or True))
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout

        report = new_stdout.getvalue()
        print(report)
        report_path = BASE_DIR / "reports" / "preprocessing_dry_run.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
