import json
from pathlib import Path
from typing import List, Dict, Any

from src.evaluation.metrics import calculate_metrics, high_impact_metrics
from src.evaluation.confusion_matrix import compute_confusion_matrix


def generate_report(
    labels: List[int],
    predictions: List[int],
    output_dir: str = "outputs/metrics",
) -> Dict[str, Any]:
    """
    Generates a full evaluation report and saves JSON files.

    IMPORTANT: Only call this with REAL labels and predictions from
    the held-out test set after genuine model training.
    """
    metrics = calculate_metrics(labels, predictions)
    cm = compute_confusion_matrix(labels, predictions)

    report = {
        "metrics": metrics,
        "confusion_matrix": cm,
        "high_impact": high_impact_metrics(metrics),
    }

    # Save to disk
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(out_path / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

    with open(out_path / "confusion_matrix.json", "w") as f:
        json.dump(cm, f, indent=4)

    with open(out_path / "report.json", "w") as f:
        json.dump(report, f, indent=4)

    return report
