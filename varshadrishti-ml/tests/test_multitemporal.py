"""
Tests for multi-temporal artifact creation, reload, DataLoader integration.

Note: Software fixtures are used for logic tests only.
They MUST NEVER be used for model training or scientific results.
"""

import sys
import json
import unittest
import tempfile
import shutil
import numpy as np
import torch
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from torch.utils.data import DataLoader
from src.data.dataset import VarshaDataset
from src.data.sequence_builder import build_temporal_sequences
from src.data.temporal_matcher import match_temporally

# ── Fixture helpers ──────────────────────────────────────────────────────────

def _make_pair(dt: datetime) -> dict:
    """Software-only fixture: a matched pair dict."""
    return {
        "timestamp": dt,
        "l1b_path": "/fake/l1b.h5",
        "l2b_path": "/fake/l2b.h5",
        "l1b_filename": "l1b.h5",
        "l2b_filename": "l2b.h5",
        "time_diff_minutes": 0.0
    }


T0 = datetime(2026, 8, 17, 21, 15)

ARTIFACT_DIR = BASE_DIR / "data" / "processed" / "multitemporal_dev"


class TestMultiTemporalArtifact(unittest.TestCase):
    """Integration tests against the real materialized artifact (if it exists)."""

    @classmethod
    def setUpClass(cls):
        cls.artifact_exists = ARTIFACT_DIR.exists() and (ARTIFACT_DIR / "data" / "sequences.npy").exists()

    def _skip_if_absent(self):
        if not self.artifact_exists:
            self.skipTest("Multitemporal artifact not yet materialized — skipping integration test.")

    # ─── Reload tests ────────────────────────────────────────────────────────

    def test_sequences_shape(self):
        self._skip_if_absent()
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        N, C, T, H, W = seq.shape
        self.assertEqual(C, 3, "Expected 3 input channels")
        self.assertEqual(T, 6, "Expected T=6 timestamps")
        self.assertEqual(H, 256)
        self.assertEqual(W, 256)

    def test_targets_shape(self):
        self._skip_if_absent()
        targets = np.load(ARTIFACT_DIR / "data" / "targets.npy")
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        self.assertEqual(targets.shape[0], seq.shape[0])
        self.assertEqual(targets.shape[1], 256)
        self.assertEqual(targets.shape[2], 256)

    def test_labels_shape(self):
        self._skip_if_absent()
        labels = np.load(ARTIFACT_DIR / "data" / "labels.npy")
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        self.assertEqual(labels.shape[0], seq.shape[0])

    def test_masks_shape(self):
        self._skip_if_absent()
        masks = np.load(ARTIFACT_DIR / "masks" / "masks.npy")
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        self.assertEqual(masks.shape[0], seq.shape[0])
        self.assertEqual(masks.dtype, bool)

    def test_no_nan_in_sequences(self):
        self._skip_if_absent()
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        self.assertFalse(np.isnan(seq).any(), "NaN found in sequences array")

    def test_no_inf_in_sequences(self):
        self._skip_if_absent()
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        self.assertFalse(np.isinf(seq).any(), "Inf found in sequences array")

    def test_valid_target_pixels_finite(self):
        self._skip_if_absent()
        targets = np.load(ARTIFACT_DIR / "data" / "targets.npy")
        masks = np.load(ARTIFACT_DIR / "masks" / "masks.npy")
        valid = targets[masks]
        self.assertFalse(np.isnan(valid).any(), "NaN in valid target pixels")
        self.assertFalse(np.isinf(valid).any(), "Inf in valid target pixels")

    def test_sequence_dtype(self):
        self._skip_if_absent()
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        self.assertEqual(seq.dtype, np.float32)

    def test_channel_order_in_metadata(self):
        self._skip_if_absent()
        with open(ARTIFACT_DIR / "metadata" / "metadata.json") as f:
            meta = json.load(f)
        self.assertEqual(meta["channels"], ["IMG_MIR", "IMG_TIR1", "IMG_TIR2"])

    def test_metadata_warning_present(self):
        self._skip_if_absent()
        with open(ARTIFACT_DIR / "metadata" / "metadata.json") as f:
            meta = json.load(f)
        self.assertIn("WARNING", meta)
        self.assertFalse(meta["scientific_training_ready"])
        self.assertFalse(meta["training_ready_for_scientific_training"])

    def test_metadata_timestamps_count(self):
        self._skip_if_absent()
        with open(ARTIFACT_DIR / "metadata" / "metadata.json") as f:
            meta = json.load(f)
        self.assertEqual(len(meta["source_timestamps"]), 6)

    def test_metadata_patch_count_matches_array(self):
        self._skip_if_absent()
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        with open(ARTIFACT_DIR / "metadata" / "metadata.json") as f:
            meta = json.load(f)
        self.assertEqual(meta["number_of_spatial_patches"], seq.shape[0])

    def test_no_repeated_timestamps_in_metadata(self):
        self._skip_if_absent()
        with open(ARTIFACT_DIR / "metadata" / "metadata.json") as f:
            meta = json.load(f)
        ts = meta["source_timestamps"]
        self.assertEqual(len(set(ts)), len(ts), "Duplicate timestamps in metadata")

    # ─── DataLoader integration ───────────────────────────────────────────────

    def test_dataloader_shape(self):
        self._skip_if_absent()
        seq = np.load(ARTIFACT_DIR / "data" / "sequences.npy")
        labels = np.load(ARTIFACT_DIR / "data" / "labels.npy")
        N, C, T, H, W = seq.shape

        items = []
        for i in range(N):
            items.append({
                "sequence": torch.from_numpy(seq[i]),  # [C, T, H, W]
                "label": int(labels[i]),
                "timestamp": f"seq_{i}"
            })

        dataset = VarshaDataset(items)
        loader = DataLoader(dataset, batch_size=4, shuffle=False)
        batch = next(iter(loader))

        self.assertEqual(batch["sequence"].shape, torch.Size([4, C, T, H, W]))
        self.assertEqual(batch["sequence"].shape[2], 6, "T dimension must be 6")

    def test_labels_valid_range(self):
        self._skip_if_absent()
        labels = np.load(ARTIFACT_DIR / "data" / "labels.npy")
        self.assertTrue(np.all(labels >= 0))
        self.assertTrue(np.all(labels <= 3))


