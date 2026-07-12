"""
Pydantic V2 schemas for AssetAllocation.

CreateAllocation enforces the employee-XOR-department rule at the API
boundary (mirrors the DB CheckConstraint) so a bad request fails with
a clean 422 instead of reaching the DB and erroring there.

is_overdue is a COMPUTED field, not a stored column. AllocationStatusEnum
has an OVERDUE member, but it is intentionally never written to the DB —
see AllocationService docstring for why (the partial unique index that
prevents double-allocation only covers status='ACTIVE'; writing OVERDUE
into that column would silently reopen the double-allocation race for
any late return). "Overdue" is always derived at read time instead.
"""
from __future__ import annotations

from datetime import date as date_, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from models.enums import AllocationStatusEnum, AssetConditionEnum


class AllocationCreate(BaseModel):
    asset_id: int
    employee_id: Optional[int] = None
    department_id: Optional[int] = None
    expected_return_date: Optional[date_] = None

    @model_validator(mode="after")
    def check_target_xor(self) -> "AllocationCreate":
        if bool(self.employee_id) == bool(self.department_id):
            raise ValueError(
                "Exactly one of employee_id or department_id must be provided, not both or neither."
            )
        return self


class AllocationReturn(BaseModel):
    return_condition: AssetConditionEnum
    return_notes: Optional[str] = None
    # Post-return target is AVAILABLE unless mark_lost is set — the asset
    # lifecycle table only permits ALLOCATED -> AVAILABLE or ALLOCATED -> LOST,
    # never straight to UNDER_MAINTENANCE. Damaged returns go to AVAILABLE
    # first, then a separate /assets/{id}/change-status call.
    mark_lost: bool = False


class AllocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    employee_id: Optional[int]
    department_id: Optional[int]
    allocated_by_id: int
    allocated_at: datetime
    expected_return_date: Optional[date_]
    returned_at: Optional[datetime]
    return_condition: Optional[AssetConditionEnum]
    return_notes: Optional[str]
    status: AllocationStatusEnum
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[misc]
    @property
    def is_overdue(self) -> bool:
        return (
            self.status == AllocationStatusEnum.ACTIVE
            and self.expected_return_date is not None
            and self.expected_return_date < date_.today()
        )


class AllocationConflictDetail(BaseModel):
    """Shape of the 409 detail payload when an asset is already actively allocated."""
    asset_id: int
    current_allocation_id: int
    held_by_employee_id: Optional[int]
    held_by_department_id: Optional[int]
    allocated_at: datetime
    expected_return_date: Optional[date_]