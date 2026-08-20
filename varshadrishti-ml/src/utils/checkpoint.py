import torch
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    metric: float,
    config: Dict[str, Any],
    save_path: str,
    dataset_info: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Saves a training checkpoint.

    IMPORTANT: This function must only be called during REAL training on
    REAL satellite data. The resulting checkpoint is the final model artifact.
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "validation_metric": metric,
        "config": config,
        "timestamp": datetime.utcnow().isoformat(),
        "dataset_info": dataset_info or {},
    }

    torch.save(checkpoint, save_path)


def load_checkpoint(
    model: torch.nn.Module,
    checkpoint_path: str,
    optimizer: Optional[torch.optim.Optimizer] = None,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """
    Loads a training checkpoint and restores model (and optionally optimizer) state.
    """
    if not Path(checkpoint_path).exists():
        raise FileNotFoundError(
            f"Checkpoint not found at: {checkpoint_path}. "
            "Real model training has not yet been performed."
        )

    if device is None:
        device = torch.device("cpu")

    checkpoint = torch.load(checkpoint_path, map_location=device)

    model.load_state_dict(checkpoint["model_state_dict"])

    if optimizer is not None and "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    return checkpoint
