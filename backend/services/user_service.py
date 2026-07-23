"""User service — read-only employee directory queries, plus the
Asset Manager promotion path.

Role/status mutation is otherwise kept out of here on purpose: the
only other permitted path to change a user's role is Organization
Setup (Screen 3, Tab C) via DepartmentService.assign_head, which
promotes to DEPARTMENT_HEAD. promote_to_asset_manager below is the
equivalent path for ASSET_MANAGER, since that role isn't
department-scoped and has no natural home in DepartmentService.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException, ValidationException
from models.enums import ActiveStatusEnum, RoleEnum
from models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        department_id: Optional[int] = None,
        role: Optional[RoleEnum] = None,
        status: Optional[ActiveStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[User]:
        query = self.db.query(User)

        if department_id is not None:
            query = query.filter(User.department_id == department_id)
        if role is not None:
            query = query.filter(User.role == role)
        if status is not None:
            query = query.filter(User.status == status)

        return query.offset(skip).limit(limit).all()

    def get(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise NotFoundException("User not found")
        return user

    def promote_to_asset_manager(self, user_id: int) -> User:
        user = self.get(user_id)

        if user.status != ActiveStatusEnum.ACTIVE:
            raise ValidationException("Cannot promote an inactive user.")

        # Same guard as DepartmentService.assign_head — never silently
        # overwrite an existing ADMIN's role. An admin outranks this
        # promotion; changing it here would be an accidental demotion
        # of privilege scope, not an upgrade.
        if user.role == RoleEnum.ADMIN:
            raise ValidationException("Cannot change an Admin's role through this action.")

        user.role = RoleEnum.ASSET_MANAGER
        self.db.commit()
        self.db.refresh(user)
        return user