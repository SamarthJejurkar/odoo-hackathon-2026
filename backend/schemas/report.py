"""
Pydantic response schemas for Screen 9 (Reports & Analytics).

Two things worth knowing before you touch this file:

1. "Assets due for maintenance" has no due-date field anywhere in the
   schema (MaintenanceRequest has no scheduled/next-service-date column,
   and Asset has none either). Rather than invent one under time
   pressure, this reports on OPEN maintenance requests ordered by
   priority + age - a legitimate proxy, just not literally "N days
   until service."
2. "Idle N days" is derived, not stored: it's days since the asset's
   most recent booking OR allocation activity, whichever is more
   recent. An asset with no activity at all is idle "since creation"
   (falls back to created_at).
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel


class DepartmentUtilization(BaseModel):
    department_name: str
    total_assets: int
    allocated_assets: int
    utilization_pct: float


class MaintenanceFrequencyPoint(BaseModel):
    month: str  # "2026-07"
    count: int


class MostUsedAsset(BaseModel):
    asset_id: int
    asset_tag: str
    name: str
    usage_count: int


class IdleAsset(BaseModel):
    asset_id: int
    asset_tag: str
    name: str
    days_idle: int


class MaintenanceDueAsset(BaseModel):
    asset_id: int
    asset_tag: str
    name: str
    priority: str
    status: str
    days_open: int


class AgingAsset(BaseModel):
    asset_id: int
    asset_tag: str
    name: str
    acquisition_date: Optional[date]
    age_years: float


class ReportSummary(BaseModel):
    utilization_by_department: list[DepartmentUtilization]
    maintenance_frequency: list[MaintenanceFrequencyPoint]
    most_used_assets: list[MostUsedAsset]
    idle_assets: list[IdleAsset]
    maintenance_due: list[MaintenanceDueAsset]
    aging_assets: list[AgingAsset]