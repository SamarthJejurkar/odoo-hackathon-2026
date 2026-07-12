"""
Business logic for Audit Cycles.

Item generation (start_cycle) queries assets in scope and bulk-inserts
PENDING AuditItem rows — idempotent thanks to the unique(audit_cycle_id,
asset_id) constraint, so re-running start on an already-started cycle
just skips assets that already have an item instead of erroring.

close_cycle() is the one place this module writes to Asset.status —
each MISSING item independently attempts AVAILABLE/ALLOCATED/etc -> LOST
via AssetLifecycleService. A per-item ValidationException (e.g. an
asset in RESERVED, which has no -> LOST edge) does NOT abort the whole
close; it's collected and returned so nothing is silently lost.

DAMAGED items are recorded but intentionally NOT auto-transitioned —
not specified in the model's own docstring, so not invented here. See
chat history if this needs to change.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from models.asset import Asset
from models.audit import AuditCycle, AuditCycleAuditor, AuditItem
from models.department import Department
from models.enums import AssetStatusEnum, AuditCycleStatusEnum, AuditItemStatusEnum, RoleEnum
from models.user import User
from repositories.audit_repository import AuditRepository
from schemas.audit import AuditCycleCreate, AuditItemVerify
from services.asset_lifecycle_service import AssetLifecycleService


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditRepository(db)
        self.lifecycle = AssetLifecycleService(db)

    def create_cycle(self, payload: AuditCycleCreate, actor: User) -> AuditCycle:
        if payload.scope_department_id is not None:
            if self.db.get(Department, payload.scope_department_id) is None:
                raise NotFoundException(f"Department {payload.scope_department_id} not found.")

        cycle = AuditCycle(
            name=payload.name,
            scope_department_id=payload.scope_department_id,
            scope_location=payload.scope_location,
            start_date=payload.start_date,
            end_date=payload.end_date,
            created_by_id=actor.id,
            status=AuditCycleStatusEnum.PLANNED,
        )
        self.repo.create_cycle(cycle)
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def assign_auditor(self, cycle_id: int, auditor_id: int, actor: User) -> AuditCycleAuditor:
        cycle = self._get_cycle(cycle_id)
        if cycle.status == AuditCycleStatusEnum.CLOSED:
            raise ConflictException(f"Audit cycle {cycle_id} is closed; cannot assign auditors.")
        if self.db.get(User, auditor_id) is None:
            raise NotFoundException(f"User {auditor_id} not found.")
        if self.repo.is_auditor(cycle_id, auditor_id):
            raise ConflictException(f"User {auditor_id} is already an auditor on this cycle.")

        link = AuditCycleAuditor(audit_cycle_id=cycle_id, auditor_id=auditor_id)
        self.repo.add_auditor(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def start_cycle(self, cycle_id: int, actor: User) -> AuditCycle:
        cycle = self._get_cycle(cycle_id)
        if cycle.status != AuditCycleStatusEnum.PLANNED:
            raise ValidationException(
                f"Audit cycle must be PLANNED to start (currently '{cycle.status.value}')."
            )

        in_scope_assets = self.repo.assets_in_scope(cycle.scope_department_id, cycle.scope_location)
        already_present = self.repo.existing_asset_ids_for_cycle(cycle_id)

        new_items = [
            AuditItem(audit_cycle_id=cycle_id, asset_id=asset.id, verification_status=AuditItemStatusEnum.PENDING)
            for asset in in_scope_assets
            if asset.id not in already_present
        ]
        if new_items:
            self.repo.bulk_create_items(new_items)

        cycle.status = AuditCycleStatusEnum.IN_PROGRESS
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def verify_item(self, item_id: int, payload: AuditItemVerify, actor: User) -> AuditItem:
        item = self.repo.get_item(item_id)
        if item is None:
            raise NotFoundException(f"Audit item {item_id} not found.")

        cycle = self._get_cycle(item.audit_cycle_id)
        if cycle.status != AuditCycleStatusEnum.IN_PROGRESS:
            raise ConflictException(
                f"Audit cycle {cycle.id} is '{cycle.status.value}'; items can only be verified while IN_PROGRESS."
            )

        is_assigned_auditor = self.repo.is_auditor(cycle.id, actor.id)
        is_manager = actor.role in (RoleEnum.ADMIN, RoleEnum.ASSET_MANAGER)
        if not (is_assigned_auditor or is_manager):
            raise ForbiddenException("Only an assigned auditor or Asset Manager/Admin can verify audit items.")

        item.verification_status = payload.verification_status
        item.notes = payload.notes
        item.verified_by_id = actor.id
        item.verified_at = dt.datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def close_cycle(self, cycle_id: int, actor: User) -> dict:
        cycle = self._get_cycle(cycle_id)
        if cycle.status != AuditCycleStatusEnum.IN_PROGRESS:
            raise ValidationException(
                f"Audit cycle must be IN_PROGRESS to close (currently '{cycle.status.value}')."
            )

        missing_items = self.repo.list_missing_items(cycle_id)
        transitioned: list[int] = []
        failed: list[dict] = []

        for item in missing_items:
            try:
                self.lifecycle.transition(
                    asset_id=item.asset_id,
                    to_status=AssetStatusEnum.LOST,
                    changed_by_id=actor.id,
                    reason=f"Marked LOST via audit cycle #{cycle.id} ({cycle.name})",
                )
                transitioned.append(item.asset_id)
            except ValidationException as exc:
                # Don't let one asset's illegal transition (e.g. RESERVED -> LOST,
                # which has no edge in _ALLOWED_TRANSITIONS) abort the whole close.
                failed.append({"asset_id": item.asset_id, "reason": exc.message})

        cycle.status = AuditCycleStatusEnum.CLOSED
        cycle.closed_at = dt.datetime.utcnow()
        self.db.commit()
        self.db.refresh(cycle)

        return {
            "cycle": cycle,
            "items_transitioned_to_lost": transitioned,
            "items_transition_failed": failed,
        }

    def _get_cycle(self, cycle_id: int) -> AuditCycle:
        cycle = self.repo.get_cycle(cycle_id)
        if cycle is None:
            raise NotFoundException(f"Audit cycle {cycle_id} not found.")
        return cycle

    def get_cycle(self, cycle_id: int) -> AuditCycle:
        return self._get_cycle(cycle_id)

    def list_cycles(
        self, status: Optional[AuditCycleStatusEnum] = None, skip: int = 0, limit: int = 50
    ) -> Sequence[AuditCycle]:
        return self.repo.list_cycles(status, skip, limit)

    def list_items(
        self,
        cycle_id: int,
        verification_status: Optional[AuditItemStatusEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditItem]:
        self._get_cycle(cycle_id)  # 404 if cycle doesn't exist
        return self.repo.list_items(cycle_id, verification_status, skip, limit)

    def list_auditors(self, cycle_id: int) -> Sequence[AuditCycleAuditor]:
        self._get_cycle(cycle_id)
        return self.repo.list_auditors(cycle_id)