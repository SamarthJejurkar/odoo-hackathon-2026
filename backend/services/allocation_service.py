"""
Business logic for AssetAllocation.

Concurrency note: the "asset already taken" check is NOT trusted from a
pre-flight SELECT. We attempt the INSERT and let the DB's partial unique
index (uq_one_active_allocation_per_asset) be the final word. On
IntegrityError we re-query for the live holder and raise a
ConflictException that names them — this is what closes the TOCTOU race
two concurrent requests could otherwise hit.

Commit boundary: AssetLifecycleService.transition() commits internally
(status change + history write, atomic, per its own docstring). Every
method here therefore does exactly ONE commit total, performed inside
transition() itself — never a separate self.db.commit() after it, and
never before it (the allocation row is only flush()'d beforehand, via
the repository, so it's visible in the same open transaction without
being durable until transition() commits).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException, ValidationException
from models.allocation import AssetAllocation
from models.asset import Asset
from models.department import Department
from models.enums import AllocationStatusEnum, AssetStatusEnum
from models.user import User
from repositories.allocation_repository import AllocationRepository
from schemas.allocation import AllocationConflictDetail, AllocationCreate, AllocationReturn
from services.asset_lifecycle_service import AssetLifecycleService


class AllocationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AllocationRepository(db)
        self.lifecycle = AssetLifecycleService(db)

    def _resolve_target(self, payload: AllocationCreate) -> None:
        if payload.employee_id is not None:
            if self.db.get(User, payload.employee_id) is None:
                raise NotFoundException(f"Employee {payload.employee_id} not found.")
        if payload.department_id is not None:
            if self.db.get(Department, payload.department_id) is None:
                raise NotFoundException(f"Department {payload.department_id} not found.")

    def create_allocation(self, payload: AllocationCreate, actor: User) -> AssetAllocation:
        asset = self.db.get(Asset, payload.asset_id)
        if asset is None:
            raise NotFoundException(f"Asset {payload.asset_id} not found.")

        if asset.status not in (AssetStatusEnum.AVAILABLE, AssetStatusEnum.RESERVED):
            raise ValidationException(
                f"Asset {asset.asset_tag} is '{asset.status.value}' and cannot be allocated. "
                "Only AVAILABLE or RESERVED assets can be allocated."
            )

        self._resolve_target(payload)

        allocation = AssetAllocation(
            asset_id=payload.asset_id,
            employee_id=payload.employee_id,
            department_id=payload.department_id,
            allocated_by_id=actor.id,
            allocated_at=datetime.utcnow(),
            expected_return_date=payload.expected_return_date,
            status=AllocationStatusEnum.ACTIVE,
        )

        try:
            self.repo.create(allocation)  # flush only — surfaces the unique-index violation here
            self.lifecycle.transition(
                asset_id=asset.id,
                to_status=AssetStatusEnum.ALLOCATED,
                changed_by_id=actor.id,
                reason=f"Allocated via allocation #{allocation.id}",
            )
            # transition() commits internally — no separate commit here.
        except IntegrityError:
            self.db.rollback()
            current = self.repo.get_active_for_asset(payload.asset_id)
            detail = (
                AllocationConflictDetail(
                    asset_id=asset.id,
                    current_allocation_id=current.id,
                    held_by_employee_id=current.employee_id,
                    held_by_department_id=current.department_id,
                    allocated_at=current.allocated_at,
                    expected_return_date=current.expected_return_date,
                )
                if current
                else None
            )
            raise ConflictException(
                f"Asset {asset.asset_tag} is already actively allocated. Use a Transfer Request instead.",
                detail=detail.model_dump() if detail else None,
            )

        self.db.refresh(allocation)
        return allocation

    def return_allocation(self, allocation_id: int, payload: AllocationReturn, actor: User) -> AssetAllocation:
        allocation = self.repo.get_by_id(allocation_id)
        if allocation is None:
            raise NotFoundException(f"Allocation {allocation_id} not found.")
        if allocation.status != AllocationStatusEnum.ACTIVE:
            raise ConflictException(f"Allocation {allocation_id} is not currently active.")

        self.repo.mark_returned(allocation, payload.return_condition, payload.return_notes)  # flush only

        to_status = AssetStatusEnum.LOST if payload.mark_lost else AssetStatusEnum.AVAILABLE
        self.lifecycle.transition(
            asset_id=allocation.asset_id,
            to_status=to_status,
            changed_by_id=actor.id,
            reason=f"Returned via allocation #{allocation.id}",
        )
        # transition() commits internally — no separate commit here.

        self.db.refresh(allocation)
        return allocation

    def get_allocation(self, allocation_id: int) -> AssetAllocation:
        allocation = self.repo.get_by_id(allocation_id)
        if allocation is None:
            raise NotFoundException(f"Allocation {allocation_id} not found.")
        return allocation

    def list_allocations(
        self,
        asset_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[AllocationStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[AssetAllocation]:
        return self.repo.list_filtered(asset_id, employee_id, department_id, status, skip, limit)

    def list_overdue(self) -> Sequence[AssetAllocation]:
        return self.repo.list_overdue()