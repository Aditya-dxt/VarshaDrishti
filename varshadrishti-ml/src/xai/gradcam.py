import os
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

class GradCAM3D:
    """
    Computes 3D Grad-CAM for a specified target layer.
    """
    def __init__(self, model, target_layer_name='conv3'):
        self.model = model
        self.target_layer_name = target_layer_name
        self.gradients = None
        self.activations = None
        self.hooks = []
        
        self._register_hooks()
        
    def _register_hooks(self):
        target_layer = dict(self.model.named_modules()).get(self.target_layer_name)
        if target_layer is None:
            raise ValueError(f"Layer {self.target_layer_name} not found in model.")
            
        def forward_hook(module, input, output):
            self.activations = output
            
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
            
        self.hooks.append(target_layer.register_forward_hook(forward_hook))
        self.hooks.append(target_layer.register_full_backward_hook(backward_hook))

    def remove_hooks(self):
        for hook in self.hooks:
            hook.remove()

    def generate(self, input_tensor, target_class=None):
        """
        input_tensor: [B, C, T, H, W] tensor. Must have requires_grad=True if not already.
        Returns a [H_out, W_out] spatial heatmap in [0, 1].
        """
        was_training = self.model.training
        self.model.eval()
        self.model.zero_grad()
        
        # Clone and require grad to ensure gradients flow back to the input/target layer
        x = input_tensor.clone().detach().requires_grad_(True)
        
        logits = self.model(x)
        
        if target_class is None:
            target_class = logits.argmax(dim=1).item()
            
        target = logits[0, target_class]
        target.backward()
        
        # weights: [1, Channels, 1, 1, 1]
        weights = torch.mean(self.gradients, dim=(2, 3, 4), keepdim=True)
        
        # Weighted combinations of activations: [1, 1, T, H', W']
        cam_3d = torch.sum(weights * self.activations, dim=1, keepdim=True)
        
        # ReLU to keep only features that have a positive influence on the target class
        cam_3d = F.relu(cam_3d)
        
        # Aggregate across time (average) -> [1, 1, H', W']
        cam_2d = torch.mean(cam_3d, dim=2, keepdim=False)
        
        # Resize to original spatial dimensions
        orig_h, orig_w = input_tensor.shape[3], input_tensor.shape[4]
        cam_resized_tensor = F.interpolate(cam_2d, size=(orig_h, orig_w), mode='bilinear', align_corners=False)
        
        cam_resized = cam_resized_tensor.squeeze().detach().cpu().numpy()
        
        # Normalize to [0, 1]
        max_val = np.max(cam_resized)
        if max_val > 1e-8:
            cam_resized = cam_resized / max_val
        else:
            cam_resized = np.zeros_like(cam_resized)
            
        if was_training:
            self.model.train()
            
        return cam_resized

def save_heatmap_image(cam_2d, out_path):
    """
    Saves a normalized [0,1] 2D numpy array as a jet-colored heatmap image.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.imsave(out_path, cam_2d, cmap='jet')
