from fastapi import APIRouter, Body, Depends

from app.dependencies import get_prediction_service
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["predictions"])


@router.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest | None = Body(default=None),
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    return service.predict(payload or PredictionRequest())


@router.get("/latest", response_model=PredictionResponse)
def latest(service: PredictionService = Depends(get_prediction_service)) -> PredictionResponse:
    return service.latest()
