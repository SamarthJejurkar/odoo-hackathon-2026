"""Thin router for AssetTransferRequest workflow endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import RoleEnum, TransferStatusEnum
from models.user import User
from schemas.transfer import TransferCreate, TransferRead, TransferRejection
from services.transfer_service import TransferService
from utils.response import success_envelope

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("", response_model=dict, status_code=201)
def create_transfer(
    payload: TransferCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    transfer = TransferService(db).create_transfer(payload, actor)
    return success_envelope(TransferRead.model_validate(transfer).model_dump())


@router.get("", response_model=dict)
def list_transfers(
    asset_id: Optional[int] = None,
    status: Optional[TransferStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    transfers = TransferService(db).list_transfers(asset_id, status, skip, limit)
    return success_envelope([TransferRead.model_validate(t).model_dump() for t in transfers])


@router.get("/{transfer_id}", response_model=dict)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    transfer = TransferService(db).get_transfer(transfer_id)
    return success_envelope(TransferRead.model_validate(transfer).model_dump())


@router.post("/{transfer_id}/approve-dept-head", response_model=dict)
def approve_dept_head(
    transfer_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.DEPARTMENT_HEAD, RoleEnum.ADMIN)),
):
    transfer = TransferService(db).approve_dept_head(transfer_id, actor)
    return success_envelope(TransferRead.model_validate(transfer).model_dump())


@router.post("/{transfer_id}/approve-asset-manager", response_model=dict)
def approve_asset_manager(
    transfer_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.ASSET_MANAGER, RoleEnum.ADMIN)),
):
    transfer = TransferService(db).approve_asset_manager(transfer_id, actor)
    return success_envelope(TransferRead.model_validate(transfer).model_dump())


@router.post("/{transfer_id}/reject", response_model=dict)
def reject_transfer(
    transfer_id: int,
    payload: TransferRejection,
    db: Session = Depends(get_db),
    actor: User = Depends(require_role(RoleEnum.DEPARTMENT_HEAD, RoleEnum.ASSET_MANAGER, RoleEnum.ADMIN)),
):
    transfer = TransferService(db).reject(transfer_id, payload, actor)
    return success_envelope(TransferRead.model_validate(transfer).model_dump())
