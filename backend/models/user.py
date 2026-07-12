"""
User = the employee directory + auth identity, unified into one table.

Why one table and not Employee + separate Auth/Credentials table?
Every employee in AssetFlow can potentially log in (signup creates an
Employee account), so splitting auth into its own table would just mean
a mandatory 1:1 join on every login - added complexity with no isolation
benefit, since there's no case where an "employee" exists without login
credentials. Split them only if you later add non-login entities (e.g.
contractors who hold assets but never authenticate).

ROLE RULE: role is assigned here, but the *only* code path allowed to
promote a user to department_head or asset_manager is the Organization
Setup service (Screen 3, Tab C). Signup always inserts role=EMPLOYEE.
Never trust a role value coming from the client on any other endpoint.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import ActiveStatusEnum, RoleEnum
from models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_department_id", "department_id"),
        Index("ix_users_role", "role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    role: Mapped[RoleEnum] = mapped_column(
        PgEnum(RoleEnum, name="role_enum", native_enum=True),
        default=RoleEnum.EMPLOYEE,
        nullable=False,
    )
    status: Mapped[ActiveStatusEnum] = mapped_column(
        PgEnum(ActiveStatusEnum, name="active_status_enum", native_enum=True),
        default=ActiveStatusEnum.ACTIVE,
        nullable=False,
    )

    # --- relationships ---
    department: Mapped[Optional["Department"]] = relationship(
        back_populates="employees", foreign_keys=[department_id]
    )

    # AssetAllocation has TWO foreign keys into users (employee_id and
    # allocated_by_id), so each relationship here must be disambiguated
    # with foreign_keys= and mapped to its own back_populates on
    # AssetAllocation - otherwise SQLAlchemy can't tell which FK column
    # a given relationship refers to (AmbiguousForeignKeysError).
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        back_populates="employee", foreign_keys="AssetAllocation.employee_id"
    )
    allocations_made: Mapped[list["AssetAllocation"]] = relationship(
        back_populates="allocated_by", foreign_keys="AssetAllocation.allocated_by_id"
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="booked_by_user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


class PasswordResetToken(Base, TimestampMixin):
    """Short-lived tokens for the 'forgot password' flow (Screen 1).

    Kept as its own table rather than columns on User so a user can have
    multiple outstanding/expired tokens without ever overwriting history,
    and so token rows can be purged independently via a scheduled job
    without touching the users table.
    """
    __tablename__ = "password_reset_tokens"
    __table_args__ = (Index("ix_password_reset_tokens_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)