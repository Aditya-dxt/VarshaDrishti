"""
Exports evaluation metrics for the existing development model checkpoint
on the held-out validation event (18 Aug 2026).

DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY
Only two independent weather events are available.
Results MUST NOT be interpreted as scientifically generalizable performance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.dataset import VarshaDataset
from src.data.splitter import split_by_temporal_event
from src.models.cnn3d import VarshaDrishti3DCNN
from src.training.validate import validate_one_epoch
from src.utils.checkpoint import load_checkpoint
from src.utils.device import get_device
from src.evaluation.report import generate_report

ARTIFACT_DIR = BASE_DIR / "data" / "processed" / "multitemporal_dev"
CHECKPOINT_PATH = BASE_DIR / "models" / "checkpoints" / "dev_poc_best.pth"
TRAIN_EVENT_ID = 0
VAL_EVENT_ID = 1

def _build_dataset(sequences: np.ndarray, labels: np.ndarray, samples: List[dict]) -> VarshaDataset:
    items = []
    for sample in samples:
        idx = int(sample["patch_idx"])
        items.append(
            {
                "sequence": torch.from_numpy(np.array(sequences[idx], dtype=np.float32)),
                "label": int(labels[idx]),
                "timestamp": sample.get("timestamps", [""])[-1],
                "metadata": {"temporal_sequence_id": sample["temporal_sequence_id"], "patch_idx": idx},
            }
        )
    return VarshaDataset(items)


def main() -> int:
    print("DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY")
    print("Results must NOT be interpreted as scientifically generalizable model performance.")
    print(f"Exporting evaluation metrics on the held-out event (temporal_sequence_id={VAL_EVENT_ID}, 18 Aug 2026)...")

    device = get_device("auto")

    # Load manifest
    manifest_path = ARTIFACT_DIR / "manifest" / "sequence_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Use existing split_by_temporal_event logic
    _, val_samples = split_by_temporal_event(
        manifest,
        train_event_ids=[TRAIN_EVENT_ID],
        val_event_ids=[VAL_EVENT_ID],
    )

    print(f"Loaded {len(val_samples)} validation samples from the held-out event.")

    # Load sequences and labels
    sequences = np.load(ARTIFACT_DIR / "data" / "sequences.npy", mmap_mode="r")
    labels = np.load(ARTIFACT_DIR / "data" / "labels.npy")

    # Build dataset and dataloader
    val_ds = _build_dataset(sequences, labels, val_samples)
    val_loader = DataLoader(val_ds, batch_size=4, shuffle=False, num_workers=0)

    # Initialize model
    in_channels = int(sequences.shape[1])
    num_classes = 4  # configured number of classes
    model = VarshaDrishti3DCNN(
        in_channels=in_channels,
        num_classes=num_classes,
        dropout=0.3,
    )

    # Load checkpoint
    if not CHECKPOINT_PATH.exists():
        raise RuntimeError(f"Checkpoint not found at {CHECKPOINT_PATH}. Run training first.")
    
    load_checkpoint(model, str(CHECKPOINT_PATH), optimizer=None, device=device)
    
    # We need a criterion to pass to validate_one_epoch
    criterion = nn.CrossEntropyLoss().to(device)

    # Run validation to get predictions and labels
    val_out = validate_one_epoch(model, val_loader, criterion, device)
    
    # Pass to evaluation script
    output_dir = BASE_DIR / "outputs" / "metrics"
    generate_report(val_out["labels"], val_out["predictions"], output_dir=str(output_dir))

    print(f"Export successful. Artifacts generated in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
