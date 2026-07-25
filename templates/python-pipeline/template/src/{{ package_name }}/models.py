"""Validated contracts at pipeline boundaries."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str = Field(min_length=1)
    occurred_at: datetime
    value: Decimal = Field(ge=0)


class DailyTotal(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_date: date
    event_count: int = Field(ge=0)
    total_value: Decimal = Field(ge=0)
