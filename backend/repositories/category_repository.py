"""Repository layer for AssetCategory — raw DB queries only."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.category import AssetCategory
from models.asset import Asset


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> AssetCategory | None:
        return self.db.scalar(select(AssetCategory).where(AssetCategory.id == category_id))

    def get_by_name(self, name: str) -> AssetCategory | None:
        return self.db.scalar(select(AssetCategory).where(AssetCategory.name == name))

    def list_all(self, skip: int = 0, limit: int = 100) -> list[AssetCategory]:
        return list(
            self.db.scalars(select(AssetCategory).offset(skip).limit(limit)).all()
        )

    def count_assets_using(self, category_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Asset).where(Asset.category_id == category_id)
        ) or 0

    def create(self, *, name: str, description: str | None, custom_fields_schema: list | None) -> AssetCategory:
        category = AssetCategory(
            name=name,
            description=description,
            custom_fields_schema=custom_fields_schema,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def save(self, category: AssetCategory) -> AssetCategory:
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: AssetCategory) -> None:
        self.db.delete(category)
        self.db.commit()