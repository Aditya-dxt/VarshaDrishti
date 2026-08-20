import torch
import torch.nn as nn

class VarshaDrishti3DCNN(nn.Module):
    """
    Baseline 3D-CNN for VarshaDrishti satellite rainfall prediction.
    Expected Input: [B, C, T, H, W]
    Expected Output: [B, num_classes] (raw logits)
    """
    def __init__(self, in_channels: int, num_classes: int = 4, dropout: float = 0.3):
        super(VarshaDrishti3DCNN, self).__init__()
        
        if in_channels is None or in_channels <= 0:
            raise ValueError("in_channels must be a positive integer.")
            
        self.in_channels = in_channels
        self.num_classes = num_classes

        # Block 1
        self.conv1 = nn.Conv3d(in_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm3d(32)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool3d(kernel_size=(1, 2, 2))

        # Block 2
        self.conv2 = nn.Conv3d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm3d(64)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool3d(kernel_size=(2, 2, 2))

        # Block 3
        self.conv3 = nn.Conv3d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm3d(128)
        self.relu3 = nn.ReLU()

        # Global Average Pooling
        self.adaptive_pool = nn.AdaptiveAvgPool3d((1, 1, 1))

        # Fully Connected Layer
        self.flatten = nn.Flatten()
        self.dropout = nn.Dropout(p=dropout)
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        x: Tensor of shape [B, C, T, H, W]
        Returns raw logits.
        """
        if x.dim() != 5:
            raise ValueError(f"Expected input shape [B, C, T, H, W], got {x.shape}")
        if x.size(1) != self.in_channels:
            raise ValueError(f"Expected {self.in_channels} channels, got {x.size(1)}")

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.pool2(x)

        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu3(x)

        x = self.adaptive_pool(x)
        x = self.flatten(x)
        x = self.dropout(x)
        x = self.fc(x)

        return x

def get_model_summary(model: nn.Module) -> dict:
    """Returns a summary of the model."""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        "model_name": model.__class__.__name__,
        "input_contract": "[B, C, T, H, W]",
        "output_contract": f"[B, {model.num_classes}]",
        "total_parameters": total_params,
        "trainable_parameters": trainable_params
    }
