import sys
import os
import unittest
import tempfile
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.train import validate_training_data, EarlyStopper, Trainer, train_one_epoch
from src.training.validate import validate_one_epoch
from src.models.cnn3d import VarshaDrishti3DCNN
from src.data.dataset import VarshaDataset


class TestEarlyStopper(unittest.TestCase):

    def test_stops_on_no_improvement(self):
        stopper = EarlyStopper(patience=3, mode="min")
        self.assertFalse(stopper.update(1.0))
        self.assertFalse(stopper.update(1.1))
        self.assertFalse(stopper.update(1.2))
        self.assertTrue(stopper.update(1.3))   # 3 no-improvements → stop

    def test_resets_on_improvement(self):
        stopper = EarlyStopper(patience=2, mode="min")
        stopper.update(1.0)
        stopper.update(1.1)       # no improvement
        stopper.update(0.5)       # improvement — resets counter
        self.assertFalse(stopper.stop)


class TestSafetyGate(unittest.TestCase):

    def test_empty_train_loader_raises(self):
        empty_dataset = VarshaDataset([])
        empty_loader = DataLoader(empty_dataset)
        with self.assertRaises(RuntimeError) as ctx:
            validate_training_data(empty_loader, empty_loader)
        self.assertIn("REAL TRAINING DATA REQUIRED", str(ctx.exception))

    def test_none_loader_raises(self):
        with self.assertRaises(RuntimeError):
            validate_training_data(None, None)


class TestTrainOneEpoch(unittest.TestCase):

    def setUp(self):
        # TEST ONLY
        # Synthetic fixture.
        # NOT satellite data.
        # NOT used for final training.
        # NOT used for hackathon results.
        self.model = VarshaDrishti3DCNN(in_channels=2, num_classes=4)
        self.device = torch.device("cpu")
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-3)

        # Tiny synthetic dataset: 4 samples shaped [C=2, T=3, H=16, W=16]
        # TEST ONLY — synthetic fixture, NOT satellite data.
        sequences = [torch.randn(2, 3, 16, 16) for _ in range(4)]
        labels = [0, 1, 2, 3]
        items = [{"sequence": s, "label": l, "timestamp": "", "latitude": 0.0, "longitude": 0.0}
                 for s, l in zip(sequences, labels)]
        dataset = VarshaDataset(items)
        self.loader = DataLoader(dataset, batch_size=2)

    def test_train_one_epoch_returns_metrics(self):
        # TEST ONLY — synthetic fixture
        metrics = train_one_epoch(
            model=self.model,
            dataloader=self.loader,
            optimizer=self.optimizer,
            criterion=self.criterion,
            device=self.device,
        )
        self.assertIn("loss", metrics)
        self.assertIn("accuracy", metrics)
        self.assertIsInstance(metrics["loss"], float)

    def test_validate_one_epoch_returns_metrics(self):
        # TEST ONLY — synthetic fixture
        result = validate_one_epoch(
            model=self.model,
            dataloader=self.loader,
            criterion=self.criterion,
            device=self.device,
        )
        self.assertIn("loss", result)
        self.assertIn("predictions", result)
        self.assertIn("labels", result)
        self.assertIn("probabilities", result)
        self.assertEqual(len(result["predictions"]), 4)


if __name__ == "__main__":
    unittest.main()
