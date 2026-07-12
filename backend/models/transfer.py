"""
AssetTransferRequest - implements the workflow:

    Employee -> Requested -> Dept Head Approval -> Asset Manager Approval
             -> Transfer -> History Update

Each approval stage gets its own (approver_id, approved_at) pair rather
than a single "approved_by" column, because the brief requires BOTH
approvals to be individually traceable (who approved as dept head vs.
who approved as asset manager may be different people, at different
times, and either can reject). Collapsing this into one pair of columns
would silently lose half the audit trail.

On completion, the service layer closes the current AssetAllocation
(status=returned) and opens a new one - the transfer request itself
does NOT hold allocation state, keeping it a pure workflow/approval
record that references, but doesn't duplicate, allocation data.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import TransferStatusEnum
from models.mixins import TimestampMixin


class AssetTransferRequest(Base, TimestampMixin):
    __tablename__ = "asset_transfer_requests"
    __table_args__ = (
        Index("ix_asset_transfer_requests_asset_id", "asset_id"),
        Index("ix_asset_transfer_requests_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    current_allocation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("asset_allocations.id", ondelete="SET NULL"), nullable=True
    )

    requested_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    requested_to_employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    requested_to_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[TransferStatusEnum] = mapped_column(
        PgEnum(TransferStatusEnum, name="transfer_status_enum", native_enum=True),
        default=TransferStatusEnum.REQUESTED,
        nullable=False,
    )

    dept_head_approved_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    dept_head_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    asset_manager_approved_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    asset_manager_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- relationships ---
    asset: Mapped["Asset"] = relationship(back_populates="transfer_requests")

    current_allocation: Mapped[Optional["AssetAllocation"]] = relationship(
        foreign_keys=[current_allocation_id]
    )

    # This table has FOUR foreign keys into users (requested_by,
    # requested_to_employee, dept_head_approved_by,
    # asset_manager_approved_by) plus one into departments
    # (requested_to_department). Each relationship below is
    # disambiguated with foreign_keys= for the same reason
    # AssetAllocation needed it - without it, any future call site
    # that touches these attributes hits AmbiguousForeignKeysError.
    # No back_populates is declared (one-directional, viewonly access
    # from the transfer side only) to avoid requiring matching
    # collection attributes on User/Department - same pattern as
    # Department.head already uses.
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id]
    )
    requested_to_employee: Mapped[Optional["User"]] = relationship(
        foreign_keys=[requested_to_employee_id]
    )
    requested_to_department: Mapped[Optional["Department"]] = relationship(
        foreign_keys=[requested_to_department_id]
    )
    dept_head_approver: Mapped[Optional["User"]] = relationship(
        foreign_keys=[dept_head_approved_by_id]
    )
    asset_manager_approver: Mapped[Optional["User"]] = relationship(
        foreign_keys=[asset_manager_approved_by_id]
    )

    def __repr__(self) -> str:
        return f"<AssetTransferRequest id={self.id} asset_id={self.asset_id} status={self.status}>"