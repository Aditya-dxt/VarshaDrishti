import numpy as np
from typing import List, Dict, Tuple

def generate_patches(
    image_shape: Tuple[int, int],
    patch_size: int,
    stride: int,
    valid_mask: np.ndarray,
    min_valid_pct: float
) -> List[Tuple[int, int, int, int]]:
    """
    Generates patch coordinates (r1, r2, c1, c2) for a given shape and stride.
    Only keeps patches that meet the minimum valid pixel percentage.
    """
    H, W = image_shape
    patches = []
    
    for r in range(0, H - patch_size + 1, stride):
        for c in range(0, W - patch_size + 1, stride):
            r2, c2 = r + patch_size, c + patch_size
            
            mask_patch = valid_mask[r:r2, c:c2]
            valid_pct = 100.0 * np.sum(mask_patch) / mask_patch.size
            
            if valid_pct >= min_valid_pct:
                patches.append((r, r2, c, c2))
                
    return patches

def classify_patch_rainfall(rainfall_patch: np.ndarray, thresholds: Dict[str, float]) -> Dict[str, int]:
    """
    Classifies the pixels in a rainfall patch.
    """
    valid = rainfall_patch[~np.isnan(rainfall_patch)]
    
    if valid.size == 0:
        return {"total_valid": 0}
        
    counts = {
        "total_valid": valid.size,
        "no_rain": int(np.sum(valid <= thresholds["no_rain"])),
        "light": int(np.sum((valid > thresholds["no_rain"]) & (valid <= thresholds["light"]))),
        "moderate": int(np.sum((valid > thresholds["light"]) & (valid <= thresholds["moderate"]))),
        "heavy": int(np.sum((valid > thresholds["moderate"]) & (valid <= thresholds["heavy"]))),
        "high_impact": int(np.sum(valid > thresholds["heavy"]))
    }
    
    return counts
