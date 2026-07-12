"""Raw DB access only — no business rules."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.maintenance import MaintenanceRequest
from models.enums import MaintenanceStatusEnum


class MaintenanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, request: MaintenanceRequest) -> MaintenanceRequest:
        self.db.add(request)
        self.db.flush()
        return request

    def get_by_id(self, request_id: int) -> Optional[MaintenanceRequest]:
        return self.db.get(MaintenanceRequest, request_id)

    def list_filtered(
        self,
        asset_id: Optional[int] = None,
        status: Optional[MaintenanceStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[MaintenanceRequest]:
        stmt = select(MaintenanceRequest)
        if asset_id is not None:
            stmt = stmt.where(MaintenanceRequest.asset_id == asset_id)
        if status is not None:
            stmt = stmt.where(MaintenanceRequest.status == status)
        stmt = stmt.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()