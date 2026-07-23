"""Thin router — validation, DI, response shaping only. No business logic."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import ActiveStatusEnum, RoleEnum
from schemas.user import UserResponse
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    department_id: Optional[int] = None,
    role: Optional[RoleEnum] = None,
    status: Optional[ActiveStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    actor=Depends(get_current_user),
):
    return UserService(db).list(department_id, role, status, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    actor=Depends(get_current_user),
):
    return UserService(db).get(user_id)


@router.post("/{user_id}/promote-asset-manager", response_model=UserResponse)
def promote_to_asset_manager(
    user_id: int,
    db: Session = Depends(get_db),
    actor=Depends(require_role(RoleEnum.ADMIN)),
):
    return UserService(db).promote_to_asset_manager(user_id)