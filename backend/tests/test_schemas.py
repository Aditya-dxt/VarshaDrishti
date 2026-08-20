from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.prediction import PredictionResponse


def response_payload() -> dict:
    return {
        "prediction": {"class_id": 3, "label": "high_impact", "confidence": 0.7},
        "probabilities": {"no_rain": 0.1, "moderate": 0.1, "heavy": 0.1, "high_impact": 0.7},
        "xai": {"gradcam": None, "shap": None},
        "metadata": {"timestamp": datetime.now(timezone.utc), "latitude": 26.8, "longitude": 80.9},
    }


def test_prediction_contract_accepts_valid_output() -> None:
    assert PredictionResponse.model_validate(response_payload()).prediction.label == "high_impact"


def test_probabilities_must_sum_to_one() -> None:
    payload = response_payload()
    payload["probabilities"]["high_impact"] = 0.2
    with pytest.raises(ValidationError):
        PredictionResponse.model_validate(payload)


def test_timestamp_requires_timezone() -> None:
    payload = response_payload()
    payload["metadata"]["timestamp"] = "2026-08-20T12:00:00"
    with pytest.raises(ValidationError):
        PredictionResponse.model_validate(payload)
