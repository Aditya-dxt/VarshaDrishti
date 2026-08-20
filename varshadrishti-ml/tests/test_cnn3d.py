import os
import sys
import unittest
from pathlib import Path
import torch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.cnn3d import VarshaDrishti3DCNN, get_model_summary

class TestVarshaDrishti3DCNN(unittest.TestCase):

    def setUp(self):
        # We explicitly set in_channels for tests as it is null in config
        self.in_channels = 4
        self.num_classes = 4
        self.model = VarshaDrishti3DCNN(in_channels=self.in_channels, num_classes=self.num_classes)
        # Ensure model is in eval mode for simple forward pass tests (disables dropout randomness)
        self.model.eval()

    def test_model_initialization(self):
        """Test model initializes correctly and rejects bad in_channels."""
        with self.assertRaises(ValueError):
            VarshaDrishti3DCNN(in_channels=None)
        with self.assertRaises(ValueError):
            VarshaDrishti3DCNN(in_channels=0)
            
        self.assertEqual(self.model.in_channels, self.in_channels)
        self.assertEqual(self.model.num_classes, self.num_classes)

    def test_invalid_input_dimensions(self):
        """Test model rejects tensors without 5 dimensions or wrong channels."""
        # TEST ONLY
        # Synthetic tensor used exclusively for architecture validation.
        
        # 4D tensor (missing batch or time)
        bad_input_4d = torch.randn(self.in_channels, 6, 64, 64)
        with self.assertRaises(ValueError):
            self.model(bad_input_4d)
            
        # Wrong channels
        bad_input_channels = torch.randn(2, self.in_channels + 1, 6, 64, 64)
        with self.assertRaises(ValueError):
            self.model(bad_input_channels)

    def test_forward_pass_and_output_shape(self):
        """Test the forward pass produces correct [B, 4] output shape."""
        # TEST ONLY
        # Synthetic tensor used exclusively for architecture validation.
        # NOT satellite data.
        # NOT used for training.
        # NOT used for hackathon results.
        
        batch_size = 2
        seq_length = 6
        h, w = 64, 64
        
        dummy_input = torch.randn(batch_size, self.in_channels, seq_length, h, w)
        output = self.model(dummy_input)
        
        self.assertEqual(output.shape, (batch_size, self.num_classes))

    def test_forward_pass_different_spatial_dims(self):
        """Test adaptive pooling handles different spatial dimensions safely."""
        # TEST ONLY
        # Synthetic tensor used exclusively for architecture validation.
        
        batch_size = 1
        seq_length = 4
        h, w = 128, 128
        
        dummy_input = torch.randn(batch_size, self.in_channels, seq_length, h, w)
        output = self.model(dummy_input)
        
        self.assertEqual(output.shape, (batch_size, self.num_classes))

    def test_gradient_flow(self):
        """Test that gradients flow backward through the network."""
        # TEST ONLY
        # Synthetic tensor used exclusively for architecture validation.
        
        self.model.train() # Enable training mode for gradients
        dummy_input = torch.randn(2, self.in_channels, 4, 32, 32)
        dummy_target = torch.randn(2, self.num_classes)
        
        output = self.model(dummy_input)
        loss = torch.nn.functional.mse_loss(output, dummy_target)
        loss.backward()
        
        # Check if gradients exist in the first layer
        self.assertIsNotNone(self.model.conv1.weight.grad)
        self.assertNotEqual(torch.sum(torch.abs(self.model.conv1.weight.grad)).item(), 0)

    def test_model_summary(self):
        """Test model summary utility."""
        summary = get_model_summary(self.model)
        self.assertEqual(summary["model_name"], "VarshaDrishti3DCNN")
        self.assertEqual(summary["input_contract"], "[B, C, T, H, W]")
        self.assertEqual(summary["output_contract"], "[B, 4]")
        self.assertGreater(summary["total_parameters"], 0)
        self.assertGreater(summary["trainable_parameters"], 0)

if __name__ == '__main__':
    unittest.main()
