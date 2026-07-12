"""
Pydantic V2 schemas for Booking.

Effective status (UPCOMING/ONGOING/COMPLETED) is computed at read time
from start_time/end_time vs now — never stored. Only UPCOMING (at
creation) and CANCELLED (explicit action) are ever written to the
status column. See BookingService docstring for why.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from models.enums import BookingStatusEnum


class BookingCreate(BaseModel):
    asset_id: int
    department_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    purpose: Optional[str] = None

    @model_validator(mode="after")
    def check_time_range(self) -> "BookingCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time.")
        now = datetime.now(timezone.utc)
        start = self.start_time if self.start_time.tzinfo else self.start_time.replace(tzinfo=timezone.utc)
        if start < now:
            raise ValueError("start_time cannot be in the past.")
        return self


class BookingCancel(BaseModel):
    cancellation_reason: str


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    booked_by_id: int
    department_id: Optional[int]
    start_time: datetime
    end_time: datetime
    purpose: Optional[str]
    status: BookingStatusEnum
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[misc]
    @property
    def effective_status(self) -> BookingStatusEnum:
        if self.status == BookingStatusEnum.CANCELLED:
            return BookingStatusEnum.CANCELLED
        now = datetime.now(timezone.utc)
        if now < self.start_time:
            return BookingStatusEnum.UPCOMING
        if self.start_time <= now < self.end_time:
            return BookingStatusEnum.ONGOING
        return BookingStatusEnum.COMPLETED


class SuggestedSlot(BaseModel):
    asset_id: int
    start_time: datetime
    end_time: datetime


class BookingConflictDetail(BaseModel):
    """409 detail payload — includes a suggested next-available slot when one could be found."""
    asset_id: int
    requested_start: datetime
    requested_end: datetime
    suggested_slot: Optional[SuggestedSlot] = None