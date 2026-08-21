import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional, List
import numpy as np


def validate_training_data(train_loader: DataLoader, val_loader: DataLoader) -> None:
    """
    Safety gate: validates that real datasets are non-empty before training begins.

    IMPORTANT: REAL INSAT-3DR + rainfall training data MUST be present.
    This function MUST raise RuntimeError if data is missing or invalid.
    DO NOT generate synthetic fallback data here.
    """
    if train_loader is None or len(train_loader.dataset) == 0:
        raise RuntimeError(
            "REAL TRAINING DATA REQUIRED — TRAINING NOT STARTED.\n"
            "The training dataset is empty. Real INSAT-3DR satellite data "
            "and matched rainfall targets are required."
        )

    if val_loader is None or len(val_loader.dataset) == 0:
        raise RuntimeError(
            "REAL VALIDATION DATA REQUIRED — TRAINING NOT STARTED.\n"
            "The validation dataset is empty."
        )


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    gradient_clipping: bool = False,
    max_norm: float = 1.0,
) -> Dict[str, float]:
    """Runs one training epoch. Returns train loss and accuracy."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch in dataloader:
        sequences = batch["sequence"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        logits = model(sequences)
        loss = criterion(logits, labels)
        loss.backward()

        if gradient_clipping:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)

        optimizer.step()

        total_loss += loss.item() * sequences.size(0)
        preds = logits.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += sequences.size(0)

    return {
        "loss": total_loss / total if total > 0 else 0.0,
        "accuracy": correct / total if total > 0 else 0.0,
    }


class EarlyStopper:
    """Implements early stopping based on a monitored metric (lower is better by default)."""

    def __init__(self, patience: int = 5, mode: str = "min"):
        """
        patience: epochs to wait with no improvement before stopping.
        mode: 'min' for loss (lower=better) or 'max' for F1 (higher=better).
        """
        self.patience = patience
        self.mode = mode
        self.best_value = float("inf") if mode == "min" else float("-inf")
        self.counter = 0
        self.stop = False

    def update(self, value: float) -> bool:
        """Returns True if training should stop."""
        improved = (self.mode == "min" and value < self.best_value) or \
                   (self.mode == "max" and value > self.best_value)

        if improved:
            self.best_value = value
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.stop = True

        return self.stop


class Trainer:
    """
    Orchestrates REAL model training. Must only be used with real datasets.
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        device: torch.device,
        config: Dict[str, Any],
        checkpoint_path: Optional[str] = None,
    ):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.config = config
        self.checkpoint_path = checkpoint_path
        self.history: List[Dict[str, Any]] = []

        training_cfg = config.get("training", {})
        es_cfg = training_cfg.get("early_stopping", {})
        self.early_stopper = EarlyStopper(
            patience=es_cfg.get("patience", 5),
            mode="min",
        ) if es_cfg.get("enabled", True) else None

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        from_epoch: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Runs the full training loop.
        Requires REAL non-empty train and validation DataLoaders.
        """
        from src.training.validate import validate_one_epoch
        from src.utils.checkpoint import save_checkpoint
        import logging

        logger = logging.getLogger("trainer")

        # --- SAFETY GATE ---
        validate_training_data(train_loader, val_loader)

        training_cfg = self.config.get("training", {})
        epochs = training_cfg.get("epochs", 30)
        gc_cfg = training_cfg.get("gradient_clipping", {})

        best_val_loss = float("inf")

        for epoch in range(from_epoch, epochs):
            train_metrics = train_one_epoch(
                model=self.model,
                dataloader=train_loader,
                optimizer=self.optimizer,
                criterion=self.criterion,
                device=self.device,
                gradient_clipping=gc_cfg.get("enabled", False),
                max_norm=gc_cfg.get("max_norm", 1.0),
            )
            val_metrics = validate_one_epoch(
                model=self.model,
                dataloader=val_loader,
                criterion=self.criterion,
                device=self.device,
            )

            epoch_record = {
                "epoch": epoch + 1,
                "train_loss": train_metrics["loss"],
                "train_accuracy": train_metrics["accuracy"],
                "val_loss": val_metrics["loss"],
                "val_accuracy": val_metrics["accuracy"],
                "learning_rate": self.optimizer.param_groups[0]["lr"],
            }
            self.history.append(epoch_record)

            logger.info(
                f"Epoch {epoch+1}/{epochs} | "
                f"TrainLoss={train_metrics['loss']:.4f} | "
                f"ValLoss={val_metrics['loss']:.4f} | "
                f"ValAcc={val_metrics['accuracy']:.4f}"
            )

            # Save best checkpoint
            if val_metrics["loss"] < best_val_loss:
                best_val_loss = val_metrics["loss"]
                if self.checkpoint_path and training_cfg.get("checkpoint", {}).get("enabled", True):
                    save_checkpoint(
                        model=self.model,
                        optimizer=self.optimizer,
                        epoch=epoch + 1,
                        metric=best_val_loss,
                        config=self.config,
                        save_path=self.checkpoint_path,
                    )
                    logger.info(f"  Checkpoint saved (val_loss={best_val_loss:.4f})")

            # Early stopping
            if self.early_stopper and self.early_stopper.update(val_metrics["loss"]):
                logger.info(f"Early stopping triggered at epoch {epoch+1}.")
                break

        return self.history
