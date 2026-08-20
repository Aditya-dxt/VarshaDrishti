"""
VarshaDrishti — Dev Artifact Integrity & DataLoader Test
"""

import sys
import os
import json
import numpy as np
import torch
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from torch.utils.data import Dataset, DataLoader
from src.data.dataset import VarshaDataset

def run_integrity_test():
    out_dir = BASE_DIR / "data" / "processed" / "dev_single_timestamp"
    
    with open(out_dir / "metadata" / "metadata.json", "r") as f:
        meta = json.load(f)
        
    print("--- 1. Metadata Verification ---")
    print(f"Artifact Type: {meta['artifact_type']}")
    print(f"Training Ready: {meta['scientific_training_ready']}")
    print(f"Patches Expected: {meta['number_of_patches']}")
    print(meta["WARNING"])
    
    # Reload files
    dev_inputs = np.load(out_dir / "data" / "dev_inputs.npy")
    dev_targets = np.load(out_dir / "data" / "dev_targets.npy")
    dev_labels = np.load(out_dir / "data" / "dev_labels.npy")
    dev_masks = np.load(out_dir / "masks" / "dev_masks.npy")
    
    print("\n--- 2. Shape Verification ---")
    N = meta['number_of_patches']
    C = len(meta['channels'])
    H = W = meta['patch_size']
    
    assert dev_inputs.shape == (N, C, H, W), f"Inputs shape mismatch: {dev_inputs.shape}"
    assert dev_targets.shape == (N, H, W), f"Targets shape mismatch: {dev_targets.shape}"
    assert dev_masks.shape == (N, H, W), f"Masks shape mismatch: {dev_masks.shape}"
    assert dev_labels.shape == (N,), f"Labels shape mismatch: {dev_labels.shape}"
    print("Shapes verified.")
    
    print("\n--- 3. Dtype and Integrity Verification ---")
    assert dev_inputs.dtype == np.float32, "dev_inputs should be float32"
    assert dev_targets.dtype == np.float32, "dev_targets should be float32"
    assert dev_masks.dtype == bool, "dev_masks should be bool"
    
    assert not np.isnan(dev_inputs).any(), "Found NaN in dev_inputs"
    assert not np.isinf(dev_inputs).any(), "Found Inf in dev_inputs"
    
    # Targets may have NaNs where mask is False, but valid pixels should be finite
    valid_targets = dev_targets[dev_masks]
    assert not np.isnan(valid_targets).any(), "Found NaN in valid targets"
    assert not np.isinf(valid_targets).any(), "Found Inf in valid targets"
    print("Dtypes and finite values verified.")
    
    print("\n--- 4. DataLoader Integration Test ---")
    # Convert this flat patch array into a format VarshaDataset expects.
    # VarshaDataset expects dictionaries with "sequence" and "label".
    # For spatial testing, we can artificially add the time dimension (T=1) 
    # to satisfy the CNN's [B, C, T, H, W] requirement without pretending it's real temporal data.
    
    items = []
    for i in range(N):
        # input shape is [C, H, W], expand to [C, T=1, H, W]
        seq = torch.from_numpy(dev_inputs[i]).unsqueeze(1) 
        items.append({
            "sequence": seq,
            "label": int(dev_labels[i]),
            "timestamp": meta["observation_time_utc"]
        })
        
    dataset = VarshaDataset(items)
    print(f"VarshaDataset initialized. Length: {len(dataset)}")
    
    loader = DataLoader(dataset, batch_size=4, shuffle=False)
    batch = next(iter(loader))
    
    seq_batch = batch["sequence"]
    lbl_batch = batch["label"]
    
    print(f"Batch Sequence Shape: {seq_batch.shape} (Expected: [B, C, T, H, W])")
    print(f"Batch Label Shape: {lbl_batch.shape}")
    
    assert seq_batch.shape == (4, C, 1, H, W), "DataLoader sequence shape mismatch"
    assert lbl_batch.shape == (4,), "DataLoader label shape mismatch"
    
    print("\nDataLoader successfully served real-data patches.")
    print("Temporal integration (T > 1) remains pending future data.")

if __name__ == "__main__":
    import io
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        run_integrity_test()
        status = "ALL TESTS PASSED"
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        status = "FAILED"
    finally:
        sys.stdout = old_stdout
        
    report_content = new_stdout.getvalue()
    print(report_content)
    
    report_path = BASE_DIR / "reports" / "dev_artifact_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("DEVELOPMENT ARTIFACT REPORT\n")
        f.write("==================================================\n")
        f.write(f"Status: {status}\n\n")
        f.write(report_content)
