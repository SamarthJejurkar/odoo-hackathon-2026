"""
Asset - the central entity of the whole system.

LIFECYCLE: available -> allocated/reserved/under_maintenance -> available
                      -> lost / retired / disposed (terminal states)
`status` here is the CURRENT state only. Every transition is additionally
written to AssetStatusHistory (append-only) so "how did this asset end up
Lost" is always answerable - this is the ERP philosophy from the brief:
never lose business history, every event traceable.

Legal transitions are validated in AssetLifecycleService, not the DB,
because the rule set is genuinely business logic (e.g. "Retired" and
"Disposed" are terminal; "Lost" can only be reached via a closed audit
cycle). The DB's job is to guarantee status is always one of the seven
valid values (via the enum type) and that every change is logged (via
a service-layer transaction, not a trigger - keeping logic visible in
Python rather than hidden in the database).

SEARCH FIELDS: asset_tag, serial_number, qr_code_value are all indexed
individually since Screen 4 requires search/filter by each independently.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import AssetConditionEnum, AssetStatusEnum
from models.mixins import TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"
    __table_args__ = (
        Index("ix_assets_status", "status"),
        Index("ix_assets_category_id", "category_id"),
        Index("ix_assets_department_id", "department_id"),
        Index("ix_assets_location", "location"),
        # Composite index supporting the common "bookable + available" filter
        # used by the Resource Booking screen's resource picker.
        Index("ix_assets_bookable_status", "is_bookable", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Human-facing identifiers - auto-generated (e.g. AF-0001), but stored
    # as real columns (not derived at query time) so they're searchable
    # and stable even if the generation sequence logic changes later.
    asset_tag: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    qr_code_value: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    acquisition_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # NUMERIC, never FLOAT, for money - avoids binary floating point drift.
    # Explicitly "kept for ranking/reports only, not linked to accounting"
    # per the brief, so no FK into any ledger/invoice concept.
    acquisition_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    condition: Mapped[AssetConditionEnum] = mapped_column(
        PgEnum(AssetConditionEnum, name="asset_condition_enum", native_enum=True),
        default=AssetConditionEnum.NEW,
        nullable=False,
    )
    status: Mapped[AssetStatusEnum] = mapped_column(
        PgEnum(AssetStatusEnum, name="asset_status_enum", native_enum=True),
        default=AssetStatusEnum.AVAILABLE,
        nullable=False,
    )
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    is_bookable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    documents: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)  # list of {name, url}
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --- relationships ---
    category: Mapped["AssetCategory"] = relationship(back_populates="assets")
    department: Mapped[Optional["Department"]] = relationship(back_populates="assets")
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        back_populates="asset", order_by="AssetAllocation.allocated_at.desc()"
    )
    transfer_requests: Mapped[list["AssetTransferRequest"]] = relationship(back_populates="asset")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="asset")
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(back_populates="asset")
    status_history: Mapped[list["AssetStatusHistory"]] = relationship(
        back_populates="asset", order_by="AssetStatusHistory.changed_at.desc()"
    )
    audit_items: Mapped[list["AuditItem"]] = relationship(back_populates="asset")

    def __repr__(self) -> str:
        return f"<Asset id={self.id} tag={self.asset_tag!r} status={self.status}>"


class AssetStatusHistory(Base, TimestampMixin):
    """Append-only log of every lifecycle transition.

    Distinct from ActivityLog: this table is asset-lifecycle-specific and
    queried heavily (per-asset history tab on Screen 4), so it gets its
    own indexed table rather than being filtered out of the generic,
    much larger activity_logs table on every page load.
    """
    __tablename__ = "asset_status_history"
    __table_args__ = (Index("ix_asset_status_history_asset_id", "asset_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[Optional[AssetStatusEnum]] = mapped_column(
        PgEnum(AssetStatusEnum, name="asset_status_enum", native_enum=True, create_type=False),
        nullable=True,
    )
    to_status: Mapped[AssetStatusEnum] = mapped_column(
        PgEnum(AssetStatusEnum, name="asset_status_enum", native_enum=True, create_type=False),
        nullable=False,
    )
    changed_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    asset: Mapped["Asset"] = relationship(back_populates="status_history")
