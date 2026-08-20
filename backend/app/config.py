from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Routes never expose configured file paths."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BHOOMIDRISHTI_", extra="ignore")

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    predictor_class: str | None = None
    predictor_kwargs: dict[str, object] = Field(default_factory=dict)
    metrics_path: Path | None = None
    historical_events_path: Path | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
