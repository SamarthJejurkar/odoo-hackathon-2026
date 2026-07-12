"""
Booking - time-slot reservation of a shared/bookable Asset.

THE OVERLAP RULE, ENFORCED WHERE IT BELONGS: "Two people can't book the
same room at overlapping times" (Screen 6). Like the allocation rule,
checking this in the service layer alone is a race condition waiting to
happen under concurrent requests. PostgreSQL has a purpose-built feature
for exactly this: an EXCLUDE constraint over a range type + btree_gist.

    CREATE EXTENSION IF NOT EXISTS btree_gist;

    ALTER TABLE bookings ADD CONSTRAINT ex_no_overlapping_bookings
    EXCLUDE USING gist (
        asset_id WITH =,
        tstzrange(start_time, end_time, '[)') WITH &&
    ) WHERE (status != 'cancelled');

Reads as: "for the same asset_id, no two rows may have overlapping
time ranges, unless one of them is cancelled." The '[)' bound means a
slot ending at 10:00 does not overlap one starting at 10:00 - exactly
the "10:00-11:00 is fine since it starts right after" example from the
brief. This single constraint replaces a whole class of hand-written
overlap-checking SQL and closes the concurrency gap entirely.

The Python model can't express EXCLUDE natively via mapped_column, so
it's declared as a raw Constraint object in __table_args__.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import BookingStatusEnum
from models.mixins import TimestampMixin


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_booking_end_after_start"),
        ExcludeConstraint(
            ("asset_id", "="),
            (text("tstzrange(start_time, end_time, '[)')"), "&&"),
            using="gist",
            where=text("status != 'CANCELLED'"),
            name="ex_no_overlapping_bookings",
        ),
        Index("ix_bookings_asset_id", "asset_id"),
        Index("ix_bookings_booked_by_id", "booked_by_id"),
        Index("ix_bookings_start_time", "start_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    booked_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[BookingStatusEnum] = mapped_column(
        PgEnum(BookingStatusEnum, name="booking_status_enum", native_enum=True),
        default=BookingStatusEnum.UPCOMING,
        nullable=False,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="bookings")
    booked_by_user: Mapped["User"] = relationship(back_populates="bookings")

    def __repr__(self) -> str:
        return f"<Booking id={self.id} asset_id={self.asset_id} {self.start_time}..{self.end_time}>"
