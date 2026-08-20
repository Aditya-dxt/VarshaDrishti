"""
VarshaDrishti — Materialize Single-Timestamp Development Artifact
"""

import sys
import os
import json
import h5py
import numpy as np
import yaml
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.calibration import calibrate_channel
from src.data.geolocation import decode_geolocation
from src.data.rainfall import load_rainfall
from src.data.patching import generate_patches, classify_patch_rainfall

def get_class_id(rain_val: float, thresholds: dict) -> int:
    """Classifies a single rainfall value into 0=no_rain, 1=light/moderate, 2=heavy, 3=high_impact."""
    if rain_val <= thresholds["no_rain"]:
        return 0
    elif rain_val <= thresholds["moderate"]:
        return 1
    elif rain_val <= thresholds["heavy"]:
        return 2
    else:
        return 3

def build_dev_artifact():
    config_path = BASE_DIR / "configs" / "preprocessing.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    data_cfg = config["data"]
    patch_cfg = config["patching"]
    rain_cfg = config["rainfall_classes"]
    
    l1b_path = BASE_DIR / data_cfg["l1b_path"]
    l2b_path = BASE_DIR / data_cfg["l2b_path"]
    
    out_dir = BASE_DIR / "data" / "processed" / "dev_single_timestamp"
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata").mkdir(parents=True, exist_ok=True)
    (out_dir / "masks").mkdir(parents=True, exist_ok=True)
    
    with h5py.File(l1b_path, "r") as f_l1b, h5py.File(l2b_path, "r") as f_l2b:
        # Load Geolocation
        lat, lon = decode_geolocation(
            f_l1b["Latitude"], f_l1b["Longitude"],
            fill_value=data_cfg["geo_fill_value"],
            scale_factor=data_cfg["geo_scale_factor"]
        )
        
        valid_geo = ~np.isnan(lat) & ~np.isnan(lon)
        
        # Load Rainfall
        imc = load_rainfall(f_l2b["IMC"], fill_value=data_cfg["l2b_fill_value"])
        valid_rain = ~np.isnan(imc)
        
        # Load Channels
        channels = data_cfg["channels"]
        channel_data = {}
        for ch in channels:
            rad, meta = calibrate_channel(f_l1b[ch], fill_value=data_cfg["l1b_fill_value"])
            channel_data[ch] = rad
            
        global_mask = valid_geo & valid_rain
        for ch in channels:
            global_mask &= ~np.isnan(channel_data[ch])
            
        patches = generate_patches(
            image_shape=lat.shape,
            patch_size=patch_cfg["size"],
            stride=patch_cfg["stride"],
            valid_mask=global_mask,
            min_valid_pct=patch_cfg["min_valid_pixels_pct"]
        )
        
        N = len(patches)
        C = len(channels)
        H = W = patch_cfg["size"]
        
        dev_inputs = np.zeros((N, C, H, W), dtype=np.float32)
        dev_targets = np.zeros((N, H, W), dtype=np.float32)
        dev_labels = np.zeros((N,), dtype=np.int64)
        dev_masks = np.zeros((N, H, W), dtype=bool)
        
        # Calculate DEV-ONLY normalization stats
        norm_stats = {}
        for i, ch in enumerate(channels):
            rad = channel_data[ch]
            # Use only globally valid pixels for stats
            valid_pixels = rad[global_mask]
            norm_stats[ch] = {
                "mean": float(np.nanmean(valid_pixels)),
                "std": float(np.nanstd(valid_pixels))
            }
        
        for idx, (r1, r2, c1, c2) in enumerate(patches):
            for i, ch in enumerate(channels):
                p_rad = channel_data[ch][r1:r2, c1:c2]
                # Normalize using dev stats
                m = norm_stats[ch]["mean"]
                s = norm_stats[ch]["std"]
                p_norm = (p_rad - m) / (s + 1e-8)
                dev_inputs[idx, i] = p_norm
                
            dev_targets[idx] = imc[r1:r2, c1:c2]
            dev_masks[idx] = global_mask[r1:r2, c1:c2]
            
            # Label based on maximum rainfall in patch for sequence testing (if needed)
            valid_target_pixels = dev_targets[idx][dev_masks[idx]]
            max_rain = float(np.nanmax(valid_target_pixels)) if valid_target_pixels.size > 0 else 0.0
            dev_labels[idx] = get_class_id(max_rain, rain_cfg)
            
        # Write to disk
        np.save(out_dir / "data" / "dev_inputs.npy", dev_inputs)
        np.save(out_dir / "data" / "dev_targets.npy", dev_targets)
        np.save(out_dir / "data" / "dev_labels.npy", dev_labels)
        np.save(out_dir / "masks" / "dev_masks.npy", dev_masks)
        
        # Metadata
        metadata = {
            "WARNING": "THIS IS A SINGLE-TIMESTAMP DEVELOPMENT ARTIFACT. IT MUST NOT BE USED FOR SCIENTIFIC MODEL TRAINING, VALIDATION, TESTING, OR PERFORMANCE CLAIMS.",
            "artifact_type": "development_only_single_timestamp",
            "scientific_training_ready": False,
            "source_l1b_filename": l1b_path.name,
            "source_l2b_filename": l2b_path.name,
            "observation_time_utc": "2026-08-17T23:45:00Z",
            "channels": channels,
            "channel_order": channels,
            "input_shape": list(dev_inputs.shape),
            "target_shape": list(dev_targets.shape),
            "patch_size": patch_cfg["size"],
            "stride": patch_cfg["stride"],
            "minimum_valid_pixels": patch_cfg["min_valid_pixels_pct"],
            "calibration_method": "LAB_STANDARD_QUADRATIC",
            "normalization_method": "development_only_standard_scaling",
            "normalization_statistics": norm_stats,
            "rainfall_units": "mm/hr",
            "rainfall_fill_value": data_cfg["l2b_fill_value"],
            "l1b_fill_value": data_cfg["l1b_fill_value"],
            "number_of_patches": N,
            "rainfall_class_thresholds": rain_cfg,
            "geolocation_information": "Decoded with scale_factor 0.01",
            "validation_report_path": "reports/preprocessing_validation_gate.txt",
            "created_at": datetime.utcnow().isoformat()
        }
        
        with open(out_dir / "metadata" / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Artifact successfully created at {out_dir}")
        print(f"Number of patches: {N}")

if __name__ == "__main__":
    build_dev_artifact()
