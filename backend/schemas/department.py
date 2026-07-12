"""Pydantic V2 schemas for Department."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.enums import ActiveStatusEnum


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str = Field(min_length=2, max_length=20)
    parent_department_id: Optional[int] = None


class DepartmentUpdate(BaseModel):
    """Partial update — only provided fields are changed.
    Head assignment and status changes go through their own dedicated
    business-action endpoints, not this generic update (per API philosophy:
    design around business actions, not raw CRUD)."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    code: Optional[str] = Field(default=None, min_length=2, max_length=20)
    parent_department_id: Optional[int] = None


class AssignHeadRequest(BaseModel):
    user_id: int


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    parent_department_id: Optional[int]
    department_head_id: Optional[int]
    status: ActiveStatusEnum
    created_at: datetime