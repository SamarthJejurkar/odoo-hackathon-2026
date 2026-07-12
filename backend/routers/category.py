"""Asset Category router. Admin-only per Screen 3 (Organization Setup)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import RoleEnum
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Asset Categories"])

_ADMIN_ONLY = require_role(RoleEnum.ADMIN)


@router.post("", response_model=CategoryResponse, status_code=201,
             dependencies=[Depends(_ADMIN_ONLY)])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService(db).create(payload)


@router.get("", response_model=list[CategoryResponse],
            dependencies=[Depends(get_current_user)])
def list_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return CategoryService(db).list(skip, limit)


@router.get("/{category_id}", response_model=CategoryResponse,
            dependencies=[Depends(get_current_user)])
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService(db).get(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse,
              dependencies=[Depends(_ADMIN_ONLY)])
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    return CategoryService(db).update(category_id, payload)


@router.delete("/{category_id}", status_code=204,
               dependencies=[Depends(_ADMIN_ONLY)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    CategoryService(db).delete(category_id)