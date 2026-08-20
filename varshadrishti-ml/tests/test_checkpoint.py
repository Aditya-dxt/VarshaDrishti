import sys
import os
import tempfile
import unittest
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.checkpoint import save_checkpoint, load_checkpoint
from src.models.cnn3d import VarshaDrishti3DCNN


class TestCheckpoint(unittest.TestCase):

    def setUp(self):
        # TEST ONLY
        # Synthetic model state — not satellite data.
        # Never used for final model training or hackathon results.
        self.model = VarshaDrishti3DCNN(in_channels=2, num_classes=4)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-3)
        self.config = {"model": {"in_channels": 2, "num_classes": 4}}

    def test_save_and_load(self):
        """Test that checkpoint saves and restores model state correctly."""
        # TEST ONLY — synthetic fixture
        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt_path = os.path.join(tmpdir, "TEST_ONLY_synthetic_smoke_test.pth")

            save_checkpoint(
                model=self.model,
                optimizer=self.optimizer,
                epoch=1,
                metric=0.5,
                config=self.config,
                save_path=ckpt_path,
            )

            self.assertTrue(os.path.exists(ckpt_path))

            # Create a fresh model and restore
            new_model = VarshaDrishti3DCNN(in_channels=2, num_classes=4)
            ckpt = load_checkpoint(new_model, ckpt_path)

            self.assertEqual(ckpt["epoch"], 1)
            self.assertAlmostEqual(ckpt["validation_metric"], 0.5)
            self.assertIn("timestamp", ckpt)

            # Verify weights were actually restored
            for (name_a, param_a), (name_b, param_b) in zip(
                self.model.named_parameters(), new_model.named_parameters()
            ):
                self.assertTrue(torch.allclose(param_a, param_b), f"Mismatch in {name_a}")

    def test_load_missing_checkpoint_raises(self):
        """Test that loading a non-existent checkpoint raises FileNotFoundError."""
        new_model = VarshaDrishti3DCNN(in_channels=2, num_classes=4)
        with self.assertRaises(FileNotFoundError) as ctx:
            load_checkpoint(new_model, "models/checkpoints/best_model.pth")
        self.assertIn("Real model training has not yet been performed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
