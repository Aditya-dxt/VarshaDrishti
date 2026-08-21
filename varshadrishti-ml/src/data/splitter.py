from typing import List, Tuple, Any, Dict, Iterable, Set

def split_by_time(
    samples: List[Any], 
    train_ratio: float = 0.7, 
    val_ratio: float = 0.15, 
    test_ratio: float = 0.15
) -> Tuple[List[Any], List[Any], List[Any]]:
    """
    Splits data chronologically to prevent temporal leakage.
    Earlier data -> Train
    Later data -> Validation
    Latest data -> Test
    """
    if not samples:
        return [], [], []
        
    total_ratio = train_ratio + val_ratio + test_ratio
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")

    n = len(samples)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    # Note: Assumes samples are already chronologically sorted.
    # The actual implementation should verify timestamps.
    
    train_split = samples[:train_end]
    val_split = samples[train_end:val_end]
    test_split = samples[val_end:]

    return train_split, val_split, test_split


def _event_ids(samples: List[Dict[str, Any]]) -> Set[Any]:
    ids = set()
    for sample in samples:
        if "temporal_sequence_id" not in sample:
            raise KeyError("Each sample must include temporal_sequence_id for an event-level split.")
        ids.add(sample["temporal_sequence_id"])
    return ids


def split_by_temporal_event(
    samples: List[Dict[str, Any]],
    train_event_ids: Iterable[Any],
    val_event_ids: Iterable[Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split samples by independent temporal event id.

    This is the leakage-safe split for VarshaDrishti development runs.
    Do NOT randomly split spatial patches from the same weather event.
    """
    if not samples:
        return [], []

    train_ids = set(train_event_ids)
    val_ids = set(val_event_ids)
    overlap = train_ids & val_ids
    if overlap:
        raise ValueError(
            f"Event leakage in split definition: event ids {sorted(overlap)} "
            "were assigned to both train and validation."
        )

    train_split = [s for s in samples if s["temporal_sequence_id"] in train_ids]
    val_split = [s for s in samples if s["temporal_sequence_id"] in val_ids]

    if not train_split:
        raise ValueError(f"No training samples found for event ids {sorted(train_ids)}.")
    if not val_split:
        raise ValueError(f"No validation samples found for event ids {sorted(val_ids)}.")

    train_events = _event_ids(train_split)
    val_events = _event_ids(val_split)
    leaked = train_events & val_events
    if leaked:
        raise RuntimeError(
            f"Event leakage detected after split: {sorted(leaked)} occur in both sets."
        )
    if not train_events.isdisjoint(val_ids) or not val_events.isdisjoint(train_ids):
        raise RuntimeError("Event leakage detected: a temporal_sequence_id crossed the split.")

    return train_split, val_split
