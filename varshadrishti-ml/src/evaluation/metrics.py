from typing import List, Dict, Any
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

CLASS_NAMES = ["no_rain", "moderate", "heavy", "high_impact"]
NUM_CLASSES = 4


def calculate_metrics(
    labels: List[int],
    predictions: List[int],
) -> Dict[str, Any]:
    """
    Calculates full evaluation metrics.

    Uses zero_division=0 to gracefully handle classes absent from predictions.
    This must be documented clearly — a class with no predictions is NOT the
    same as a class with good performance.
    """
    if not labels or not predictions:
        raise ValueError("Labels and predictions must not be empty.")

    acc = accuracy_score(labels, predictions)
    macro_f1 = f1_score(labels, predictions, average="macro", zero_division=0)
    weighted_f1 = f1_score(labels, predictions, average="weighted", zero_division=0)

    per_class_precision = precision_score(labels, predictions, average=None, zero_division=0, labels=list(range(NUM_CLASSES)))
    per_class_recall    = recall_score(labels, predictions, average=None, zero_division=0, labels=list(range(NUM_CLASSES)))
    per_class_f1        = f1_score(labels, predictions, average=None, zero_division=0, labels=list(range(NUM_CLASSES)))

    per_class = {}
    for i, name in enumerate(CLASS_NAMES):
        per_class[name] = {
            "precision": per_class_precision[i],
            "recall":    per_class_recall[i],
            "f1":        per_class_f1[i],
        }

    return {
        "accuracy":    acc,
        "macro_f1":    macro_f1,
        "weighted_f1": weighted_f1,
        "classes":     per_class,
    }


def high_impact_metrics(metrics: Dict[str, Any]) -> Dict[str, float]:
    """Extracts the high-impact class metrics for quick inspection."""
    return metrics["classes"].get("high_impact", {})
