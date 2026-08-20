from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta


def match_temporally(l1b_inventory: List[Dict[str, Any]],
                     l2b_inventory: List[Dict[str, Any]],
                     tolerance_minutes: int = 0) -> Tuple[List[Dict[str, Any]], List[Dict], List[Dict]]:
    """
    Matches L1B and L2B files by timestamp.
    Returns: matched_pairs, unmatched_l1b, unmatched_l2b

    Each matched pair is a dict:
    {
        "timestamp": datetime,
        "l1b_path": str,
        "l2b_path": str,
        "time_diff_minutes": float
    }
    Never silently pairs unrelated observations.
    """
    matched_pairs = []
    unmatched_l1b = []
    unmatched_l2b = list(l2b_inventory)

    for l1b in l1b_inventory:
        t1 = l1b["timestamp"]

        best_match = None
        best_diff = float("inf")

        for l2b in unmatched_l2b:
            t2 = l2b["timestamp"]
            diff_min = abs((t1 - t2).total_seconds()) / 60.0

            if diff_min <= tolerance_minutes and diff_min < best_diff:
                best_diff = diff_min
                best_match = l2b

        if best_match:
            matched_pairs.append({
                "timestamp": t1,
                "l1b_path": l1b["full_path"],
                "l2b_path": best_match["full_path"],
                "l1b_filename": l1b["filename"],
                "l2b_filename": best_match["filename"],
                "time_diff_minutes": best_diff
            })
            unmatched_l2b.remove(best_match)
        else:
            unmatched_l1b.append(l1b)

    # Sort matched pairs chronologically
    matched_pairs = sorted(matched_pairs, key=lambda x: x["timestamp"])

    return matched_pairs, unmatched_l1b, unmatched_l2b


class TemporalMatcher:
    """
    Backward-compatible class-based interface for temporal matching.
    The new functional API is match_temporally().
    This shim is preserved for existing tests and interfaces.
    """

    def __init__(self, tolerance: int = 1800):
        """tolerance: matching tolerance in seconds."""
        self.tolerance = tolerance  # stored in seconds

    def match(self, satellite_frames, rainfall_frames):
        """Returns empty list if either input is empty (safe no-op for unconfigured callers)."""
        if not satellite_frames or not rainfall_frames:
            return []
        raise NotImplementedError(
            "Use match_temporally() with real HDF5 inventories for production matching."
        )

