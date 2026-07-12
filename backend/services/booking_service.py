"""
Business logic for Booking.

Overlap is enforced by Postgres (ex_no_overlapping_bookings, EXCLUDE
USING gist over asset_id + tstzrange(start_time, end_time, '[)')) —
same TOCTOU-safe pattern as AssetAllocation's partial unique index.
We attempt the insert and catch IntegrityError; we specifically check
that the failure came from the exclusion constraint (not some other
integrity error) before treating it as a booking conflict, then try to
suggest the next available slot of equal duration.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from models.asset import Asset
from models.booking import Booking
from models.enums import AssetStatusEnum, BookingStatusEnum, RoleEnum
from models.user import User
from repositories.booking_repository import BookingRepository
from schemas.booking import BookingConflictDetail, BookingCreate, SuggestedSlot

_EXCLUSION_CONSTRAINT_NAME = "ex_no_overlapping_bookings"


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BookingRepository(db)

    def create_booking(self, payload: BookingCreate, actor: User) -> Booking:
        asset = self.db.get(Asset, payload.asset_id)
        if asset is None:
            raise NotFoundException(f"Asset {payload.asset_id} not found.")
        if not asset.is_bookable:
            raise ValidationException(f"Asset {asset.asset_tag} is not a bookable resource.")
        if asset.status != AssetStatusEnum.AVAILABLE:
            raise ValidationException(
                f"Asset {asset.asset_tag} is '{asset.status.value}' and cannot be booked right now."
            )

        booking = Booking(
            asset_id=payload.asset_id,
            booked_by_id=actor.id,
            department_id=payload.department_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            purpose=payload.purpose,
            status=BookingStatusEnum.UPCOMING,
        )

        try:
            self.repo.create(booking)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            if _EXCLUSION_CONSTRAINT_NAME not in str(exc.orig):
                # Some other integrity failure (e.g. FK) — don't mask it as a booking conflict.
                raise ValidationException("Could not create booking due to a data integrity error.")

            duration = payload.end_time - payload.start_time
            suggestion = self._suggest_next_slot(payload.asset_id, payload.start_time, duration)
            detail = BookingConflictDetail(
                asset_id=payload.asset_id,
                requested_start=payload.start_time,
                requested_end=payload.end_time,
                suggested_slot=suggestion,
            )
            raise ConflictException(
                f"Asset {asset.asset_tag} is already booked for an overlapping time slot.",
                detail=detail.model_dump(),
            )

        self.db.refresh(booking)
        return booking

    def _suggest_next_slot(
        self, asset_id: int, desired_start: datetime, duration: timedelta
    ) -> Optional[SuggestedSlot]:
        """Walk existing non-cancelled bookings in time order and return the
        first gap >= duration, starting no earlier than now or desired_start
        (whichever is later)."""
        now = datetime.now(timezone.utc)
        search_from = max(desired_start, now)

        upcoming = self.repo.list_active_from(asset_id, search_from)
        cursor = search_from

        for booking in upcoming:
            if booking.start_time - cursor >= duration:
                return SuggestedSlot(asset_id=asset_id, start_time=cursor, end_time=cursor + duration)
            cursor = max(cursor, booking.end_time)

        # No conflicting booking after the last one found — free from cursor onward.
        return SuggestedSlot(asset_id=asset_id, start_time=cursor, end_time=cursor + duration)

    def suggest_slot(self, asset_id: int, desired_start: datetime, duration_minutes: int) -> SuggestedSlot:
        asset = self.db.get(Asset, asset_id)
        if asset is None:
            raise NotFoundException(f"Asset {asset_id} not found.")
        suggestion = self._suggest_next_slot(asset_id, desired_start, timedelta(minutes=duration_minutes))
        return suggestion

    def cancel_booking(self, booking_id: int, reason: str, actor: User) -> Booking:
        booking = self.repo.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(f"Booking {booking_id} not found.")

        is_owner = booking.booked_by_id == actor.id
        is_manager = actor.role in (RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)
        if not (is_owner or is_manager):
            raise ForbiddenException("Only the booker or an Asset Manager/Admin can cancel this booking.")

        if booking.status == BookingStatusEnum.CANCELLED:
            raise ConflictException(f"Booking {booking_id} is already cancelled.")

        now = datetime.now(timezone.utc)
        if booking.end_time <= now:
            raise ValidationException("Cannot cancel a booking that has already ended.")

        self.repo.cancel(booking, reason)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_booking(self, booking_id: int) -> Booking:
        booking = self.repo.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(f"Booking {booking_id} not found.")
        return booking

    def list_bookings(
        self,
        asset_id: Optional[int] = None,
        booked_by_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[BookingStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Booking]:
        return self.repo.list_filtered(asset_id, booked_by_id, department_id, status, skip, limit)