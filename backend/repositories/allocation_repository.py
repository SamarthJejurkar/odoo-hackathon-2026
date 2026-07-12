"""
Raw DB access only — no business rules here. The uniqueness guarantee
lives in the DB (partial unique index on status='ACTIVE'); this layer
just surfaces IntegrityError up to the service, which is the only place
that knows how to turn it into a meaningful conflict response.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.allocation import AssetAllocation
from models.enums import AllocationStatusEnum, AssetConditionEnum


class AllocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, allocation: AssetAllocation) -> AssetAllocation:
        self.db.add(allocation)
        self.db.flush()  # surfaces IntegrityError before commit, without ending the transaction
        return allocation

    def get_by_id(self, allocation_id: int) -> Optional[AssetAllocation]:
        return self.db.get(AssetAllocation, allocation_id)

    def get_active_for_asset(self, asset_id: int) -> Optional[AssetAllocation]:
        stmt = select(AssetAllocation).where(
            AssetAllocation.asset_id == asset_id,
            AssetAllocation.status == AllocationStatusEnum.ACTIVE,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_filtered(
        self,
        asset_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[AllocationStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[AssetAllocation]:
        # OVERDUE is never stored on the row (see schemas/allocation.py docstring) —
        # it's derived from ACTIVE + a past-due expected_return_date. Translate a
        # status=OVERDUE filter into that computed query instead of matching a
        # literal column value that will never exist in the DB.
        if status == AllocationStatusEnum.OVERDUE:
            return self.list_overdue(skip=skip, limit=limit)

        stmt = select(AssetAllocation)
        if asset_id is not None:
            stmt = stmt.where(AssetAllocation.asset_id == asset_id)
        if employee_id is not None:
            stmt = stmt.where(AssetAllocation.employee_id == employee_id)
        if department_id is not None:
            stmt = stmt.where(AssetAllocation.department_id == department_id)
        if status is not None:
            stmt = stmt.where(AssetAllocation.status == status)
        stmt = stmt.order_by(AssetAllocation.allocated_at.desc()).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def list_overdue(
        self, as_of: Optional[date] = None, skip: int = 0, limit: int = 50
    ) -> Sequence[AssetAllocation]:
        as_of = as_of or date.today()
        stmt = (
            select(AssetAllocation)
            .where(
                AssetAllocation.status == AllocationStatusEnum.ACTIVE,
                AssetAllocation.expected_return_date.is_not(None),
                AssetAllocation.expected_return_date < as_of,
            )
            .order_by(AssetAllocation.expected_return_date.asc())
            .offset(skip)
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def mark_returned(
        self,
        allocation: AssetAllocation,
        return_condition: AssetConditionEnum,
        return_notes: Optional[str],
    ) -> AssetAllocation:
        allocation.status = AllocationStatusEnum.RETURNED
        allocation.returned_at = datetime.utcnow()
        allocation.return_condition = return_condition
        allocation.return_notes = return_notes
        self.db.flush()
        return allocation