"""Pydantic V2 schemas for AuditCycle / AuditCycleAuditor / AuditItem."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from models.enums import AuditCycleStatusEnum, AuditItemStatusEnum


class AuditCycleCreate(BaseModel):
    name: str
    scope_department_id: Optional[int] = None
    scope_location: Optional[str] = None
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self) -> "AuditCycleCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date.")
        return self


class AuditorAssign(BaseModel):
    auditor_id: int


class AuditItemVerify(BaseModel):
    verification_status: AuditItemStatusEnum
    notes: Optional[str] = None

    @model_validator(mode="after")
    def check_not_pending(self) -> "AuditItemVerify":
        if self.verification_status == AuditItemStatusEnum.PENDING:
            raise ValueError("Cannot verify an item back into PENDING — choose an actual outcome.")
        return self


class AuditCycleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    scope_department_id: Optional[int]
    scope_location: Optional[str]
    start_date: date
    end_date: date
    status: AuditCycleStatusEnum
    created_by_id: int
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class AuditItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    audit_cycle_id: int
    asset_id: int
    verified_by_id: Optional[int]
    verification_status: AuditItemStatusEnum
    notes: Optional[str]
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class AuditorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    audit_cycle_id: int
    auditor_id: int


class CloseCycleResult(BaseModel):
    cycle: AuditCycleRead
    items_transitioned_to_lost: list[int]  # asset_ids
    items_transition_failed: list[dict]     # [{asset_id, reason}]