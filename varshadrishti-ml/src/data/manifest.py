import os
import h5py
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

EPOCH = datetime(2000, 1, 1)

def extract_timestamp(h5_path: Path) -> Optional[datetime]:
    """Extracts UTC timestamp from INSAT-3DR HDF5 file time dataset."""
    try:
        with h5py.File(h5_path, "r") as hf:
            for key in ("time", "scan_time", "Time", "IMAGE_DATE_AND_TIME"):
                if key in hf:
                    minutes = float(np.ravel(hf[key][()])[0])
                    return EPOCH + timedelta(minutes=minutes)
    except Exception:
        pass
    return None

def build_file_inventory(directory: Path, product_type: str) -> List[Dict[str, Any]]:
    """Scans a directory for HDF5 files and extracts metadata."""
    inventory = []
    
    if not directory.exists():
        return inventory
        
    for file_path in directory.rglob("*.h5"):
        timestamp = extract_timestamp(file_path)
        
        if timestamp:
            inventory.append({
                "filename": file_path.name,
                "full_path": str(file_path),
                "timestamp": timestamp,
                "product_type": product_type,
                "file_size": file_path.stat().st_size
            })
            
    return sorted(inventory, key=lambda x: x["timestamp"])
