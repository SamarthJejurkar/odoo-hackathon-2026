"""Pydantic V2 schemas for AssetCategory."""
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class CustomFieldDefinition(BaseModel):
    """One entry in a category's custom_fields_schema, e.g.
    {"key": "warranty_months", "label": "Warranty (months)", "type": "integer"}"""
    key: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=100)
    type: Literal["string", "integer", "number", "boolean", "date"]


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    custom_fields_schema: Optional[list[CustomFieldDefinition]] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    custom_fields_schema: Optional[list[CustomFieldDefinition]] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    custom_fields_schema: Optional[list]
    created_at: datetime