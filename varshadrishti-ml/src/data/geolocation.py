import numpy as np
import h5py
from typing import Tuple

def decode_geolocation(lat_ds: h5py.Dataset, lon_ds: h5py.Dataset, 
                       fill_value: int = 32767, scale_factor: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
    """
    Decodes L1B/L2B integer geolocation grids to float degrees.
    """
    lat_raw = lat_ds[()]
    lon_raw = lon_ds[()]
    
    # Pre-allocate NaNs
    lat = np.full(lat_raw.shape, np.nan, dtype=np.float64)
    lon = np.full(lon_raw.shape, np.nan, dtype=np.float64)
    
    valid_lat = (lat_raw != fill_value)
    valid_lon = (lon_raw != fill_value)
    
    lat[valid_lat] = lat_raw[valid_lat].astype(np.float64) * scale_factor
    lon[valid_lon] = lon_raw[valid_lon].astype(np.float64) * scale_factor
    
    return lat, lon
