"""Repository layer for Department — raw DB queries only."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.department import Department
from models.user import User
from models.enums import ActiveStatusEnum


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, department_id: int) -> Department | None:
        return self.db.scalar(select(Department).where(Department.id == department_id))

    def get_by_name(self, name: str) -> Department | None:
        return self.db.scalar(select(Department).where(Department.name == name))

    def get_by_code(self, code: str) -> Department | None:
        return self.db.scalar(select(Department).where(Department.code == code))

    def list_all(
        self,
        status: ActiveStatusEnum | None = None,
        parent_department_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Department]:
        query = select(Department)
        if status is not None:
            query = query.where(Department.status == status)
        if parent_department_id is not None:
            query = query.where(Department.parent_department_id == parent_department_id)
        query = query.offset(skip).limit(limit)
        return list(self.db.scalars(query).all())

    def get_ancestor_ids(self, department_id: int) -> set[int]:
        """Walks the parent chain upward. Used for cycle detection when
        re-parenting a department — O(depth), fine for the 2-3 level
        org charts this system expects."""
        ancestors: set[int] = set()
        current = self.get_by_id(department_id)
        while current and current.parent_department_id is not None:
            if current.parent_department_id in ancestors:
                break  # already-broken cycle in existing data; stop, don't loop forever
            ancestors.add(current.parent_department_id)
            current = self.get_by_id(current.parent_department_id)
        return ancestors

    def count_active_employees(self, department_id: int) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.department_id == department_id, User.status == ActiveStatusEnum.ACTIVE)
        ) or 0

    def create(self, *, name: str, code: str, parent_department_id: int | None) -> Department:
        dept = Department(name=name, code=code, parent_department_id=parent_department_id)
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept

    def save(self, department: Department) -> Department:
        """Persists changes made to an already-fetched Department instance."""
        self.db.commit()
        self.db.refresh(department)
        return department