"""Business logic for Asset Category management."""
from sqlalchemy.orm import Session

from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate, CategoryUpdate
from core.exceptions import ConflictException, NotFoundException


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def get(self, category_id: int):
        category = self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Asset category not found.")
        return category

    def list(self, skip: int = 0, limit: int = 100):
        return self.repo.list_all(skip, limit)

    def create(self, payload: CategoryCreate):
        if self.repo.get_by_name(payload.name):
            raise ConflictException(f"A category named '{payload.name}' already exists.")

        schema = (
            [f.model_dump() for f in payload.custom_fields_schema]
            if payload.custom_fields_schema else None
        )
        return self.repo.create(
            name=payload.name,
            description=payload.description,
            custom_fields_schema=schema,
        )

    def update(self, category_id: int, payload: CategoryUpdate):
        category = self.get(category_id)
        updates = payload.model_dump(exclude_unset=True)

        if "name" in updates and updates["name"] != category.name:
            if self.repo.get_by_name(updates["name"]):
                raise ConflictException(f"A category named '{updates['name']}' already exists.")
            category.name = updates["name"]

        if "description" in updates:
            category.description = updates["description"]

        if "custom_fields_schema" in updates:
            schema = updates["custom_fields_schema"]
            category.custom_fields_schema = (
                [f if isinstance(f, dict) else f.model_dump() for f in schema] if schema else None
            )

        return self.repo.save(category)

    def delete(self, category_id: int):
        category = self.get(category_id)
        asset_count = self.repo.count_assets_using(category_id)
        if asset_count > 0:
            raise ConflictException(
                f"Cannot delete: {asset_count} asset(s) still reference this category."
            )
        self.repo.delete(category)