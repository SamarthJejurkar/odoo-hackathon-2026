"""
Department master data.

Two relationships worth calling out:

1. parent_department_id is self-referential -> lets Admin model an org
   chart (e.g. "IT" under "Operations") without a separate closure table.
   For AssetFlow's expected depth (2-3 levels) an adjacency list is the
   right tool; a closure table or ltree would be over-engineering for
   this scale (YAGNI).

2. department_head_id points at users.id, but users.department_id points
   back at departments.id - a genuine circular FK. This is modeled with
   use_alter=True so Alembic emits the departments->users FK as a
   separate ALTER TABLE after both tables exist, breaking the creation
   order deadlock. See seed/seed_data.py for the two-phase insert this
   requires at the data level.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import ActiveStatusEnum
from models.mixins import TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"
    __table_args__ = (
        CheckConstraint("id != parent_department_id", name="ck_department_not_own_parent"),
        Index("ix_departments_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    parent_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    # Circular reference resolved with use_alter - see module docstring.
    department_head_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL", use_alter=True, name="fk_department_head"),
        nullable=True,
    )

    status: Mapped[ActiveStatusEnum] = mapped_column(
        PgEnum(ActiveStatusEnum, name="active_status_enum", native_enum=True, create_type=False),
        default=ActiveStatusEnum.ACTIVE,
        nullable=False,
    )

    # --- relationships ---
    parent: Mapped[Optional["Department"]] = relationship(
        remote_side="Department.id", back_populates="children"
    )
    children: Mapped[list["Department"]] = relationship(back_populates="parent")

    head = relationship(
        "User", foreign_keys=[department_head_id], post_update=True, viewonly=False
    )
    employees: Mapped[list["User"]] = relationship(
        back_populates="department", foreign_keys="User.department_id"
    )
    assets: Mapped[list["Asset"]] = relationship(back_populates="department")

    # Departments can be the allocation target (asset issued to a whole
    # department rather than an individual employee) - see the XOR
    # constraint on AssetAllocation. foreign_keys= is required here
    # because AssetAllocation has multiple FK columns pointing at
    # different tables/columns that back_populates must be told apart.
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        back_populates="department", foreign_keys="AssetAllocation.department_id"
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"