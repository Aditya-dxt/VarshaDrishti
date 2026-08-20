from typing import Dict, Any

class SpatialCropper:
    """Configurable spatial cropping interface."""
    
    def __init__(self, roi: Dict[str, float]):
        """
        roi dictionary expecting:
        - min_lat
        - max_lat
        - min_lon
        - max_lon
        """
        self.roi = roi

    def crop(self, frame: Any) -> Any:
        """
        Applies spatial crop based on ROI.
        Implementation depends on the geolocation grid in the real HDF5 file.
        """
        if not self.roi or not all(k in self.roi for k in ["min_lat", "max_lat", "min_lon", "max_lon"]):
            raise ValueError("Invalid or unconfigured ROI.")
            
        if self.roi["min_lat"] is None:
             raise ValueError("ROI bounds are not configured. Cannot crop.")

        # Placeholder for real cropping logic
        raise NotImplementedError("Cropping logic depends on actual geolocation arrays.")
