"""
Raw DB access only. The overlap guarantee lives entirely in Postgres
(ex_no_overlapping_bookings, EXCLUDE USING gist) — this layer just
flush()es and lets IntegrityError surface to the service.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.booking import Booking
from models.enums import BookingStatusEnum


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.flush()  # surfaces ExclusionViolation here, before commit
        return booking

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        return self.db.get(Booking, booking_id)

    def list_filtered(
        self,
        asset_id: Optional[int] = None,
        booked_by_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[BookingStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Booking]:
        stmt = select(Booking)
        if asset_id is not None:
            stmt = stmt.where(Booking.asset_id == asset_id)
        if booked_by_id is not None:
            stmt = stmt.where(Booking.booked_by_id == booked_by_id)
        if department_id is not None:
            stmt = stmt.where(Booking.department_id == department_id)
        if status is not None:
            stmt = stmt.where(Booking.status == status)
        stmt = stmt.order_by(Booking.start_time.asc()).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def list_active_from(self, asset_id: int, from_time: datetime) -> Sequence[Booking]:
        """Non-cancelled bookings for an asset that end after from_time,
        ordered by start_time — used for gap-finding in slot suggestion."""
        stmt = (
            select(Booking)
            .where(
                Booking.asset_id == asset_id,
                Booking.status != BookingStatusEnum.CANCELLED,
                Booking.end_time > from_time,
            )
            .order_by(Booking.start_time.asc())
        )
        return self.db.execute(stmt).scalars().all()

    def cancel(self, booking: Booking, reason: str) -> Booking:
        booking.status = BookingStatusEnum.CANCELLED
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = reason
        self.db.flush()
        return booking