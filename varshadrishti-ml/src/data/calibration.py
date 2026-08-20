import numpy as np
import h5py
from typing import Dict, Tuple

def calibrate_channel(dataset: h5py.Dataset, fill_value: int = 1023, use_gsics: bool = False) -> Tuple[np.ndarray, Dict]:
    """
    Applies the MOSDAC quadratic radiometric calibration to raw counts.
    
    Formula:
    L = C^2 * quad + C * scale_factor + offset
    """
    raw_counts = dataset[()]
    if raw_counts.ndim == 3 and raw_counts.shape[0] == 1:
        raw_counts = raw_counts[0]
        
    counts = raw_counts.astype(np.float64)
    valid_mask = (raw_counts != fill_value) & np.isfinite(counts)
    
    # Extract coefficients
    attrs = dataset.attrs
    
    prefix = "lab_radiance"
    suffix = "_gsics" if use_gsics else ""
    
    try:
        quad = float(attrs[f"{prefix}_quad{suffix}"][0])
        scale = float(attrs[f"{prefix}_scale_factor{suffix}"][0])
        offset = float(attrs[f"{prefix}_add_offset{suffix}"][0])
    except KeyError as e:
        raise ValueError(f"Missing calibration attribute for {dataset.name}: {e}")
        
    radiance = np.full_like(counts, np.nan)
    C = counts[valid_mask]
    
    radiance[valid_mask] = (C**2) * quad + C * scale + offset
    
    meta = {
        "calibrated": True,
        "method": "GSICS" if use_gsics else "LAB_STANDARD",
        "quad": quad,
        "scale": scale,
        "offset": offset,
        "units": attrs.get("radiance_units", b"").decode("utf-8")
    }
    
    return radiance, meta
