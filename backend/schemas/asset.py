"""Pydantic V2 schemas for Asset."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.enums import AssetConditionEnum, AssetStatusEnum


class AssetCreate(BaseModel):
    """asset_tag is NEVER accepted from the client — always server-generated."""
    name: str = Field(min_length=2, max_length=150)
    category_id: int
    department_id: Optional[int] = None
    serial_number: Optional[str] = Field(default=None, max_length=100)
    qr_code_value: Optional[str] = Field(default=None, max_length=100)
    acquisition_date: Optional[date] = None
    acquisition_cost: Optional[Decimal] = Field(default=None, ge=0)
    condition: AssetConditionEnum = AssetConditionEnum.NEW
    location: Optional[str] = Field(default=None, max_length=150)
    is_bookable: bool = False
    photo_url: Optional[str] = Field(default=None, max_length=500)
    documents: Optional[list] = None
    custom_fields: Optional[dict] = None
    notes: Optional[str] = None


class AssetUpdate(BaseModel):
    """Partial update of descriptive fields only.
    Status changes go through the dedicated /change-status endpoint,
    never through this — status is a workflow action, not a field edit."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    serial_number: Optional[str] = Field(default=None, max_length=100)
    qr_code_value: Optional[str] = Field(default=None, max_length=100)
    acquisition_date: Optional[date] = None
    acquisition_cost: Optional[Decimal] = Field(default=None, ge=0)
    condition: Optional[AssetConditionEnum] = None
    location: Optional[str] = Field(default=None, max_length=150)
    is_bookable: Optional[bool] = None
    photo_url: Optional[str] = Field(default=None, max_length=500)
    documents: Optional[list] = None
    custom_fields: Optional[dict] = None
    notes: Optional[str] = None


class ChangeStatusRequest(BaseModel):
    to_status: AssetStatusEnum
    reason: Optional[str] = Field(default=None, max_length=255)


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_tag: str
    serial_number: Optional[str]
    qr_code_value: Optional[str]
    name: str
    category_id: int
    department_id: Optional[int]
    acquisition_date: Optional[date]
    acquisition_cost: Optional[Decimal]
    condition: AssetConditionEnum
    status: AssetStatusEnum
    location: Optional[str]
    is_bookable: bool
    photo_url: Optional[str]
    documents: Optional[list]
    custom_fields: Optional[dict]
    notes: Optional[str]
    created_at: datetime


class AssetStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_status: Optional[AssetStatusEnum]
    to_status: AssetStatusEnum
    changed_by_id: Optional[int]
    reason: Optional[str]
    changed_at: datetime