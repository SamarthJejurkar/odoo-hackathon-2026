"""Raw DB access only — no business rules."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.asset import Asset
from models.audit import AuditCycle, AuditCycleAuditor, AuditItem
from models.enums import AssetStatusEnum, AuditCycleStatusEnum, AuditItemStatusEnum


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Cycle ---
    def create_cycle(self, cycle: AuditCycle) -> AuditCycle:
        self.db.add(cycle)
        self.db.flush()
        return cycle

    def get_cycle(self, cycle_id: int) -> Optional[AuditCycle]:
        return self.db.get(AuditCycle, cycle_id)

    def list_cycles(
        self, status: Optional[AuditCycleStatusEnum] = None, skip: int = 0, limit: int = 50
    ) -> Sequence[AuditCycle]:
        stmt = select(AuditCycle)
        if status is not None:
            stmt = stmt.where(AuditCycle.status == status)
        stmt = stmt.order_by(AuditCycle.start_date.desc()).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    # --- Auditors ---
    def add_auditor(self, link: AuditCycleAuditor) -> AuditCycleAuditor:
        self.db.add(link)
        self.db.flush()
        return link

    def list_auditors(self, cycle_id: int) -> Sequence[AuditCycleAuditor]:
        stmt = select(AuditCycleAuditor).where(AuditCycleAuditor.audit_cycle_id == cycle_id)
        return self.db.execute(stmt).scalars().all()

    def is_auditor(self, cycle_id: int, user_id: int) -> bool:
        stmt = select(AuditCycleAuditor).where(
            AuditCycleAuditor.audit_cycle_id == cycle_id,
            AuditCycleAuditor.auditor_id == user_id,
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    # --- Items ---
    def assets_in_scope(self, department_id: Optional[int], location: Optional[str]) -> Sequence[Asset]:
        stmt = select(Asset).where(
            Asset.status.not_in([AssetStatusEnum.RETIRED, AssetStatusEnum.DISPOSED])
        )
        if department_id is not None:
            stmt = stmt.where(Asset.department_id == department_id)
        if location is not None:
            stmt = stmt.where(Asset.location == location)
        return self.db.execute(stmt).scalars().all()

    def bulk_create_items(self, items: list[AuditItem]) -> None:
        self.db.add_all(items)
        self.db.flush()

    def get_item(self, item_id: int) -> Optional[AuditItem]:
        return self.db.get(AuditItem, item_id)

    def list_items(
        self,
        cycle_id: int,
        verification_status: Optional[AuditItemStatusEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditItem]:
        stmt = select(AuditItem).where(AuditItem.audit_cycle_id == cycle_id)
        if verification_status is not None:
            stmt = stmt.where(AuditItem.verification_status == verification_status)
        stmt = stmt.order_by(AuditItem.id.asc()).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def list_missing_items(self, cycle_id: int) -> Sequence[AuditItem]:
        stmt = select(AuditItem).where(
            AuditItem.audit_cycle_id == cycle_id,
            AuditItem.verification_status == AuditItemStatusEnum.MISSING,
        )
        return self.db.execute(stmt).scalars().all()

    def existing_asset_ids_for_cycle(self, cycle_id: int) -> set[int]:
        stmt = select(AuditItem.asset_id).where(AuditItem.audit_cycle_id == cycle_id)
        return set(self.db.execute(stmt).scalars().all())