"""
Notification and ActivityLog - the two tables the ERP philosophy in the
brief requires EVERY important business action to write to, alongside
History (modeled per-domain: AssetStatusHistory, allocation rows, audit
items) and Audit Trail (this ActivityLog).

Notification: user-facing, has a read/unread state, describes ONE event.
ActivityLog:  system-facing, immutable, generic across every entity type
              in the system - this is the who/what/when/old/new record.

ActivityLog uses polymorphic entity_type + entity_id (no FK) rather than
a nullable FK per entity type, because a single log table needs to
reference assets, bookings, transfers, audits, etc. without a
combinatorial explosion of nullable FK columns. The tradeoff (no
referential integrity on entity_id) is acceptable here because this
table is write-once, read-for-audit - it's a log, not a live relation
that needs cascade behavior.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import NotificationTypeEnum
from models.mixins import TimestampMixin


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_id_is_read", "user_id", "is_read"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    type: Mapped[NotificationTypeEnum] = mapped_column(
        PgEnum(NotificationTypeEnum, name="notification_type_enum", native_enum=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="notifications")


class ActivityLog(Base, TimestampMixin):
    """Immutable audit trail. Never updated or deleted after insert -
    enforce this with a REVOKE UPDATE, DELETE ON activity_logs FROM
    app_role; grant in the Alembic migration (see guidance below)."""
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_entity", "entity_type", "entity_id"),
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "asset.allocate"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "asset"
    entity_id: Mapped[int] = mapped_column(nullable=False)

    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
