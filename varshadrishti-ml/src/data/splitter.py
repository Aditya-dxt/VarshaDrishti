from typing import List, Tuple, Any

def split_by_time(
    samples: List[Any], 
    train_ratio: float = 0.7, 
    val_ratio: float = 0.15, 
    test_ratio: float = 0.15
) -> Tuple[List[Any], List[Any], List[Any]]:
    """
    Splits data chronologically to prevent temporal leakage.
    Earlier data -> Train
    Later data -> Validation
    Latest data -> Test
    """
    if not samples:
        return [], [], []
        
    total_ratio = train_ratio + val_ratio + test_ratio
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")

    n = len(samples)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    # Note: Assumes samples are already chronologically sorted.
    # The actual implementation should verify timestamps.
    
    train_split = samples[:train_end]
    val_split = samples[train_end:val_end]
    test_split = samples[val_end:]

    return train_split, val_split, test_split
