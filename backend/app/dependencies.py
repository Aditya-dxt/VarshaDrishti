from __future__ import annotations

from functools import lru_cache

from app.adapters.model_adapter import ModelAdapter
from app.config import get_settings
from app.services.historical_service import HistoricalService
from app.services.metrics_service import MetricsService
from app.services.prediction_service import PredictionService


@lru_cache
def get_prediction_service() -> PredictionService:
    return PredictionService(ModelAdapter(get_settings()))


@lru_cache
def get_metrics_service() -> MetricsService:
    return MetricsService(get_settings())


@lru_cache
def get_historical_service() -> HistoricalService:
    return HistoricalService(get_settings())
