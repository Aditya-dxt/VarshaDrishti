from typing import List, Dict, Any
from sklearn.metrics import confusion_matrix as sk_confusion_matrix

CLASS_NAMES = ["no_rain", "moderate", "heavy", "high_impact"]


def compute_confusion_matrix(
    labels: List[int],
    predictions: List[int],
) -> Dict[str, Any]:
    """
    Computes the confusion matrix and returns a JSON-serializable structure.
    Class order is fixed: no_rain, moderate, heavy, high_impact.
    """
    if not labels or not predictions:
        raise ValueError("Labels and predictions must not be empty.")

    matrix = sk_confusion_matrix(labels, predictions, labels=list(range(len(CLASS_NAMES))))

    return {
        "class_names": CLASS_NAMES,
        "matrix": matrix.tolist(),  # 2D list for JSON serialization
    }
