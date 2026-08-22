from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from .prediction import RiskLabel


class ClassMetrics(BaseModel):
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    f1: float = Field(ge=0, le=1)
    support: int | None = None


class OverallMetrics(BaseModel):
    accuracy: float = Field(ge=0, le=1)
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    roc_auc: float | None = None


class ConfusionMatrix(BaseModel):
    labels: list[RiskLabel] = Field(min_length=1)
    matrix: list[list[int]] = Field(min_length=1)

    @field_validator("matrix")
    @classmethod
    def square_non_negative(cls, matrix: list[list[int]]) -> list[list[int]]:
        if any(len(row) != len(matrix) or any(value < 0 for value in row) for row in matrix):
            raise ValueError("matrix must be square and contain non-negative counts")
        return matrix


class MetricsResponse(BaseModel):
    overall: OverallMetrics
    per_class: dict[RiskLabel, ClassMetrics]
    confusion_matrix: ConfusionMatrix
    evaluation_set: str = Field(min_length=1)
    evaluated_at: datetime

    @model_validator(mode="after")
    def require_all_classes(self) -> "MetricsResponse":
        if set(self.per_class) != {"no_rain", "moderate", "heavy", "high_impact"}:
            raise ValueError("per_class must contain each risk class exactly once")
        return self

    @field_validator("evaluated_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("evaluated_at must include a timezone offset")
        return value
