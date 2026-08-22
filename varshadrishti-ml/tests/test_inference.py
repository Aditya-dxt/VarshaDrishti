"""
Focused tests for the backend inference integration.
"""
import unittest
import numpy as np
import torch
from pathlib import Path

from src.inference.backend_adapter import VarshaDrishtiPredictor

class TestBackendInference(unittest.TestCase):
    def setUp(self):
        # We test with the actual POC checkpoint and artifact 
        # as requested for the integration POC.
        self.predictor = VarshaDrishtiPredictor()

    def test_checkpoint_loads_and_eval_mode(self):
        self.assertFalse(self.predictor.model.training, "Model should be in eval() mode")

    def test_inference_shape_and_probabilities(self):
        # Use first patch
        result = self.predictor.predict({"patch_idx": 0})
        
        # Check overall structure
        self.assertIn("prediction", result)
        self.assertIn("probabilities", result)
        
        # Check prediction
        pred = result["prediction"]
        self.assertIn(pred["class_id"], [0, 1, 2, 3])
        self.assertIsInstance(pred["label"], str)
        self.assertTrue(0.0 <= pred["confidence"] <= 1.0)
        
        # Check probabilities
        probs = result["probabilities"]
        self.assertEqual(len(probs), 4)
        self.assertIn("no_rain", probs)
        self.assertIn("moderate", probs)
        self.assertIn("heavy", probs)
        self.assertIn("high_impact", probs)
        
        # Sum to approx 1
        prob_sum = sum(probs.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=4)
        
        # Check for NaNs
        for k, v in probs.items():
            self.assertFalse(np.isnan(v), f"NaN probability found for {k}")
            self.assertFalse(np.isinf(v), f"Inf probability found for {k}")

    def test_missing_checkpoint_raises(self):
        with self.assertRaises(RuntimeError) as context:
            VarshaDrishtiPredictor(checkpoint_path="/fake/path/does/not/exist.pth")
        self.assertIn("Missing checkpoint", str(context.exception))

    def test_metadata_extraction_and_latest_event(self):
        # By default, predict() with no observation should select the latest event
        # and pull the real timestamps from the sequence manifest.
        result = self.predictor.predict(None)
        
        self.assertIn("metadata", result)
        metadata = result["metadata"]
        
        # We expect the timestamp to be pulled from the manifest
        self.assertIn("T", metadata["timestamp"])
        self.assertIn("Z", metadata["timestamp"])
        
        # Since we have two events in the dev data (Aug 17 and Aug 18), 
        # the latest event is Aug 18.
        self.assertTrue("2026-08-18" in metadata["timestamp"], 
                        f"Expected latest event (Aug 18) to be selected, got {metadata['timestamp']}")

    def test_metadata_specific_patch(self):
        # Predict on patch 0 (which is Aug 17 in the manifest)
        result = self.predictor.predict({"patch_idx": 0})
        
        metadata = result["metadata"]
        self.assertTrue("2026-08-17" in metadata["timestamp"], 
                        f"Expected Aug 17 for patch 0, got {metadata['timestamp']}")

if __name__ == "__main__":
    unittest.main()
