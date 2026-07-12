"""
Asset router. Registration/editing restricted to Admin + Asset Manager
per the problem statement ("Asset Manager registers and allocates
assets"). Read access is open to any authenticated user — every role
needs to search/browse the directory.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.user import User
from models.enums import RoleEnum, AssetStatusEnum
from schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    ChangeStatusRequest,
    AssetStatusHistoryResponse,
)
from services.asset_service import AssetService
from services.asset_lifecycle_service import AssetLifecycleService

router = APIRouter(prefix="/assets", tags=["Assets"])

_CAN_MANAGE = require_role(RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)


@router.post("", response_model=AssetResponse, status_code=201,
             dependencies=[Depends(_CAN_MANAGE)])
def register_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    return AssetService(db).register(payload)


@router.get("", response_model=list[AssetResponse],
            dependencies=[Depends(get_current_user)])
def search_assets(
    q: str | None = Query(default=None, description="Search asset tag, serial number, QR code, or name"),
    category_id: int | None = None,
    department_id: int | None = None,
    status: AssetStatusEnum | None = None,
    location: str | None = None,
    is_bookable: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return AssetService(db).search(
        query=q, category_id=category_id, department_id=department_id,
        status=status, location=location, is_bookable=is_bookable,
        skip=skip, limit=limit,
    )


@router.get("/{asset_id}", response_model=AssetResponse,
            dependencies=[Depends(get_current_user)])
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    return AssetService(db).get(asset_id)


@router.patch("/{asset_id}", response_model=AssetResponse,
              dependencies=[Depends(_CAN_MANAGE)])
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    return AssetService(db).update(asset_id, payload)


@router.get("/{asset_id}/history", response_model=list[AssetStatusHistoryResponse],
            dependencies=[Depends(get_current_user)])
def get_asset_history(asset_id: int, db: Session = Depends(get_db)):
    return AssetService(db).get_history(asset_id)


@router.post("/{asset_id}/change-status", response_model=AssetResponse,
             dependencies=[Depends(_CAN_MANAGE)])
def change_asset_status(
    asset_id: int,
    payload: ChangeStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AssetLifecycleService(db).transition(
        asset_id, to_status=payload.to_status, changed_by_id=current_user.id, reason=payload.reason
    )