import torch

def get_device(device_config: str = "auto") -> torch.device:
    """
    Detects and returns the appropriate PyTorch device.
    Supports CUDA if available, otherwise falls back to CPU.
    """
    if device_config == "auto":
        if torch.cuda.is_available():
            device_name = "cuda"
        else:
            device_name = "cpu"
    else:
        device_name = device_config

    device = torch.device(device_name)
    return device

def get_device_info() -> dict:
    """Returns information about the available computational devices."""
    info = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "current_device_index": torch.cuda.current_device() if torch.cuda.is_available() else None,
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    }
    return info
