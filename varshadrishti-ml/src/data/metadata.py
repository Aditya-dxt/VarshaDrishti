from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class Metadata:
    """Structured metadata for satellite observations."""
    file_path: Optional[str] = None
    timestamp: Optional[str] = None
    latitude_shape: Optional[List[int]] = None
    longitude_shape: Optional[List[int]] = None
    channels: Optional[List[str]] = None
    spatial_resolution: Optional[str] = None
    units: Optional[Dict[str, str]] = None
    source: Optional[str] = None
    product_id: Optional[str] = None

@dataclass
class SatelliteFrame:
    """
    Representation of one satellite observation.
    Will hold tensors and metadata once parsed.
    """
    data: Optional[Any] = None  # Tensor or array
    timestamp: Optional[str] = None
    metadata: Optional[Metadata] = None
    geolocation: Optional[Dict[str, Any]] = None
    quality_mask: Optional[Any] = None
