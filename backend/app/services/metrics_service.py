import os
from datetime import datetime, timezone

from pydantic import ValidationError

from app.config import Settings
from app.schemas.metrics import MetricsResponse
from app.services.artifact_reader import read_json_artifact
from app.services.errors import ArtifactMalformed


class MetricsService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def get_metrics(self) -> MetricsResponse:
        raw = read_json_artifact(self._settings.metrics_path, "Metrics")

        mtime = os.path.getmtime(self._settings.metrics_path) if self._settings.metrics_path else 0
        evaluated_at = datetime.fromtimestamp(mtime, tz=timezone.utc)

        payload = {
            "overall": {
                "accuracy": raw["metrics"]["accuracy"],
                "f1": raw["metrics"]["macro_f1"],
            },
            "per_class": raw["metrics"]["classes"],
            "confusion_matrix": {
                "labels": raw["confusion_matrix"]["class_names"],
                "matrix": raw["confusion_matrix"]["matrix"],
            },
            "evaluation_set": "Held-out Validation Event (18 Aug 2026)",
            "evaluated_at": evaluated_at.isoformat(),
        }

        try:
            return MetricsResponse.model_validate(payload)
        except ValidationError as exc:
            raise ArtifactMalformed("Metrics artifact does not satisfy the API contract.") from exc
