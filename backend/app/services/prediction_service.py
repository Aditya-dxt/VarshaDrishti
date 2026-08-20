from __future__ import annotations

from app.adapters.model_adapter import ModelAdapter
from app.schemas.prediction import PredictionRequest, PredictionResponse


class PredictionService:
    def __init__(self, adapter: ModelAdapter):
        self._adapter = adapter

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        return self._adapter.predict(request.observation)

    def latest(self) -> PredictionResponse:
        """Ask the real predictor for its current/latest available observation."""
        return self._adapter.predict(None)
