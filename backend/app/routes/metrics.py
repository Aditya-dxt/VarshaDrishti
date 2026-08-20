from fastapi import APIRouter, Depends

from app.dependencies import get_metrics_service
from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=MetricsResponse)
def metrics(service: MetricsService = Depends(get_metrics_service)) -> MetricsResponse:
    return service.get_metrics()
