"""
Asset categories.

DESIGN DECISION - custom_fields_schema (JSONB) instead of EAV tables:
The spec calls for "optional category-specific fields (e.g. warranty
period for Electronics)". A classic EAV (entity-attribute-value) model
would need attribute_definitions + attribute_values tables and would
make every category-specific query a multi-join. For a hackathon-scale
set of ~5-10 categories with a handful of extra fields each, that's
over-engineering (YAGNI) and it fights PostgreSQL's strengths.

Instead: the category stores a JSON Schema-like definition of its extra
fields, and each Asset stores its matching values in Asset.custom_fields
(also JSONB). This keeps the schema normalized (no sparse NULL-heavy
columns), keeps category definitions independently versionable, and
still allows indexed lookups via a GIN index on the JSONB column if a
report ever needs "all electronics with warranty expiring this month".

Example custom_fields_schema value:
  [{"key": "warranty_months", "label": "Warranty (months)", "type": "integer"}]
"""
from __future__ import annotations

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.mixins import TimestampMixin


class AssetCategory(Base, TimestampMixin):
    __tablename__ = "asset_categories"
    __table_args__ = (Index("ix_asset_categories_name", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_fields_schema: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    assets: Mapped[list["Asset"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<AssetCategory id={self.id} name={self.name!r}>"
