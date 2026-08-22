from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import get_metrics_service, get_prediction_service
from app.main import app
from app.schemas.prediction import PredictionResponse
from app.services.metrics_service import MetricsService
from app.services.errors import ModelUnavailable
from app.services.prediction_service import PredictionService


class RoutePredictionDouble:
    def predict(self, _):
        return PredictionResponse.model_validate({
            "prediction": {"class_id": 0, "label": "no_rain", "confidence": 1.0},
            "probabilities": {"no_rain": 1.0, "moderate": 0.0, "heavy": 0.0, "high_impact": 0.0},
            "metadata": {"timestamp": "2026-08-20T12:00:00Z", "latitude": 0, "longitude": 0},
        })

    def latest(self):
        return self.predict(None)


def test_predict_route_uses_injected_service() -> None:
    app.dependency_overrides[get_prediction_service] = lambda: RoutePredictionDouble()
    try:
        response = TestClient(app).post("/api/predict", json={})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["prediction"]["label"] == "no_rain"


def test_unconfigured_model_returns_503() -> None:
    class UnavailablePredictionService:
        def latest(self):
            raise ModelUnavailable("No predictor is configured.")

    app.dependency_overrides[get_prediction_service] = lambda: UnavailablePredictionService()
    try:
        response = TestClient(app).get("/api/latest")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["code"] == "model_unavailable"


def test_missing_metrics_artifact_returns_404() -> None:
    app.dependency_overrides[get_metrics_service] = lambda: MetricsService(Settings(metrics_path=None))
    try:
        response = TestClient(app).get("/api/metrics")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json()["code"] == "artifact_not_found"
