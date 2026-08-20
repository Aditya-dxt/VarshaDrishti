"""
VarshaDrishti — Temporal Dataset Validation
"""

import sys
import yaml
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.manifest import build_file_inventory
from src.data.temporal_matcher import match_temporally
from src.data.sequence_builder import build_temporal_sequences

def run_validation():
    lines = []
    def P(s=""):
        lines.append(s)
        print(s)
        
    config_path = BASE_DIR / "configs" / "preprocessing.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    seq_cfg = config.get("sequencing", {})
    seq_len = seq_cfg.get("sequence_length", 6)
    step_min = seq_cfg.get("temporal_step_minutes", 30)
    tol_min = seq_cfg.get("tolerance_minutes", 0)
    
    l1b_dir = BASE_DIR / "data" / "raw" / "insat3dr_l1b"
    l2b_dir = BASE_DIR / "data" / "raw" / "insat3dr_l2b"
    
    l1b_inv = build_file_inventory(l1b_dir, "L1B")
    l2b_inv = build_file_inventory(l2b_dir, "L2B")
    
    matched, un_l1b, un_l2b = match_temporally(l1b_inv, l2b_inv, tolerance_minutes=tol_min)
    
    sequences = build_temporal_sequences(matched, sequence_length=seq_len, step_minutes=step_min)
    
    # Calculate longest continuous sequence
    longest = 0
    if matched:
        current_streak = 1
        for i in range(1, len(matched)):
            diff = (matched[i]["timestamp"] - matched[i-1]["timestamp"]).total_seconds() / 60.0
            if abs(diff - step_min) <= 0.01:
                current_streak += 1
                longest = max(longest, current_streak)
            else:
                current_streak = 1
                
        longest = max(longest, current_streak)
    
    P("==================================================")
    P("TEMPORAL DATASET VALIDATION")
    P("==================================================")
    P(f"L1B observations: {len(l1b_inv)}")
    P(f"L2B observations: {len(l2b_inv)}")
    P(f"Matched observations: {len(matched)}")
    P(f"Unmatched L1B files: {len(un_l1b)}")
    P(f"Unmatched L2B files: {len(un_l2b)}")
    
    if len(matched) > 1:
        gaps = 0
        for i in range(1, len(matched)):
            diff = (matched[i]["timestamp"] - matched[i-1]["timestamp"]).total_seconds() / 60.0
            if abs(diff - step_min) > 0.01:
                gaps += 1
        P(f"Timestamp gaps (broken continuity): {gaps}")
    else:
        P("Timestamp gaps (broken continuity): N/A")
        
    P(f"Longest continuous sequence (frames): {longest}")
    P(f"{seq_len}-frame sequences: {len(sequences)}")
    
    # Validation
    if len(sequences) > 0:
        P("Training ready: TRUE")
    else:
        P("Training ready: FALSE")
        P("\nINSUFFICIENT TEMPORAL DATA — TRAINING NOT READY")
        P("Waiting for more consecutive real data timestamps.")
        
    return lines

if __name__ == "__main__":
    report_lines = run_validation()
    report = "\n".join(report_lines)
    
    report_path = BASE_DIR / "reports" / "temporal_dataset_validation.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
