from fastapi import APIRouter, Depends

from app.dependencies import get_historical_service
from app.schemas.historical import HistoricalEventResponse, HistoricalListResponse
from app.services.historical_service import HistoricalService

router = APIRouter(tags=["historical"])


@router.get("/historical", response_model=HistoricalListResponse)
def historical_list(service: HistoricalService = Depends(get_historical_service)) -> HistoricalListResponse:
    return service.list_events()


@router.get("/historical/{event_id}", response_model=HistoricalEventResponse)
def historical_event(event_id: str, service: HistoricalService = Depends(get_historical_service)) -> HistoricalEventResponse:
    return service.get_event(event_id)
