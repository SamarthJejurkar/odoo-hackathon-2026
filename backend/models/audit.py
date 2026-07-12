"""
Audit cycles - structured verification, not a single form (Screen 8).

Three tables model three distinct concerns:
  AuditCycle          - the cycle itself: scope, date range, status
  AuditCycleAuditor    - who is assigned to run it (many-to-many, cycle<->user)
  AuditItem            - one row per asset-in-scope, holding the verification
                         outcome. This is the actual discrepancy data.

AuditItem gets a unique(audit_cycle_id, asset_id) constraint so an asset
can't accidentally be double-verified within the same cycle, and a
verification_status of MISSING/DAMAGED is exactly what a "discrepancy
report" query filters for - it's a live query, not a generated document.

Closing a cycle (status -> CLOSED) is a service-layer operation that:
  1. Locks the cycle (blocks further AuditItem writes - enforced in
     service, since "an audit item cannot be created/edited after its
     parent cycle is closed" is a temporal business rule, not a
     structural one a FK/check constraint can express cleanly).
  2. For each MISSING item, transitions the asset to LOST and writes
     an AssetStatusHistory row citing the audit cycle as the reason.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import AuditCycleStatusEnum, AuditItemStatusEnum
from models.mixins import TimestampMixin


class AuditCycle(Base, TimestampMixin):
    __tablename__ = "audit_cycles"
    __table_args__ = (Index("ix_audit_cycles_status", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    scope_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    scope_location: Mapped[Optional[str]] = mapped_column(nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[AuditCycleStatusEnum] = mapped_column(
        PgEnum(AuditCycleStatusEnum, name="audit_cycle_status_enum", native_enum=True),
        default=AuditCycleStatusEnum.PLANNED,
        nullable=False,
    )
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    auditors: Mapped[list["AuditCycleAuditor"]] = relationship(back_populates="audit_cycle")
    items: Mapped[list["AuditItem"]] = relationship(back_populates="audit_cycle")


class AuditCycleAuditor(Base, TimestampMixin):
    """Many-to-many: an audit cycle can have several auditors assigned."""
    __tablename__ = "audit_cycle_auditors"
    __table_args__ = (
        UniqueConstraint("audit_cycle_id", "auditor_id", name="uq_audit_cycle_auditor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    audit_cycle_id: Mapped[int] = mapped_column(
        ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False
    )
    auditor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    audit_cycle: Mapped["AuditCycle"] = relationship(back_populates="auditors")


class AuditItem(Base, TimestampMixin):
    __tablename__ = "audit_items"
    __table_args__ = (
        UniqueConstraint("audit_cycle_id", "asset_id", name="uq_audit_item_cycle_asset"),
        Index("ix_audit_items_verification_status", "verification_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    audit_cycle_id: Mapped[int] = mapped_column(
        ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    verified_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    verification_status: Mapped[AuditItemStatusEnum] = mapped_column(
        PgEnum(AuditItemStatusEnum, name="audit_item_status_enum", native_enum=True),
        default=AuditItemStatusEnum.PENDING,
        nullable=False,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    audit_cycle: Mapped["AuditCycle"] = relationship(back_populates="items")
    asset: Mapped["Asset"] = relationship(back_populates="audit_items")
