"""Pydantic V2 schemas for MaintenanceRequest."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from models.enums import AssetStatusEnum, MaintenancePriorityEnum, MaintenanceStatusEnum

# Legal outcomes when resolving — matches UNDER_MAINTENANCE's outgoing
# edges in AssetLifecycleService._ALLOWED_TRANSITIONS.
_VALID_RESOLUTION_TARGETS = {
    AssetStatusEnum.AVAILABLE,
    AssetStatusEnum.LOST,
    AssetStatusEnum.RETIRED,
    AssetStatusEnum.DISPOSED,
}


class MaintenanceRequestCreate(BaseModel):
    asset_id: int
    issue_description: str
    priority: MaintenancePriorityEnum = MaintenancePriorityEnum.MEDIUM
    photo_url: Optional[str] = None


class MaintenanceRejection(BaseModel):
    rejection_reason: str


class TechnicianAssignment(BaseModel):
    technician_name: str


class MaintenanceResolution(BaseModel):
    resolution_notes: str
    resulting_status: AssetStatusEnum = AssetStatusEnum.AVAILABLE

    @model_validator(mode="after")
    def check_target(self) -> "MaintenanceResolution":
        if self.resulting_status not in _VALID_RESOLUTION_TARGETS:
            allowed = ", ".join(s.value for s in _VALID_RESOLUTION_TARGETS)
            raise ValueError(f"resulting_status must be one of: {allowed}")
        return self


class MaintenanceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    raised_by_id: int
    issue_description: str
    priority: MaintenancePriorityEnum
    photo_url: Optional[str]
    status: MaintenanceStatusEnum
    approved_by_id: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    technician_name: Optional[str]
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime