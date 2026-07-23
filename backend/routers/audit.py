"""Thin router for Audit Cycle workflow endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import AuditCycleStatusEnum, AuditItemStatusEnum, RoleEnum
from models.user import User
from schemas.audit import (
    AuditCycleCreate,
    AuditCycleRead,
    AuditItemRead,
    AuditItemVerify,
    AuditorAssign,
    AuditorRead,
    CloseCycleResult,
)
from services.audit_service import AuditService
from utils.response import success_envelope

router = APIRouter(prefix="/audit-cycles", tags=["Audit Cycles"])


@router.post("", response_model=dict, status_code=201)
def create_cycle(
    payload: AuditCycleCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    cycle = AuditService(db).create_cycle(payload, actor)
    return success_envelope(AuditCycleRead.model_validate(cycle).model_dump())


@router.get("", response_model=dict)
def list_cycles(
    status: Optional[AuditCycleStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    cycles = AuditService(db).list_cycles(status, skip, limit)
    return success_envelope([AuditCycleRead.model_validate(c).model_dump() for c in cycles])


@router.get("/{cycle_id}", response_model=dict)
def get_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    cycle = AuditService(db).get_cycle(cycle_id)
    return success_envelope(AuditCycleRead.model_validate(cycle).model_dump())


@router.post("/{cycle_id}/auditors", response_model=dict, status_code=201)
def assign_auditor(
    cycle_id: int,
    payload: AuditorAssign,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    link = AuditService(db).assign_auditor(cycle_id, payload.auditor_id, actor)
    return success_envelope(AuditorRead.model_validate(link).model_dump())


@router.get("/{cycle_id}/auditors", response_model=dict)
def list_auditors(
    cycle_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    auditors = AuditService(db).list_auditors(cycle_id)
    return success_envelope([AuditorRead.model_validate(a).model_dump() for a in auditors])


@router.post("/{cycle_id}/start", response_model=dict)
def start_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    cycle = AuditService(db).start_cycle(cycle_id, actor)
    return success_envelope(AuditCycleRead.model_validate(cycle).model_dump())


@router.get("/{cycle_id}/items", response_model=dict)
def list_items(
    cycle_id: int,
    verification_status: Optional[AuditItemStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    items = AuditService(db).list_items(cycle_id, verification_status, skip, limit)
    return success_envelope([AuditItemRead.model_validate(i).model_dump() for i in items])


@router.post("/items/{item_id}/verify", response_model=dict)
def verify_item(
    item_id: int,
    payload: AuditItemVerify,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    item = AuditService(db).verify_item(item_id, payload, actor)
    return success_envelope(AuditItemRead.model_validate(item).model_dump())


@router.post("/{cycle_id}/close", response_model=dict)
def close_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)),
):
    result = AuditService(db).close_cycle(cycle_id, actor)
    return success_envelope(
        CloseCycleResult(
            cycle=AuditCycleRead.model_validate(result["cycle"]),
            items_transitioned_to_lost=result["items_transitioned_to_lost"],
            items_transition_failed=result["items_transition_failed"],
        ).model_dump()
    )