"""Repository layer for Asset — raw DB queries only."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.asset import Asset, AssetStatusHistory
from models.enums import AssetStatusEnum


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, asset_id: int) -> Asset | None:
        return self.db.scalar(select(Asset).where(Asset.id == asset_id))

    def get_by_asset_tag(self, asset_tag: str) -> Asset | None:
        return self.db.scalar(select(Asset).where(Asset.asset_tag == asset_tag))

    def get_by_serial_number(self, serial_number: str) -> Asset | None:
        return self.db.scalar(select(Asset).where(Asset.serial_number == serial_number))

    def next_asset_tag(self) -> str:
        """Generates the next sequential asset tag, e.g. AF-0001."""
        count = self.db.scalar(select(func.count()).select_from(Asset)) or 0
        return f"AF-{count + 1:04d}"

    def search(
        self,
        *,
        query: str | None = None,
        category_id: int | None = None,
        department_id: int | None = None,
        status: AssetStatusEnum | None = None,
        location: str | None = None,
        is_bookable: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Asset]:
        stmt = select(Asset)
        if query:
            like = f"%{query}%"
            stmt = stmt.where(
                (Asset.asset_tag.ilike(like))
                | (Asset.serial_number.ilike(like))
                | (Asset.qr_code_value.ilike(like))
                | (Asset.name.ilike(like))
            )
        if category_id is not None:
            stmt = stmt.where(Asset.category_id == category_id)
        if department_id is not None:
            stmt = stmt.where(Asset.department_id == department_id)
        if status is not None:
            stmt = stmt.where(Asset.status == status)
        if location is not None:
            stmt = stmt.where(Asset.location.ilike(f"%{location}%"))
        if is_bookable is not None:
            stmt = stmt.where(Asset.is_bookable == is_bookable)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, **fields) -> Asset:
        asset = Asset(**fields)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def save(self, asset: Asset) -> Asset:
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def add_status_history(
        self, *, asset_id: int, from_status, to_status, changed_by_id: int, reason: str | None
    ) -> AssetStatusHistory:
        entry = AssetStatusHistory(
            asset_id=asset_id,
            from_status=from_status,
            to_status=to_status,
            changed_by_id=changed_by_id,
            reason=reason,
        )
        self.db.add(entry)
        return entry  # NOT committed here — caller commits as part of one transaction

    def get_status_history(self, asset_id: int) -> list[AssetStatusHistory]:
        return list(
            self.db.scalars(
                select(AssetStatusHistory)
                .where(AssetStatusHistory.asset_id == asset_id)
                .order_by(AssetStatusHistory.changed_at.desc())
            ).all()
        )