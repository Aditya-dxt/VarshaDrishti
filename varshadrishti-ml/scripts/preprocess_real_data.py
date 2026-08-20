"""
VarshaDrishti — Real Data Preprocessing (Dry Run)
"""

import sys
import yaml
import h5py
import numpy as np
from pathlib import Path
import argparse

# Add src to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.calibration import calibrate_channel
from src.data.geolocation import decode_geolocation
from src.data.rainfall import load_rainfall
from src.data.patching import generate_patches, classify_patch_rainfall

def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_pipeline(config: dict, dry_run: bool = True):
    print("=" * 70)
    print("VarshaDrishti — Preprocessing Dry Run")
    print("=" * 70)
    
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    calib_cfg = config["calibration"]
    
    l1b_path = BASE_DIR / data_cfg["l1b_path"]
    l2b_path = BASE_DIR / data_cfg["l2b_path"]
    
    if not l1b_path.exists() or not l2b_path.exists():
        print("ERROR: Real HDF5 files not found.")
        sys.exit(1)
        
    print(f"L1B: {l1b_path.name}")
    print(f"L2B: {l2b_path.name}")
    print()
    
    # Open files
    with h5py.File(l1b_path, "r") as f_l1b, h5py.File(l2b_path, "r") as f_l2b:
        
        # 1. Verify Spatial Dimensions and Decode Geolocation
        print("--- Geolocation ---")
        l1b_lat_ds = f_l1b["Latitude"]
        l1b_lon_ds = f_l1b["Longitude"]
        l2b_lat_ds = f_l2b["Latitude"]
        l2b_lon_ds = f_l2b["Longitude"]
        
        if l1b_lat_ds.shape != l2b_lat_ds.shape:
            print("ERROR: Spatial dimension mismatch between L1B 4km grid and L2B.")
            sys.exit(1)
            
        shape = l1b_lat_ds.shape
        print(f"Common Grid Shape: {shape}")
        
        lat, lon = decode_geolocation(
            l1b_lat_ds, l1b_lon_ds, 
            fill_value=data_cfg["geo_fill_value"],
            scale_factor=data_cfg["geo_scale_factor"]
        )
        
        valid_geo = ~np.isnan(lat) & ~np.isnan(lon)
        valid_geo_pct = 100.0 * np.sum(valid_geo) / valid_geo.size
        print(f"Valid Geolocation: {valid_geo_pct:.2f}% of pixels")
        print(f"Latitude Range:  {np.nanmin(lat):.2f} to {np.nanmax(lat):.2f} degrees")
        print(f"Longitude Range: {np.nanmin(lon):.2f} to {np.nanmax(lon):.2f} degrees")
        print()
        
        # 2. Process Input Channels
        print("--- Calibrated Input Channels ---")
        channel_data = {}
        use_gsics = (calib_cfg["method"] == "gsics")
        
        for ch in data_cfg["channels"]:
            ds = f_l1b[ch]
            rad, meta = calibrate_channel(ds, fill_value=data_cfg["l1b_fill_value"], use_gsics=use_gsics)
            channel_data[ch] = rad
            
            valid_ch = ~np.isnan(rad)
            valid_ch_pct = 100.0 * np.sum(valid_ch) / valid_ch.size
            
            print(f"{ch}:")
            print(f"  Method      : {meta['method']}")
            print(f"  Valid Px    : {valid_ch_pct:.2f}%")
            print(f"  Radiance Min: {np.nanmin(rad):.4f}")
            print(f"  Radiance Max: {np.nanmax(rad):.4f}")
            print(f"  Radiance Avg: {np.nanmean(rad):.4f}")
            
        print()
        
        # 3. Process Rainfall Target
        print("--- Rainfall Target ---")
        imc = load_rainfall(f_l2b["IMC"], fill_value=data_cfg["l2b_fill_value"])
        valid_rain = ~np.isnan(imc)
        valid_rain_pct = 100.0 * np.sum(valid_rain) / valid_rain.size
        print(f"Valid Rainfall Px: {valid_rain_pct:.2f}%")
        print(f"Rainfall Min     : {np.nanmin(imc):.4f}")
        print(f"Rainfall Max     : {np.nanmax(imc):.4f}")
        print()
        
        # 4. Global Valid Mask
        # A pixel is globally valid if it has valid geolocation, rainfall, and all input channels
        global_mask = valid_geo & valid_rain
        for ch in data_cfg["channels"]:
            global_mask &= ~np.isnan(channel_data[ch])
            
        global_valid_pct = 100.0 * np.sum(global_mask) / global_mask.size
        print("--- Global Data Mask ---")
        print(f"Globally valid pixels (all data present): {global_valid_pct:.2f}%")
        print()
        
        # 5. Patching
        print("--- Patch Generation (Dry Run) ---")
        print(f"Patch Size: {patch_cfg['size']}x{patch_cfg['size']}")
        print(f"Stride:     {patch_cfg['stride']}")
        print(f"Min Valid:  {patch_cfg['min_valid_pixels_pct']}%")
        
        patches = generate_patches(
            image_shape=shape,
            patch_size=patch_cfg["size"],
            stride=patch_cfg["stride"],
            valid_mask=global_mask,
            min_valid_pct=patch_cfg["min_valid_pixels_pct"]
        )
        
        print(f"Candidate Patches Generated: {len(patches)}")
        
        if not patches:
            print("No patches meet the criteria.")
            sys.exit(0)
            
        # Analyze rainfall distribution in patches
        no_rain_dominated_count = 0
        rainy_patch_count = 0
        heavy_rain_patch_count = 0
        
        for r1, r2, c1, c2 in patches:
            rain_patch = imc[r1:r2, c1:c2]
            counts = classify_patch_rainfall(rain_patch, rain_cfg)
            
            if counts["total_valid"] == 0:
                continue
                
            no_rain_pct = 100.0 * counts["no_rain"] / counts["total_valid"]
            
            if no_rain_pct > 95.0:
                no_rain_dominated_count += 1
            else:
                rainy_patch_count += 1
                
            # If the patch has any heavy or high_impact pixels, consider it a heavy rain patch
            if counts["heavy"] > 0 or counts["high_impact"] > 0:
                heavy_rain_patch_count += 1

        print(f"No-rain dominated patches : {no_rain_dominated_count} ({100*no_rain_dominated_count/len(patches):.1f}%)")
        print(f"Rainy patches (>5% rain)  : {rainy_patch_count} ({100*rainy_patch_count/len(patches):.1f}%)")
        print(f"Patches with Heavy+ rain  : {heavy_rain_patch_count} ({100*heavy_rain_patch_count/len(patches):.1f}%)")
        print()
        
        print("--- ML Data Split Warning ---")
        print("WARNING: Only one temporal observation is currently available;")
        print("additional timestamps are required for a meaningful ML train/validation/test split.")
        print()
        
        if dry_run:
            print("DRY RUN COMPLETE. No data was written to disk.")
        else:
            print("Data serialization not yet implemented.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run without writing files")
    args = parser.parse_args()
    
    config_path = Path(BASE_DIR) / "configs" / "preprocessing.yaml"
    config = load_config(str(config_path))
    
    # Capture print output to save to report
    import io
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        run_pipeline(config, dry_run=args.dry_run)
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
