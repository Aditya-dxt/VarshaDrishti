import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Any
import numpy as np


def validate_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Dict[str, Any]:
    """
    Runs one validation epoch. Returns loss, accuracy, predictions, labels,
    and probabilities for downstream evaluation.
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    all_preds: List[int] = []
    all_labels: List[int] = []
    all_probs: List[List[float]] = []

    with torch.no_grad():
        for batch in dataloader:
            sequences = batch["sequence"].to(device)
            labels = batch["label"].to(device)

            logits = model(sequences)
            loss = criterion(logits, labels)

            probs = torch.softmax(logits, dim=1)
            preds = probs.argmax(dim=1)

            total_loss += loss.item() * sequences.size(0)
            correct += (preds == labels).sum().item()
            total += sequences.size(0)

            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())
            all_probs.extend(probs.cpu().tolist())

    return {
        "loss": total_loss / total if total > 0 else 0.0,
        "accuracy": correct / total if total > 0 else 0.0,
        "predictions": all_preds,
        "labels": all_labels,
        "probabilities": all_probs,
    }
