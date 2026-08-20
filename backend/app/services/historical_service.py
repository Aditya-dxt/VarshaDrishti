from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.config import Settings
from app.schemas.historical import HistoricalEventResponse, HistoricalListResponse
from app.services.artifact_reader import read_json_artifact
from app.services.errors import ArtifactMalformed, ArtifactNotFound


class HistoricalService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def _records(self) -> list[dict[str, Any]]:
        raw = read_json_artifact(self._settings.historical_events_path, "Historical events")
        records = raw.get("events") if isinstance(raw, dict) else raw
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            raise ArtifactMalformed("Historical-events artifact must be a list or an object with an events list.")
        return records

    def list_events(self) -> HistoricalListResponse:
        try:
            events = [record.get("event", record) for record in self._records()]
            return HistoricalListResponse(events=events)
        except ValidationError as exc:
            raise ArtifactMalformed("Historical-events artifact contains an invalid event.") from exc

    def get_event(self, event_id: str) -> HistoricalEventResponse:
        for record in self._records():
            if record.get("event", {}).get("id") == event_id:
                try:
                    return HistoricalEventResponse.model_validate(record)
                except ValidationError as exc:
                    raise ArtifactMalformed("Historical event does not satisfy the API contract.") from exc
        raise ArtifactNotFound(f"Historical event '{event_id}' was not found.")
