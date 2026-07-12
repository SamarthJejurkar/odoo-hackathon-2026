"""
Business logic for Asset registration, search, and editing.
Status transitions are delegated to AssetLifecycleService — this
service never touches Asset.status directly.
"""
from sqlalchemy.orm import Session

from repositories.asset_repository import AssetRepository
from repositories.department_repository import DepartmentRepository
from schemas.asset import AssetCreate, AssetUpdate
from core.exceptions import ConflictException, NotFoundException, ValidationException
from models.category import AssetCategory
from sqlalchemy import select


class AssetService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AssetRepository(db)
        self.department_repo = DepartmentRepository(db)

    def get(self, asset_id: int):
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            raise NotFoundException("Asset not found.")
        return asset

    def search(self, **filters):
        return self.repo.search(**filters)

    def get_history(self, asset_id: int):
        self.get(asset_id)  # 404s if the asset itself doesn't exist
        return self.repo.get_status_history(asset_id)

    def register(self, payload: AssetCreate):
        self._validate_category_exists(payload.category_id)
        if payload.department_id is not None:
            self._validate_department_exists(payload.department_id)
        if payload.serial_number and self.repo.get_by_serial_number(payload.serial_number):
            raise ConflictException(
                f"An asset with serial number '{payload.serial_number}' already exists."
            )

        asset_tag = self.repo.next_asset_tag()
        return self.repo.create(asset_tag=asset_tag, **payload.model_dump())

    def update(self, asset_id: int, payload: AssetUpdate):
        asset = self.get(asset_id)
        updates = payload.model_dump(exclude_unset=True)

        if "category_id" in updates:
            self._validate_category_exists(updates["category_id"])
        if "department_id" in updates and updates["department_id"] is not None:
            self._validate_department_exists(updates["department_id"])
        if "serial_number" in updates and updates["serial_number"]:
            existing = self.repo.get_by_serial_number(updates["serial_number"])
            if existing and existing.id != asset_id:
                raise ConflictException(
                    f"An asset with serial number '{updates['serial_number']}' already exists."
                )

        for field, value in updates.items():
            setattr(asset, field, value)

        return self.repo.save(asset)

    # ---------- internal validation ----------

    def _validate_category_exists(self, category_id: int):
        category = self.db.scalar(select(AssetCategory).where(AssetCategory.id == category_id))
        if not category:
            raise ValidationException(f"Asset category with id {category_id} does not exist.")

    def _validate_department_exists(self, department_id: int):
        if not self.department_repo.get_by_id(department_id):
            raise ValidationException(f"Department with id {department_id} does not exist.")