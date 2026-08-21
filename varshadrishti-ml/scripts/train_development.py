"""
Development / proof-of-concept training run.

DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY

Only two independent weather events are available.
17 Aug 2026 → train. 18 Aug 2026 → held-out validation/test.
Validation and test are the SAME event in this POC.
Results MUST NOT be interpreted as scientifically generalizable performance.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.dataset import VarshaDataset
from src.data.splitter import split_by_temporal_event
from src.evaluation.confusion_matrix import compute_confusion_matrix
from src.evaluation.metrics import CLASS_NAMES, NUM_CLASSES, calculate_metrics
from src.models.cnn3d import VarshaDrishti3DCNN
from src.training.train import Trainer
from src.training.validate import validate_one_epoch
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.device import get_device
from src.utils.logger import setup_logger
from src.utils.seed import set_seed

ARTIFACT_DIR = BASE_DIR / "data" / "processed" / "multitemporal_dev"
REPORT_PATH = BASE_DIR / "reports" / "development_training_report.txt"
CHECKPOINT_PATH = BASE_DIR / "models" / "checkpoints" / "dev_poc_best.pth"
TRAIN_EVENT_ID = 0
VAL_EVENT_ID = 1
MAX_EPOCHS = 3
EARLY_STOPPING_PATIENCE = 2


def inverse_frequency_weights(labels: List[int], num_classes: int = NUM_CLASSES) -> np.ndarray:
    """Train-event only. Absent classes get weight 0 (not an inflated weight)."""
    counts = np.bincount(np.asarray(labels, dtype=np.int64), minlength=num_classes).astype(np.float64)
    n = float(len(labels))
    weights = np.zeros(num_classes, dtype=np.float64)
    for cls in range(num_classes):
        if counts[cls] > 0:
            weights[cls] = n / (num_classes * counts[cls])
    return weights


def _assert_no_event_leakage(train_samples: List[dict], val_samples: List[dict]) -> None:
    train_ids = {s["temporal_sequence_id"] for s in train_samples}
    val_ids = {s["temporal_sequence_id"] for s in val_samples}
    leaked = train_ids & val_ids
    if leaked:
        raise RuntimeError(f"Event leakage: temporal_sequence_id {sorted(leaked)} in both splits.")
    train_idx = {s["patch_idx"] for s in train_samples}
    val_idx = {s["patch_idx"] for s in val_samples}
    if train_idx & val_idx:
        raise RuntimeError("Patch index leakage between train and validation.")


def _class_dist(labels: List[int]) -> Dict[int, int]:
    return {int(k): int(v) for k, v in sorted(Counter(labels).items())}


def _build_dataset(indices: List[int], sequences: np.ndarray, labels: np.ndarray, samples: List[dict]) -> VarshaDataset:
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


def format_confusion_matrix(cm: dict) -> str:
    names = cm["class_names"]
    matrix = cm["matrix"]
    header = "pred->          " + "  ".join(f"{n:>12}" for n in names)
    lines = [header]
    for name, row in zip(names, matrix):
        lines.append("true " + f"{name:<10}" + "  ".join(f"{int(v):12d}" for v in row))
    return "\n".join(lines)


def write_report(payload: dict, path: Path = REPORT_PATH) -> None:
    metrics = payload["val_metrics"]
    cm = payload["confusion_matrix"]
    lines = [
        "==================================================",
        "DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY",
        "==================================================",
        "",
        "Only two independent weather events were available.",
        "17 Aug 2026 was used for training.",
        "18 Aug 2026 was used as the held-out validation/test event.",
        "Validation and test are the same held-out event because only two independent events are currently available.",
        "The results must NOT be interpreted as scientifically generalizable model performance.",
        "",
        f"Device: {payload['device']}",
        f"Seed: {payload['seed']}",
        f"Model: VarshaDrishti3DCNN  in_channels={payload['in_channels']}  num_classes={payload['num_classes']}",
        f"Optimizer: AdamW  lr={payload['learning_rate']}  weight_decay={payload['weight_decay']}",
        f"Batch size: {payload['batch_size']}",
        f"Max epochs: {payload['max_epochs']}",
        f"Early stopping patience: {payload['patience']}",
        f"Gradient clipping: {payload['gradient_clipping']}",
        f"Loss: CrossEntropyLoss with inverse-frequency class weights from TRAIN event only",
        "",
        "Split",
        "-----",
        f"Train event: {payload['train_event']}  samples={payload['n_train']}",
        f"Val/test event: {payload['val_event']}  samples={payload['n_val']}",
        f"Train temporal_sequence_id set: {payload['train_event_ids']}",
        f"Val temporal_sequence_id set: {payload['val_event_ids']}",
        f"Event id overlap: {payload['event_id_overlap']}",
        "",
        "Class distribution (train): " + str(payload["train_class_distribution"]),
        "Class distribution (val):   " + str(payload["val_class_distribution"]),
        "Class weights (train-only): " + str(payload["class_weights"]),
        "Class names: " + str(list(CLASS_NAMES)),
        "Label rule (unchanged): patch-level max rainfall at final timestamp;",
        "  0: max<=0, 1: 0<max<=5, 2: 5<max<=20, 3: max>20 mm/hr.",
        "  preprocessing.yaml keys 'light' (1.0) and 'high_impact' (50.0) are not class cuts.",
        "",
        "Epoch-wise losses",
        "-----------------",
    ]
    for row in payload["history"]:
        lines.append(
            f"  epoch {row['epoch']}: train_loss={row['train_loss']:.6f}  "
            f"val_loss={row['val_loss']:.6f}  train_acc={row['train_accuracy']:.4f}  "
            f"val_acc={row['val_accuracy']:.4f}"
        )
    lines.extend(
        [
            "",
            f"Best epoch (lowest val_loss): {payload['best_epoch']}",
            f"Best val_loss: {payload['best_val_loss']:.6f}",
            f"Checkpoint path: {payload['checkpoint_path']}",
            "",
            "Held-out event metrics (18 Aug 2026) — NOT generalizable performance",
            "-------------------------------------------------------------------",
            f"accuracy:    {metrics['accuracy']:.6f}",
            f"macro_f1:    {metrics['macro_f1']:.6f}",
            f"weighted_f1: {metrics['weighted_f1']:.6f}",
            "",
            "Per-class precision / recall / F1",
        ]
    )
    for name in CLASS_NAMES:
        stats = metrics["classes"][name]
        lines.append(
            f"  {name:12s}  P={stats['precision']:.6f}  R={stats['recall']:.6f}  F1={stats['f1']:.6f}"
        )
    lines.extend(
        [
            "",
            "Confusion matrix (rows = true, columns = predicted)",
            format_confusion_matrix(cm),
            "",
            "DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY",
            "Only two independent weather events were available.",
            "Results must NOT be interpreted as scientifically generalizable model performance.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    logger = setup_logger("trainer", log_dir=str(BASE_DIR / "outputs" / "logs"))
    print("DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY")
    print("Results must NOT be interpreted as scientifically generalizable model performance.")

    config = load_config(str(BASE_DIR / "configs" / "config.yaml"))
    training_cfg = config.setdefault("training", {})
    training_cfg["epochs"] = MAX_EPOCHS
    training_cfg["batch_size"] = 4
    training_cfg["learning_rate"] = 0.001
    training_cfg["weight_decay"] = 0.0001
    training_cfg["seed"] = 42
    training_cfg.setdefault("early_stopping", {})["enabled"] = True
    training_cfg["early_stopping"]["patience"] = EARLY_STOPPING_PATIENCE
    training_cfg.setdefault("checkpoint", {})["enabled"] = True
    training_cfg.setdefault("gradient_clipping", {})["enabled"] = False

    set_seed(int(training_cfg["seed"]))
    device = get_device(config.get("runtime", {}).get("device", "auto"))

    with open(ARTIFACT_DIR / "manifest" / "sequence_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    train_samples, val_samples = split_by_temporal_event(
        manifest,
        train_event_ids=[TRAIN_EVENT_ID],
        val_event_ids=[VAL_EVENT_ID],
    )
    _assert_no_event_leakage(train_samples, val_samples)

    train_ids = {s["temporal_sequence_id"] for s in train_samples}
    val_ids = {s["temporal_sequence_id"] for s in val_samples}
    shared_ids = train_ids & val_ids
    print("TRAIN event IDs: {}".format(sorted(train_ids)))
    print("VALIDATION/TEST event IDs: {}".format(sorted(val_ids)))
    print("Shared event IDs: {}".format(sorted(shared_ids)))
    print("TRAIN EVENT: 17 Aug 2026 -> {} samples".format(len(train_samples)))
    print("VALIDATION/TEST EVENT: 18 Aug 2026 -> {} samples".format(len(val_samples)))
    print("NO validation/test event samples will be used during training.")
    if shared_ids:
        raise RuntimeError("Refusing to train: shared temporal_sequence_ids={}".format(sorted(shared_ids)))
    sys.stdout.flush()

    sequences = np.load(ARTIFACT_DIR / "data" / "sequences.npy", mmap_mode="r")
    labels = np.load(ARTIFACT_DIR / "data" / "labels.npy")

    train_labels = [int(labels[int(s["patch_idx"])]) for s in train_samples]
    val_labels = [int(labels[int(s["patch_idx"])]) for s in val_samples]
    class_weights = inverse_frequency_weights(train_labels, NUM_CLASSES)
    print("Train class distribution: {}".format(_class_dist(train_labels)))
    print("Val class distribution:   {}".format(_class_dist(val_labels)))
    print("Class weights (train event only): {}".format(
        {CLASS_NAMES[i]: float(class_weights[i]) for i in range(NUM_CLASSES)}
    ))
    sys.stdout.flush()

    train_ds = _build_dataset([], sequences, labels, train_samples)
    val_ds = _build_dataset([], sequences, labels, val_samples)
    batch_size = int(training_cfg["batch_size"])
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    in_channels = int(sequences.shape[1])
    num_classes = int(config.get("model", {}).get("num_classes", 4))
    model = VarshaDrishti3DCNN(
        in_channels=in_channels,
        num_classes=num_classes,
        dropout=float(config.get("model", {}).get("dropout", 0.3)),
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training_cfg["learning_rate"]),
        weight_decay=float(training_cfg["weight_decay"]),
    )
    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32, device=device)
    )

    checkpoint_path = str(CHECKPOINT_PATH)
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        config=config,
        checkpoint_path=checkpoint_path,
    )
    history = trainer.fit(train_loader, val_loader)

    best_row = min(history, key=lambda r: r["val_loss"])
    load_checkpoint(model, checkpoint_path, optimizer=None, device=device)
    criterion_dev = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32, device=device)
    )
    val_out = validate_one_epoch(model, val_loader, criterion_dev, device)
    metrics = calculate_metrics(val_out["labels"], val_out["predictions"])
    cm = compute_confusion_matrix(val_out["labels"], val_out["predictions"])

    payload = {
        "device": str(device),
        "seed": training_cfg["seed"],
        "in_channels": in_channels,
        "num_classes": num_classes,
        "learning_rate": training_cfg["learning_rate"],
        "weight_decay": training_cfg["weight_decay"],
        "batch_size": batch_size,
        "max_epochs": MAX_EPOCHS,
        "patience": EARLY_STOPPING_PATIENCE,
        "gradient_clipping": False,
        "train_event": "17 Aug 2026 (temporal_sequence_id=0)",
        "val_event": "18 Aug 2026 (temporal_sequence_id=1)",
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "train_event_ids": sorted({s["temporal_sequence_id"] for s in train_samples}),
        "val_event_ids": sorted({s["temporal_sequence_id"] for s in val_samples}),
        "event_id_overlap": sorted(
            {s["temporal_sequence_id"] for s in train_samples}
            & {s["temporal_sequence_id"] for s in val_samples}
        ),
        "train_class_distribution": _class_dist(train_labels),
        "val_class_distribution": _class_dist(val_labels),
        "class_weights": {CLASS_NAMES[i]: float(class_weights[i]) for i in range(NUM_CLASSES)},
        "history": history,
        "best_epoch": best_row["epoch"],
        "best_val_loss": best_row["val_loss"],
        "checkpoint_path": checkpoint_path,
        "val_metrics": metrics,
        "confusion_matrix": cm,
    }
    write_report(payload)
    print(REPORT_PATH.read_text(encoding="utf-8"))
    print("DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY")
    logger.info("POC training finished. Report: %s", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
