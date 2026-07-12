"""
Department router. Endpoints are business actions, not raw CRUD:
create / read / update handle basic fields; assign-head and
activate/deactivate are separate, explicit workflow endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user, require_role
from models.enums import RoleEnum, ActiveStatusEnum
from schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    AssignHeadRequest,
)
from services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("", response_model=DepartmentResponse, status_code=201,
             dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService(db).create(payload)


@router.get("", response_model=list[DepartmentResponse],
            dependencies=[Depends(get_current_user)])
def list_departments(
    status: ActiveStatusEnum | None = None,
    parent_department_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return DepartmentService(db).list(status, parent_department_id, skip, limit)


@router.get("/{department_id}", response_model=DepartmentResponse,
            dependencies=[Depends(get_current_user)])
def get_department(department_id: int, db: Session = Depends(get_db)):
    return DepartmentService(db).get(department_id)


@router.patch("/{department_id}", response_model=DepartmentResponse,
              dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def update_department(department_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    return DepartmentService(db).update(department_id, payload)


@router.post("/{department_id}/assign-head", response_model=DepartmentResponse,
             dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def assign_head(department_id: int, payload: AssignHeadRequest, db: Session = Depends(get_db)):
    return DepartmentService(db).assign_head(department_id, payload.user_id)


@router.patch("/{department_id}/deactivate", response_model=DepartmentResponse,
              dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def deactivate_department(department_id: int, db: Session = Depends(get_db)):
    return DepartmentService(db).set_status(department_id, ActiveStatusEnum.INACTIVE)


@router.patch("/{department_id}/activate", response_model=DepartmentResponse,
              dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def activate_department(department_id: int, db: Session = Depends(get_db)):
    return DepartmentService(db).set_status(department_id, ActiveStatusEnum.ACTIVE)