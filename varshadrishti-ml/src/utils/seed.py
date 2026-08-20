import random
import numpy as np
import torch

def set_seed(seed: int = 42) -> None:
    """
    Sets the random seed for reproducibility across Python, NumPy, and PyTorch.

    NOTE: Setting a seed improves reproducibility but does NOT guarantee
    bit-exact determinism across all hardware, backends, or CUDA versions.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
