"""
Business logic for Department management.
This service IS the "Organization Setup service" referenced in
models/user.py's docstring — it is the only code path allowed to
promote a user's role to DEPARTMENT_HEAD.
"""
from sqlalchemy.orm import Session

from repositories.department_repository import DepartmentRepository
from repositories.user_repository import UserRepository
from schemas.department import DepartmentCreate, DepartmentUpdate
from models.enums import ActiveStatusEnum, RoleEnum
from core.exceptions import ConflictException, NotFoundException, ValidationException


class DepartmentService:
    def __init__(self, db: Session):
        self.repo = DepartmentRepository(db)
        self.user_repo = UserRepository(db)

    # ---------- reads ----------

    def get(self, department_id: int):
        dept = self.repo.get_by_id(department_id)
        if not dept:
            raise NotFoundException("Department not found.")
        return dept

    def list(self, status=None, parent_department_id=None, skip=0, limit=50):
        return self.repo.list_all(status, parent_department_id, skip, limit)

    # ---------- writes ----------

    def create(self, payload: DepartmentCreate):
        if self.repo.get_by_name(payload.name):
            raise ConflictException(f"A department named '{payload.name}' already exists.")
        if self.repo.get_by_code(payload.code):
            raise ConflictException(f"Department code '{payload.code}' is already in use.")

        if payload.parent_department_id is not None:
            self._validate_parent_exists(payload.parent_department_id)

        return self.repo.create(
            name=payload.name,
            code=payload.code,
            parent_department_id=payload.parent_department_id,
        )

    def update(self, department_id: int, payload: DepartmentUpdate):
        dept = self.get(department_id)

        if payload.name is not None and payload.name != dept.name:
            if self.repo.get_by_name(payload.name):
                raise ConflictException(f"A department named '{payload.name}' already exists.")
            dept.name = payload.name

        if payload.code is not None and payload.code != dept.code:
            if self.repo.get_by_code(payload.code):
                raise ConflictException(f"Department code '{payload.code}' is already in use.")
            dept.code = payload.code

        if payload.parent_department_id is not None:
            self._validate_reparent(dept.id, payload.parent_department_id)
            dept.parent_department_id = payload.parent_department_id

        return self.repo.save(dept)

    def assign_head(self, department_id: int, user_id: int):
        dept = self.get(department_id)

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        if user.status != ActiveStatusEnum.ACTIVE:
            raise ValidationException("Cannot assign an inactive user as department head.")

        # Only promote a plain EMPLOYEE. Never silently overwrite an
        # existing ADMIN or ASSET_MANAGER's role — they outrank this
        # assignment and a promotion here would be an accidental demotion
        # of privilege scope, not an upgrade.
        if user.role == RoleEnum.EMPLOYEE:
            self.user_repo.update_role(user, RoleEnum.DEPARTMENT_HEAD)

        dept.department_head_id = user.id
        return self.repo.save(dept)

    def set_status(self, department_id: int, status: ActiveStatusEnum):
        dept = self.get(department_id)

        if status == ActiveStatusEnum.INACTIVE:
            active_count = self.repo.count_active_employees(department_id)
            if active_count > 0:
                raise ConflictException(
                    f"Cannot deactivate: {active_count} active employee(s) are still "
                    f"assigned to this department. Reassign them first."
                )

        dept.status = status
        return self.repo.save(dept)

    # ---------- internal validation ----------

    def _validate_parent_exists(self, parent_id: int):
        if not self.repo.get_by_id(parent_id):
            raise NotFoundException(f"Parent department with id {parent_id} does not exist.")

    def _validate_reparent(self, department_id: int, new_parent_id: int):
        if new_parent_id == department_id:
            raise ValidationException("A department cannot be its own parent.")
        self._validate_parent_exists(new_parent_id)

        # Cycle check: is `department_id` an ancestor of the proposed
        # new parent? If so, re-parenting would create a loop.
        ancestors_of_new_parent = self.repo.get_ancestor_ids(new_parent_id)
        if department_id in ancestors_of_new_parent:
            raise ValidationException(
                "This change would create a circular department hierarchy."
            )