"""The sole boundary for integrating Person 1's predictor implementation."""
from __future__ import annotations

from importlib import import_module
from typing import Any, Mapping, Protocol

from pydantic import ValidationError

from app.config import Settings
from app.schemas.prediction import LABEL_BY_CLASS_ID, PredictionResponse
from app.services.errors import ModelOutputInvalid, ModelUnavailable


class RainPredictor(Protocol):
    def predict(self, observation: Mapping[str, Any] | None) -> Mapping[str, Any]: ...


class ModelAdapter:
    """Loads one configured predictor and converts its public output to the API contract."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._predictor: RainPredictor | None = None

    def _get_predictor(self) -> RainPredictor:
        if self._predictor is not None:
            return self._predictor
        target = self._settings.predictor_class
        if not target:
            raise ModelUnavailable("No predictor is configured. Set BHOOMIDRISHTI_PREDICTOR_CLASS.")
        try:
            module_name, class_name = target.split(":", 1)
            candidate = getattr(import_module(module_name), class_name)(**self._settings.predictor_kwargs)
        except (ValueError, ImportError, AttributeError, TypeError) as exc:
            raise ModelUnavailable("Configured RainPredictor could not be loaded.") from exc
        if not callable(getattr(candidate, "predict", None)):
            raise ModelUnavailable("Configured predictor does not implement predict(observation).")
        self._predictor = candidate
        return candidate

    def predict(self, observation: Mapping[str, Any] | None) -> PredictionResponse:
        try:
            raw = self._get_predictor().predict(observation)
        except ModelUnavailable:
            raise
        except Exception as exc:
            raise ModelUnavailable("RainPredictor inference is unavailable.") from exc
        return self._to_response(raw)

    @staticmethod
    def _to_response(raw: Mapping[str, Any]) -> PredictionResponse:
        if hasattr(raw, "model_dump"):
            raw = raw.model_dump()
        if not isinstance(raw, Mapping):
            raise ModelOutputInvalid("RainPredictor returned an unsupported result.")
        result = dict(raw)
        probabilities = result.get("probabilities")
        if isinstance(probabilities, (list, tuple)) and len(probabilities) == 4:
            result["probabilities"] = dict(zip(LABEL_BY_CLASS_ID.values(), probabilities, strict=True))
        try:
            return PredictionResponse.model_validate(result)
        except ValidationError as exc:
            raise ModelOutputInvalid("RainPredictor output does not satisfy the API contract.") from exc
