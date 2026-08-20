"""
VarshaDrishti — Build Multi-Temporal Manifest
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.manifest import build_file_inventory
from src.data.temporal_matcher import match_temporally

def build_manifest():
    config_path = BASE_DIR / "configs" / "preprocessing.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    seq_cfg = config.get("sequencing", {"tolerance_minutes": 0})
    
    l1b_dir = BASE_DIR / "data" / "raw" / "insat3dr_l1b"
    l2b_dir = BASE_DIR / "data" / "raw" / "insat3dr_l2b"
    
    print(f"Scanning L1B directory: {l1b_dir}")
    l1b_inv = build_file_inventory(l1b_dir, "L1B")
    print(f"Found {len(l1b_inv)} L1B files.")
    
    print(f"Scanning L2B directory: {l2b_dir}")
    l2b_inv = build_file_inventory(l2b_dir, "L2B")
    print(f"Found {len(l2b_inv)} L2B files.")
    
    matched, unmatched_l1b, unmatched_l2b = match_temporally(
        l1b_inv, l2b_inv, 
        tolerance_minutes=seq_cfg.get("tolerance_minutes", 0)
    )
    
    print(f"Matched {len(matched)} pairs.")
    
    # Serialize manifest
    manifest_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "matched_pairs": [],
        "unmatched_l1b": [],
        "unmatched_l2b": []
    }
    
    for m in matched:
        manifest_data["matched_pairs"].append({
            "timestamp": m["timestamp"].isoformat(),
            "l1b_path": str(Path(m["l1b_path"]).relative_to(BASE_DIR)).replace("\\", "/"),
            "l2b_path": str(Path(m["l2b_path"]).relative_to(BASE_DIR)).replace("\\", "/"),
            "time_diff_minutes": m["time_diff_minutes"]
        })
        
    for u in unmatched_l1b:
        manifest_data["unmatched_l1b"].append({
            "timestamp": u["timestamp"].isoformat(),
            "path": str(Path(u["full_path"]).relative_to(BASE_DIR)).replace("\\", "/")
        })
        
    for u in unmatched_l2b:
        manifest_data["unmatched_l2b"].append({
            "timestamp": u["timestamp"].isoformat(),
            "path": str(Path(u["full_path"]).relative_to(BASE_DIR)).replace("\\", "/")
        })
        
    out_dir = BASE_DIR / "data" / "processed" / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = out_dir / "temporal_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=4)
        
    print(f"Manifest saved to {manifest_path}")

if __name__ == "__main__":
    build_manifest()
