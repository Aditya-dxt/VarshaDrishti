import numpy as np
import h5py

def load_rainfall(dataset: h5py.Dataset, fill_value: float = -999.0) -> np.ndarray:
    """
    Loads IMC rainfall and masks fill values with NaN.
    """
    raw = dataset[()]
    if raw.ndim == 3 and raw.shape[0] == 1:
        raw = raw[0]
        
    arr = raw.astype(np.float64)
    invalid_mask = np.isclose(arr, fill_value) | ~np.isfinite(arr)
    
    arr[invalid_mask] = np.nan
    return arr
