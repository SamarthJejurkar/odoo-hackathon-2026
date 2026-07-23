"""Thin router — validation, DI, response shaping only. No business logic."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import AllocationStatusEnum, RoleEnum
from models.user import User
from schemas.allocation import AllocationCreate, AllocationRead, AllocationReturn
from services.allocation_service import AllocationService
from utils.response import success_envelope

router = APIRouter(prefix="/allocations", tags=["Allocations"])


@router.post("", response_model=dict, status_code=201)
def create_allocation(
    payload: AllocationCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    allocation = AllocationService(db).create_allocation(payload, actor)
    return success_envelope(AllocationRead.model_validate(allocation).model_dump())


@router.get("", response_model=dict)
def list_allocations(
    asset_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    department_id: Optional[int] = None,
    status: Optional[AllocationStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    allocations = AllocationService(db).list_allocations(
        asset_id, employee_id, department_id, status, skip, limit
    )
    return success_envelope([AllocationRead.model_validate(a).model_dump() for a in allocations])


@router.get("/overdue", response_model=dict)
def list_overdue_allocations(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    allocations = AllocationService(db).list_overdue()
    return success_envelope([AllocationRead.model_validate(a).model_dump() for a in allocations])


@router.get("/{allocation_id}", response_model=dict)
def get_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    allocation = AllocationService(db).get_allocation(allocation_id)
    return success_envelope(AllocationRead.model_validate(allocation).model_dump())


@router.post("/{allocation_id}/return", response_model=dict)
def return_allocation(
    allocation_id: int,
    payload: AllocationReturn,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    allocation = AllocationService(db).return_allocation(allocation_id, payload, actor)
    return success_envelope(AllocationRead.model_validate(allocation).model_dump())