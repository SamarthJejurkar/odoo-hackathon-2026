"""Thin router for MaintenanceRequest workflow endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import MaintenanceStatusEnum, RoleEnum
from models.user import User
from schemas.maintenance import (
    MaintenanceRejection,
    MaintenanceRequestCreate,
    MaintenanceRequestRead,
    MaintenanceResolution,
    TechnicianAssignment,
)
from services.maintenance_service import MaintenanceService
from utils.response import success_envelope

router = APIRouter(prefix="/maintenance-requests", tags=["Maintenance"])


@router.post("", response_model=dict, status_code=201)
def create_request(
    payload: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    request = MaintenanceService(db).create_request(payload, actor)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())


@router.get("", response_model=dict)
def list_requests(
    asset_id: Optional[int] = None,
    status: Optional[MaintenanceStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    requests = MaintenanceService(db).list_requests(asset_id, status, skip, limit)
    return success_envelope([MaintenanceRequestRead.model_validate(r).model_dump() for r in requests])


@router.get("/{request_id}", response_model=dict)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    request = MaintenanceService(db).get_request(request_id)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())


@router.post("/{request_id}/approve", response_model=dict)
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    request = MaintenanceService(db).approve(request_id, actor)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())


@router.post("/{request_id}/reject", response_model=dict)
def reject_request(
    request_id: int,
    payload: MaintenanceRejection,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    request = MaintenanceService(db).reject(request_id, payload, actor)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())


@router.post("/{request_id}/assign-technician", response_model=dict)
def assign_technician(
    request_id: int,
    payload: TechnicianAssignment,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    request = MaintenanceService(db).assign_technician(request_id, payload, actor)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())


@router.post("/{request_id}/start", response_model=dict)
def start_work(
    request_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    request = MaintenanceService(db).start_work(request_id, actor)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())


@router.post("/{request_id}/resolve", response_model=dict)
def resolve_request(
    request_id: int,
    payload: MaintenanceResolution,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    request = MaintenanceService(db).resolve(request_id, payload, actor)
    return success_envelope(MaintenanceRequestRead.model_validate(request).model_dump())