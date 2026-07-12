"""Pydantic V2 schemas for AssetTransferRequest."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from models.enums import TransferStatusEnum


class TransferCreate(BaseModel):
    asset_id: int
    requested_to_employee_id: Optional[int] = None
    requested_to_department_id: Optional[int] = None
    reason: Optional[str] = None

    @model_validator(mode="after")
    def check_target_xor(self) -> "TransferCreate":
        if bool(self.requested_to_employee_id) == bool(self.requested_to_department_id):
            raise ValueError(
                "Exactly one of requested_to_employee_id or requested_to_department_id "
                "must be provided, not both or neither."
            )
        return self


class TransferRejection(BaseModel):
    rejection_reason: str


class TransferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    current_allocation_id: Optional[int]
    requested_by_id: int
    requested_to_employee_id: Optional[int]
    requested_to_department_id: Optional[int]
    reason: Optional[str]
    status: TransferStatusEnum
    dept_head_approved_by_id: Optional[int]
    dept_head_approved_at: Optional[datetime]
    asset_manager_approved_by_id: Optional[int]
    asset_manager_approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime