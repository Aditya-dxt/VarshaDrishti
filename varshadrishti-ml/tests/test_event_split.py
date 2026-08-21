"""
Leakage tests for event-level train/validation splits.

Software fixtures are for logic tests only.
They MUST NOT be used as scientific training results.
"""

import json
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.splitter import split_by_temporal_event

ARTIFACT_DIR = BASE_DIR / "data" / "processed" / "multitemporal_dev"
MANIFEST_PATH = ARTIFACT_DIR / "manifest" / "sequence_manifest.json"


def _sample(idx: int, event_id: int) -> dict:
    return {
        "patch_idx": idx,
        "temporal_sequence_id": event_id,
        "label": 0,
        "sequence": None,
    }


class TestSplitByTemporalEvent(unittest.TestCase):

    def test_two_events_go_to_separate_splits(self):
        samples = [_sample(i, 0) for i in range(3)] + [_sample(10 + i, 1) for i in range(3)]
        train, val = split_by_temporal_event(samples, train_event_ids=[0], val_event_ids=[1])
        self.assertEqual({s["temporal_sequence_id"] for s in train}, {0})
        self.assertEqual({s["temporal_sequence_id"] for s in val}, {1})
        self.assertEqual(len(train), 3)
        self.assertEqual(len(val), 3)

    def test_no_temporal_sequence_id_in_both_splits(self):
        samples = [_sample(i, 0) for i in range(5)] + [_sample(100 + i, 1) for i in range(5)]
        train, val = split_by_temporal_event(samples, train_event_ids=[0], val_event_ids=[1])
        leaked = {s["temporal_sequence_id"] for s in train} & {s["temporal_sequence_id"] for s in val}
        self.assertEqual(leaked, set())
        train_idx = {s["patch_idx"] for s in train}
        val_idx = {s["patch_idx"] for s in val}
        self.assertEqual(train_idx & val_idx, set())

    def test_rejects_overlapping_event_assignment(self):
        samples = [_sample(0, 0), _sample(1, 1)]
        with self.assertRaises(ValueError) as ctx:
            split_by_temporal_event(samples, train_event_ids=[0, 1], val_event_ids=[1])
        self.assertIn("leakage", str(ctx.exception).lower())

    def test_empty_input_returns_empty(self):
        train, val = split_by_temporal_event([], train_event_ids=[0], val_event_ids=[1])
        self.assertEqual(train, [])
        self.assertEqual(val, [])

    def test_missing_event_raises(self):
        samples = [_sample(0, 0)]
        with self.assertRaises(ValueError):
            split_by_temporal_event(samples, train_event_ids=[0], val_event_ids=[1])


class TestRealManifestEventSplit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manifest_exists = MANIFEST_PATH.exists()

    def _skip_if_absent(self):
        if not self.manifest_exists:
            self.skipTest("sequence_manifest.json not present — skipping real-artifact leakage test.")

    def test_real_events_have_no_id_leakage(self):
        self._skip_if_absent()
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)
        train, val = split_by_temporal_event(samples, train_event_ids=[0], val_event_ids=[1])
        train_ids = {s["temporal_sequence_id"] for s in train}
        val_ids = {s["temporal_sequence_id"] for s in val}
        self.assertEqual(train_ids, {0})
        self.assertEqual(val_ids, {1})
        self.assertEqual(train_ids & val_ids, set())
        self.assertEqual(len(train), 69)
        self.assertEqual(len(val), 69)
        train_patches = {s["patch_idx"] for s in train}
        val_patches = {s["patch_idx"] for s in val}
        self.assertEqual(train_patches & val_patches, set())
        train_days = {ts[:10] for s in train for ts in s["timestamps"]}
        val_days = {ts[:10] for s in val for ts in s["timestamps"]}
        self.assertEqual(train_days, {"2026-08-17"})
        self.assertEqual(val_days, {"2026-08-18"})
        self.assertEqual(train_days & val_days, set())

    def test_does_not_use_ratio_split_on_patches(self):
        """Event-level split must not be equivalent to slicing the 138 patches 70/15/15."""
        self._skip_if_absent()
        from src.data.splitter import split_by_time
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)
        train, val = split_by_temporal_event(samples, train_event_ids=[0], val_event_ids=[1])
        ratio_train, ratio_val, ratio_test = split_by_time(samples, 0.7, 0.15, 0.15)
        self.assertNotEqual([s["patch_idx"] for s in train], [s["patch_idx"] for s in ratio_train])
        self.assertTrue(all(s["temporal_sequence_id"] == 0 for s in train))
        self.assertTrue(all(s["temporal_sequence_id"] == 1 for s in val))


class TestTrainOnlyClassWeights(unittest.TestCase):

    def test_weights_ignore_validation_counts(self):
        import importlib.util

        script = BASE_DIR / "scripts" / "train_development.py"
        spec = importlib.util.spec_from_file_location("train_development_script", script)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)

        train_labels = [0, 0, 0, 1]
        weights = mod.inverse_frequency_weights(train_labels, num_classes=4)
        self.assertAlmostEqual(weights[0], 4 / (4 * 3))
        self.assertAlmostEqual(weights[1], 4 / (4 * 1))
        self.assertEqual(weights[2], 0.0)
        self.assertEqual(weights[3], 0.0)


if __name__ == "__main__":
    unittest.main()
