"""
Reusable mixins for ORM models.

DATABASE RULE: every table has id, created_at, updated_at.
`id` is declared per-model (types differ in a couple of join tables), but
the timestamp pair is identical everywhere, so it belongs in a mixin -
this is what DRY looks like at the schema level.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """created_at / updated_at, both DB-generated (not app-generated).

    Using server_default=func.now() instead of a Python default means the
    timestamp is authoritative even if it's written by a raw SQL script,
    a different service, or a bulk import - the database is the single
    source of truth for time, not the application clock.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
