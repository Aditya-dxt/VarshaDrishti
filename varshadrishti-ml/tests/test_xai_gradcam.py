import unittest
import numpy as np
import torch
import copy
from pathlib import Path

import sys
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models.cnn3d import VarshaDrishti3DCNN
from src.xai.gradcam import GradCAM3D

class TestGradCAM3D(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cpu")
        self.model = VarshaDrishti3DCNN(in_channels=3, num_classes=4, dropout=0.0)
        self.model.eval()
        
        # Save a copy of state dict to verify weights don't change
        self.initial_state_dict = copy.deepcopy(self.model.state_dict())
        
        # Create a dummy input matching the real shape [B, C, T, H, W]
        self.dummy_input = torch.rand((1, 3, 6, 256, 256), dtype=torch.float32)

    def test_gradcam_output_shape_and_range(self):
        cam_generator = GradCAM3D(self.model, target_layer_name='conv3')
        heatmap = cam_generator.generate(self.dummy_input)
        cam_generator.remove_hooks()
        
        # 1. Runs on real model architecture (no exception)
        self.assertIsNotNone(heatmap)
        
        # 2. Output shape is 256x256
        self.assertEqual(heatmap.shape, (256, 256))
        
        # 3. No NaN/Inf
        self.assertFalse(np.isnan(heatmap).any())
        self.assertFalse(np.isinf(heatmap).any())
        
        # 4. Values within [0, 1]
        self.assertTrue((heatmap >= 0.0).all())
        self.assertTrue((heatmap <= 1.0 + 1e-6).all())

    def test_model_weights_unchanged(self):
        cam_generator = GradCAM3D(self.model, target_layer_name='conv3')
        cam_generator.generate(self.dummy_input)
        cam_generator.remove_hooks()
        
        # 5. Model weights are unchanged
        for name, param in self.model.state_dict().items():
            self.assertTrue(torch.equal(param, self.initial_state_dict[name]), f"Weight {name} changed after Grad-CAM!")

    def test_deterministic_class_selection(self):
        # 6. The predicted class used for Grad-CAM is deterministic
        torch.manual_seed(42)
        cam_generator1 = GradCAM3D(self.model, target_layer_name='conv3')
        heatmap1 = cam_generator1.generate(self.dummy_input)
        cam_generator1.remove_hooks()
        
        torch.manual_seed(42)
        cam_generator2 = GradCAM3D(self.model, target_layer_name='conv3')
        heatmap2 = cam_generator2.generate(self.dummy_input)
        cam_generator2.remove_hooks()
        
        self.assertTrue(np.allclose(heatmap1, heatmap2, atol=1e-6))

if __name__ == '__main__':
    unittest.main()
