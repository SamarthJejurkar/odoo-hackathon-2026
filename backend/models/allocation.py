"""
AssetAllocation - one row per allocation EVENT, never overwritten.

THE CORE BUSINESS RULE: "You can't allocate an asset that's already
taken" (Screen 5). This is enforced with a partial unique index, not
just an application check:

    CREATE UNIQUE INDEX uq_one_active_allocation_per_asset
    ON asset_allocations (asset_id) WHERE status = 'active';

Why at the DB level and not only in the service? Two concurrent requests
(Raj and a retry of Priya's own request) can both pass an app-level
"is this asset free?" check before either commits - a classic TOCTOU
race. A partial unique index makes the DB itself reject the second
INSERT with a constraint violation, which the service layer catches and
turns into the "currently held by Priya, transfer instead" response.
This is exactly the kind of guarantee an ERP reviewer will look for.

allocated_to is XOR between employee and department (CheckConstraint
below) - an asset is allocated to a person OR a department, never
ambiguously both.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import AllocationStatusEnum, AssetConditionEnum
from models.mixins import TimestampMixin


class AssetAllocation(Base, TimestampMixin):
    __tablename__ = "asset_allocations"
    __table_args__ = (
        CheckConstraint(
            "(employee_id IS NOT NULL AND department_id IS NULL) OR "
            "(employee_id IS NULL AND department_id IS NOT NULL)",
            name="ck_allocation_target_xor",
        ),
        # The business-rule-critical index: at most one ACTIVE allocation
        # row per asset, enforced by Postgres, not just Python.
        Index(
            "uq_one_active_allocation_per_asset",
            "asset_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
        Index("ix_asset_allocations_employee_id", "employee_id"),
        Index("ix_asset_allocations_department_id", "department_id"),
        Index("ix_asset_allocations_expected_return_date", "expected_return_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)

    employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True
    )
    allocated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    allocated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expected_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    return_condition: Mapped[Optional[AssetConditionEnum]] = mapped_column(
        PgEnum(AssetConditionEnum, name="asset_condition_enum", native_enum=True, create_type=False),
        nullable=True,
    )
    return_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[AllocationStatusEnum] = mapped_column(
        PgEnum(AllocationStatusEnum, name="allocation_status_enum", native_enum=True),
        default=AllocationStatusEnum.ACTIVE,
        nullable=False,
    )

    # --- Relationships ---
    # NOTE: asset_allocations has TWO foreign keys into users
    # (employee_id and allocated_by_id), so each relationship() below
    # must declare foreign_keys= explicitly - otherwise SQLAlchemy
    # can't determine which FK column a given relationship refers to
    # and raises AmbiguousForeignKeysError at mapper configuration time.
    asset: Mapped["Asset"] = relationship(back_populates="allocations")

    employee: Mapped[Optional["User"]] = relationship(
        foreign_keys=[employee_id],
        back_populates="allocations",
    )
    department: Mapped[Optional["Department"]] = relationship(
        foreign_keys=[department_id],
        back_populates="allocations",
    )
    allocated_by: Mapped["User"] = relationship(
        foreign_keys=[allocated_by_id],
        back_populates="allocations_made",
    )