from typing import Dict, Any

class RainfallLabelBuilder:
    """Builds rainfall severity labels from rainfall targets."""
    
    def __init__(self, thresholds: Dict[str, float] = None):
        """
        thresholds expecting:
        - no_rain
        - moderate
        - heavy
        - high_impact
        """
        self.thresholds = thresholds

    def build_label(self, rainfall_target: Any) -> int:
        """
        Calculates the label class (0 to 3) based on thresholds.
        """
        if not self.thresholds:
            raise ValueError("Rainfall thresholds are not yet configured. Need real data to determine.")
            
        if self.thresholds.get("no_rain") is None:
             raise ValueError("Rainfall thresholds are null. Need real data.")
             
        raise NotImplementedError("Label calculation requires real rainfall arrays and aggregation strategy.")
