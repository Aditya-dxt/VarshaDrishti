"""
Tests for real-data 3D-CNN forward-pass smoke validation.

Uses the existing VarshaDataset and VarshaDrishti3DCNN.
Does not train. Skips if the multitemporal artifact is not present.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

import torch
from torch.utils.data import DataLoader

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.dataset import VarshaDataset
from src.models.cnn3d import VarshaDrishti3DCNN

_SCRIPT = BASE_DIR / "scripts" / "test_real_multitemporal_forward.py"
_spec = importlib.util.spec_from_file_location("real_multitemporal_forward_script", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)

ARTIFACT_DIR = _mod.ARTIFACT_DIR
build_varsha_dataset = _mod.build_varsha_dataset
load_artifact_arrays = _mod.load_artifact_arrays
run_forward_pass = _mod.run_forward_pass


class TestRealMultitemporalForwardPass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact_exists = (
            ARTIFACT_DIR.exists() and (ARTIFACT_DIR / "data" / "sequences.npy").exists()
        )

    def _skip_if_absent(self):
        if not self.artifact_exists:
            self.skipTest("Multitemporal artifact not yet materialized — skipping forward-pass test.")

    def test_dataloader_and_model_forward_contract(self):
        self._skip_if_absent()
        arrays = load_artifact_arrays()
        dataset = build_varsha_dataset(arrays)
        self.assertIsInstance(dataset, VarshaDataset)
        self.assertGreaterEqual(len(dataset), 2)

        loader = DataLoader(dataset, batch_size=2, shuffle=False)
        batch = next(iter(loader))
        sequences = batch["sequence"]
        self.assertEqual(tuple(sequences.shape), (2, 3, 6, 256, 256))
        self.assertEqual(sequences.dtype, torch.float32)
        self.assertFalse(torch.isnan(sequences).any())
        self.assertFalse(torch.isinf(sequences).any())

        model = VarshaDrishti3DCNN(in_channels=3, num_classes=4)
        model.eval()
        with torch.no_grad():
            logits = model(sequences)
        self.assertEqual(tuple(logits.shape), (2, 4))
        self.assertFalse(torch.isnan(logits).any())
        self.assertFalse(torch.isinf(logits).any())

        probs = torch.softmax(logits, dim=1)
        self.assertFalse(torch.isnan(probs).any())
        self.assertFalse(torch.isinf(probs).any())
        sums = probs.sum(dim=1)
        self.assertTrue(torch.allclose(sums, torch.ones_like(sums), atol=1e-5))
        preds = probs.argmax(dim=1)
        self.assertTrue(((preds >= 0) & (preds < 4)).all())

    def test_multiple_batches_eval_no_training(self):
        self._skip_if_absent()
        result = run_forward_pass(batch_size=4, max_batches=3)
        self.assertGreaterEqual(result.n_batches, 2)
        self.assertTrue(result.weights_unchanged)
        self.assertFalse(result.training_performed)
        self.assertTrue(result.passed, msg=result.failures)
        self.assertEqual(result.num_classes, 4)
        self.assertEqual(result.model_output_shape[-1], 4)


if __name__ == "__main__":
    unittest.main()
