from __future__ import annotations

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
        try:
            return MetricsResponse.model_validate(raw)
        except ValidationError as exc:
            raise ArtifactMalformed("Metrics artifact does not satisfy the API contract.") from exc
