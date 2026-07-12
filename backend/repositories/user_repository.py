"""
Repository layer — raw DB queries only. No business rules (those live
in AuthService).
"""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.user import User
from core.security import hash_password


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.scalar(select(User).where(User.id == user_id))

    def next_employee_code(self) -> str:
        """
        Generates the next sequential employee code, e.g. EMP0001.
        NOTE: this is a placeholder scheme — replace with whatever
        convention HR/Org-Setup actually uses if one already exists.
        """
        count = self.db.scalar(select(func.count()).select_from(User)) or 0
        return f"EMP{count + 1:04d}"

    def create(self, *, full_name: str, email: str, password: str, department_id: int | None) -> User:
        user = User(
            employee_code=self.next_employee_code(),
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            department_id=department_id,
            # role and status are NOT accepted from the caller here —
            # they use the model's own defaults (EMPLOYEE / ACTIVE).
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    def update_role(self, user: "User", role) -> "User":
        """Used exclusively by the Organization Setup workflow
        (e.g. DepartmentService.assign_head) to promote a role.
        Never call this from a general-purpose user-update endpoint."""
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user