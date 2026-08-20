from typing import List, Dict, Any, Optional
from datetime import timedelta


def build_temporal_sequences(matched_pairs: List[Dict[str, Any]],
                             sequence_length: int = 6,
                             step_minutes: int = 30) -> List[List[Dict[str, Any]]]:
    """
    Groups chronologically ordered matched pairs into strict temporal sequences.
    A sequence is valid ONLY if it has exactly `sequence_length` consecutive
    frames separated by exactly `step_minutes`.
    No timestamps may be repeated. No interpolation of missing observations.
    """
    if not matched_pairs:
        return []

    sequences = []

    for i in range(len(matched_pairs) - sequence_length + 1):
        seq = [matched_pairs[i]]
        valid = True

        for j in range(1, sequence_length):
            curr_frame = matched_pairs[i + j]
            prev_frame = seq[-1]

            diff = (curr_frame["timestamp"] - prev_frame["timestamp"]).total_seconds() / 60.0

            if abs(diff - step_minutes) > 0.01:
                valid = False
                break

            seq.append(curr_frame)

        if valid and len(seq) == sequence_length:
            sequences.append(seq)

    return sequences


def build_sequences(frames, sequence_length: Optional[int] = None):
    """
    Backward-compatible shim.
    The new production API is build_temporal_sequences().
    This stub is preserved for existing tests and Phase-C interface contracts.
    """
    if sequence_length is None:
        raise ValueError("Sequence length is not yet configured.")

    if not frames:
        return []

    if len(frames) < sequence_length:
        return []

    raise NotImplementedError(
        "Use build_temporal_sequences() with real matched HDF5 file pairs. "
        "build_sequences() is a legacy stub."
    )