class TestSequenceLogic(unittest.TestCase):
    """Pure software-fixture tests for sequence builder correctness."""

    def test_six_timestamps_form_one_sequence(self):
        pairs = [_make_pair(T0 + timedelta(minutes=i * 30)) for i in range(6)]
        seqs = build_temporal_sequences(pairs, sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 1)

    def test_sequence_has_correct_temporal_order(self):
        pairs = [_make_pair(T0 + timedelta(minutes=i * 30)) for i in range(6)]
        seqs = build_temporal_sequences(pairs, sequence_length=6, step_minutes=30)
        seq = seqs[0]
        ts = [f["timestamp"] for f in seq]
        self.assertEqual(ts, sorted(ts))

    def test_spatial_patch_consistency_fixture(self):
        """Verify that the same patch coordinates are used across timestamps."""
        # This tests the contract: if patches are (r1,r2,c1,c2), the same tuple
        # is applied to every timestamp. We verify the logic by ensuring
        # a synthetic array sliced at those coords produces the expected size.
        from src.data.patching import generate_patches
        H, W = 512, 512
        mask = np.ones((H, W), dtype=bool)
        patches = generate_patches((H, W), patch_size=256, stride=256,
                                   valid_mask=mask, min_valid_pct=90.0)
        # All patches must have exactly 256x256 size
        for r1, r2, c1, c2 in patches:
            self.assertEqual(r2 - r1, 256)
            self.assertEqual(c2 - c1, 256)

    def test_no_timestamp_duplication(self):
        pairs = [_make_pair(T0 + timedelta(minutes=i * 30)) for i in range(6)]
        seqs = build_temporal_sequences(pairs, sequence_length=6, step_minutes=30)
        for seq in seqs:
            ts = [f["timestamp"] for f in seq]
            self.assertEqual(len(set(ts)), len(ts))


if __name__ == "__main__":
    unittest.main()
