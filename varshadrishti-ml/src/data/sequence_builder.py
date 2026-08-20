from typing import List, Optional
from .metadata import SatelliteFrame

def build_sequences(frames: List[SatelliteFrame], sequence_length: Optional[int]) -> List[List[SatelliteFrame]]:
    """
    Builds chronologically ordered sequences of satellite frames.
    """
    if sequence_length is None:
        raise ValueError("Sequence length is not yet configured.")
        
    if not frames:
        return []
        
    if len(frames) < sequence_length:
        return [] # Not enough frames for a single sequence

    # Placeholder: The actual implementation will need to verify
    # exact chronological spacing, handle missing intervals, etc.
    raise NotImplementedError("Sequence building requires real parsed timestamps and validation.")
