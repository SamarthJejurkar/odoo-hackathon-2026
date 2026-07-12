"""Pydantic V2 schemas for User — request/response contracts."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from models.enums import RoleEnum, ActiveStatusEnum


class UserCreate(BaseModel):
    """Self-registration payload. role/employee_code/status are NEVER
    accepted from the client — role is always forced to EMPLOYEE and
    employee_code is generated server-side (see AuthService.register)."""
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    department_id: Optional[int] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    full_name: str
    email: EmailStr
    role: RoleEnum
    status: ActiveStatusEnum
    department_id: Optional[int]
    created_at: datetime