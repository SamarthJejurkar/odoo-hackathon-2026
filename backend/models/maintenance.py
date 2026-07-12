"""
MaintenanceRequest - implements:
    Pending -> Approved/Rejected -> Technician Assigned -> In Progress -> Resolved

Each stage timestamp is nullable and only populated as the workflow
advances - the row IS the audit trail for this request, so there's no
need for a separate maintenance_status_history table (unlike Asset,
which has many concurrent concerns writing to its status). One
maintenance request has exactly one linear history, one owner.

The asset's status flips to UNDER_MAINTENANCE on approval and back to
AVAILABLE on resolution - that transition is executed by
MaintenanceService inside the same DB transaction as the status update
here, and is what populates AssetStatusHistory.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import MaintenancePriorityEnum, MaintenanceStatusEnum
from models.mixins import TimestampMixin


class MaintenanceRequest(Base, TimestampMixin):
    __tablename__ = "maintenance_requests"
    __table_args__ = (
        Index("ix_maintenance_requests_asset_id", "asset_id"),
        Index("ix_maintenance_requests_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    raised_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[MaintenancePriorityEnum] = mapped_column(
        PgEnum(MaintenancePriorityEnum, name="maintenance_priority_enum", native_enum=True),
        default=MaintenancePriorityEnum.MEDIUM,
        nullable=False,
    )
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[MaintenanceStatusEnum] = mapped_column(
        PgEnum(MaintenanceStatusEnum, name="maintenance_status_enum", native_enum=True),
        default=MaintenanceStatusEnum.PENDING,
        nullable=False,
    )

    approved_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    technician_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="maintenance_requests")
