from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from .prediction import PredictionResponse, RiskLabel


class HistoricalEvent(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    date: date
    location: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    type: RiskLabel
    description: str | None = None


class HistoricalListResponse(BaseModel):
    events: list[HistoricalEvent]


class HistoricalEventResponse(PredictionResponse):
    event: HistoricalEvent
