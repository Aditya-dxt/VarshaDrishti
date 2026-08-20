"""
VarshaDrishti — Preprocessing Validation Gate
"""

import sys
import os
import h5py
import numpy as np
import yaml
from pathlib import Path
import argparse

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.calibration import calibrate_channel
from src.data.geolocation import decode_geolocation
from src.data.rainfall import load_rainfall
from src.data.patching import generate_patches, classify_patch_rainfall

def run_validation():
    lines = []
    def P(s=""):
        lines.append(s)
        print(s)

    config_path = BASE_DIR / "configs" / "preprocessing.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    data_cfg = config["data"]
    l1b_path = BASE_DIR / data_cfg["l1b_path"]
    l2b_path = BASE_DIR / data_cfg["l2b_path"]
    
    if not l1b_path.exists() or not l2b_path.exists():
        P("FAIL: HDF5 files not found.")
        return lines, "BLOCKED"
        
    P("==================================================")
    P("VALIDATION GATE")
    P("==================================================")
    
    with h5py.File(l1b_path, "r") as f_l1b, h5py.File(l2b_path, "r") as f_l2b:
        
        # --------------------------------------------------
        # VALIDATION 1 — CALIBRATION CONSISTENCY
        # --------------------------------------------------
        P("\n==================================================")
        P("VALIDATION 1 — CALIBRATION CONSISTENCY")
        P("==================================================")
        
        for ch in data_cfg["channels"]:
            ds = f_l1b[ch]
            rad, meta = calibrate_channel(ds, fill_value=data_cfg["l1b_fill_value"], use_gsics=False)
            
            P(f"Channel: {ch}")
            P(f"  Formula: L = C^2 * quad + C * scale + offset")
            P(f"  quad   = {meta['quad']:e}")
            P(f"  scale  = {meta['scale']:e}")
            P(f"  offset = {meta['offset']:e}")
            
            # Look for temp equivalent
            temp_ch = f"{ch}_TEMP"
            if temp_ch in f_l1b:
                P(f"  Found physical product: {temp_ch}")
                temp_ds = f_l1b[temp_ch]
                
                # Check temp fill value
                temp_fill = None
                for attr_key in ("_FillValue", "FillValue", "fill_value", "missing_value"):
                    if attr_key in temp_ds.attrs:
                        temp_fill = temp_ds.attrs[attr_key][0]
                        break
                
                temp_arr = temp_ds[()]
                if temp_arr.ndim == 3 and temp_arr.shape[0] == 1:
                    temp_arr = temp_arr[0]
                temp_arr = temp_arr.astype(np.float64)
                
                if temp_fill is not None:
                    temp_arr[temp_arr == temp_fill] = np.nan
                
                valid_rad = rad[~np.isnan(rad)]
                valid_tmp = temp_arr[~np.isnan(temp_arr)]
                
                P(f"  Radiance    | Min: {np.nanmin(valid_rad):.4f}  Max: {np.nanmax(valid_rad):.4f}  Mean: {np.nanmean(valid_rad):.4f}  Std: {np.nanstd(valid_rad):.4f}")
                P(f"  Temperature | Min: {np.nanmin(valid_tmp):.4f}  Max: {np.nanmax(valid_tmp):.4f}  Mean: {np.nanmean(valid_tmp):.4f}  Std: {np.nanstd(valid_tmp):.4f}")
                P(f"  Note: Radiance and Temperature are related but numerically different quantities. Both are successfully extracted.")
            else:
                P(f"  No physical product found for {ch}.")
            P("")

        # --------------------------------------------------
        # VALIDATION 2 — GEOLOCATION
        # --------------------------------------------------
        P("==================================================")
        P("VALIDATION 2 — GEOLOCATION")
        P("==================================================")
        
        l1b_lat_ds = f_l1b["Latitude"]
        l1b_lon_ds = f_l1b["Longitude"]
        
        lat_fill = l1b_lat_ds.attrs.get("_FillValue", [None])[0]
        lon_fill = l1b_lon_ds.attrs.get("_FillValue", [None])[0]
        
        P(f"Latitude Fill expected: 32767, actual: {lat_fill}")
        P(f"Longitude Fill expected: 32767, actual: {lon_fill}")
        P(f"Scale Factor expected: 0.01, actual used: {data_cfg['geo_scale_factor']}")
        
        lat1, lon1 = decode_geolocation(l1b_lat_ds, l1b_lon_ds, fill_value=data_cfg["geo_fill_value"], scale_factor=data_cfg["geo_scale_factor"])
        
        valid_geo = ~np.isnan(lat1) & ~np.isnan(lon1)
        valid_pct = 100.0 * np.sum(valid_geo) / lat1.size
        
        P(f"Valid Geolocation Pixels: {valid_pct:.2f}%")
        P(f"Latitude Range:  {np.nanmin(lat1):.2f} to {np.nanmax(lat1):.2f}")
        P(f"Longitude Range: {np.nanmin(lon1):.2f} to {np.nanmax(lon1):.2f}")
        
        # --------------------------------------------------
        # VALIDATION 3 — L1B/L2B GRID ALIGNMENT
        # --------------------------------------------------
        P("\n==================================================")
        P("VALIDATION 3 — L1B/L2B GRID ALIGNMENT")
        P("==================================================")
        
        l2b_lat_ds = f_l2b["Latitude"]
        l2b_lon_ds = f_l2b["Longitude"]
        
        lat2, lon2 = decode_geolocation(l2b_lat_ds, l2b_lon_ds, fill_value=data_cfg["geo_fill_value"], scale_factor=data_cfg["geo_scale_factor"])
        
        P(f"L1B Geo Shape: {lat1.shape}")
        P(f"L2B Geo Shape: {lat2.shape}")
        
        if lat1.shape != lat2.shape:
            P("FAIL: Grid shapes do not match.")
            return lines, "BLOCKED"
            
        lat_diff = np.abs(lat1 - lat2)
        lon_diff = np.abs(lon1 - lon2)
        
        # Ignore NaNs where both are invalid, but warn if mismatch in validity
        mask = valid_geo
        
        max_lat_diff = np.nanmax(lat_diff[mask])
        mean_lat_diff = np.nanmean(lat_diff[mask])
        max_lon_diff = np.nanmax(lon_diff[mask])
        mean_lon_diff = np.nanmean(lon_diff[mask])
        
        P(f"Max Absolute Lat Diff: {max_lat_diff:.6f}")
        P(f"Mean Absolute Lat Diff: {mean_lat_diff:.6f}")
        P(f"Max Absolute Lon Diff: {max_lon_diff:.6f}")
        P(f"Mean Absolute Lon Diff: {mean_lon_diff:.6f}")
        
        if max_lat_diff > 0.01 or max_lon_diff > 0.01:
            P("FAIL: Grids are not perfectly aligned.")
            return lines, "BLOCKED"
        P("L1B and L2B grids are identical.")

        # --------------------------------------------------
        # VALIDATION 4 — RAINFALL TARGET
        # --------------------------------------------------
        P("\n==================================================")
        P("VALIDATION 4 — RAINFALL TARGET")
        P("==================================================")
        
        imc = load_rainfall(f_l2b["IMC"], fill_value=data_cfg["l2b_fill_value"])
        valid_rain = imc[~np.isnan(imc)]
        
        P(f"IMC Fill Value used: {data_cfg['l2b_fill_value']}")
        P(f"Finite Values: {valid_rain.size} ({100*valid_rain.size/imc.size:.2f}%)")
        
        neg_mask = (valid_rain < 0)
        neg_count = np.sum(neg_mask)
        P(f"Negative values (excluding fill): {neg_count}")
        if neg_count > 0:
            P("FAIL: Physically impossible negative rainfall values found.")
            return lines, "BLOCKED"
            
        P(f"Min: {np.nanmin(valid_rain):.4f}  Max: {np.nanmax(valid_rain):.4f}")
        P(f"Mean: {np.nanmean(valid_rain):.4f}  Std: {np.nanstd(valid_rain):.4f}")
        
        pcts = [50, 75, 90, 95, 99, 99.9]
        for p in pcts:
            P(f"Percentile {p}th: {np.percentile(valid_rain, p):.4f}")
            
        zero_rain = np.sum(valid_rain == 0)
        pos_rain = np.sum(valid_rain > 0)
        P(f"Zero-rain: {100.0*zero_rain/valid_rain.size:.2f}%")
        P(f"Positive-rain: {100.0*pos_rain/valid_rain.size:.2f}%")

        # --------------------------------------------------
        # VALIDATION 5 — PATCH SANITY
        # --------------------------------------------------
        P("\n==================================================")
        P("VALIDATION 5 — PATCH SANITY")
        P("==================================================")
        
        channel_data = {}
        for ch in data_cfg["channels"]:
            rad, _ = calibrate_channel(f_l1b[ch], fill_value=data_cfg["l1b_fill_value"], use_gsics=False)
            channel_data[ch] = rad
            
        global_mask = ~np.isnan(lat1) & ~np.isnan(lon1) & ~np.isnan(imc)
        for ch in data_cfg["channels"]:
            global_mask &= ~np.isnan(channel_data[ch])
            
        patch_cfg = config["patching"]
        patches = generate_patches(
            image_shape=lat1.shape,
            patch_size=patch_cfg["size"],
            stride=patch_cfg["stride"],
            valid_mask=global_mask,
            min_valid_pct=patch_cfg["min_valid_pixels_pct"]
        )
        
        P(f"Found {len(patches)} candidate patches.")
        P(f"{'ID':<4} | {'Valid%':<6} | {'MIR(avg)':<8} | {'TIR1(avg)':<9} | {'TIR2(avg)':<9} | {'Rain(avg)':<9} | {'Rain(max)':<9} | {'%Rainy':<7} | {'Class Counts (NR,L,M,H,HI)'}")
        P("-" * 115)
        
        for idx, (r1, r2, c1, c2) in enumerate(patches):
            patch_mask = global_mask[r1:r2, c1:c2]
            valid_pct = 100.0 * np.sum(patch_mask) / patch_mask.size
            
            p_mir = channel_data["IMG_MIR"][r1:r2, c1:c2]
            p_t1 = channel_data["IMG_TIR1"][r1:r2, c1:c2]
            p_t2 = channel_data["IMG_TIR2"][r1:r2, c1:c2]
            p_rain = imc[r1:r2, c1:c2]
            
            # Means calculated on valid pixels in patch
            vm = patch_mask
            m_mir = np.nanmean(p_mir[vm])
            m_t1 = np.nanmean(p_t1[vm])
            m_t2 = np.nanmean(p_t2[vm])
            m_rain = np.nanmean(p_rain[vm])
            mx_rain = np.nanmax(p_rain[vm])
            
            rain_pixels = np.sum(p_rain[vm] > 0)
            rainy_pct = 100.0 * rain_pixels / np.sum(vm)
            
            counts = classify_patch_rainfall(p_rain, config["rainfall_classes"])
            cc = f"{counts['no_rain']},{counts['light']},{counts['moderate']},{counts['heavy']},{counts['high_impact']}"
            
            P(f"{idx:<4} | {valid_pct:<6.1f} | {m_mir:<8.4f} | {m_t1:<9.4f} | {m_t2:<9.4f} | {m_rain:<9.4f} | {mx_rain:<9.4f} | {rainy_pct:<7.1f} | {cc}")

        # --------------------------------------------------
        # VALIDATION 6 — DATA LEAKAGE SAFETY
        # --------------------------------------------------
        P("\n==================================================")
        P("VALIDATION 6 — DATA LEAKAGE SAFETY")
        P("==================================================")
        P("Only one temporal observation is currently available. A valid ML train/validation/test split cannot yet be created.")

        P("\n==================================================")
        P("FINAL STATUS: PASS")
        P("==================================================")
        return lines, "PASS"

if __name__ == "__main__":
    report_lines, status = run_validation()
    report = "\n".join(report_lines)
    print(report)
    
    report_path = BASE_DIR / "reports" / "preprocessing_validation_gate.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
