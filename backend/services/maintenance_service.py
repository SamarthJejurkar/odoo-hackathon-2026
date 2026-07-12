"""
Business logic for MaintenanceRequest.

Approve/Resolve are the only two stages that touch Asset.status, both
via AssetLifecycleService.transition() in the same session as this
row's own status update — one commit per operation, same pattern as
Allocation/Booking.

NOTE (flagged to Samarth, not silently worked around): maintenance can
currently only be raised against an AVAILABLE asset, because
AssetLifecycleService._ALLOWED_TRANSITIONS has no ALLOCATED ->
UNDER_MAINTENANCE edge. See chat history for the Option A/B discussion —
Option A (this) was chosen for now; revisit if the brief needs an
allocated asset to go straight into maintenance.
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException, ValidationException
from models.asset import Asset
from models.enums import AssetStatusEnum, MaintenanceStatusEnum
from models.maintenance import MaintenanceRequest
from models.user import User
from repositories.maintenance_repository import MaintenanceRepository
from schemas.maintenance import (
    MaintenanceRejection,
    MaintenanceRequestCreate,
    MaintenanceResolution,
    TechnicianAssignment,
)
from services.asset_lifecycle_service import AssetLifecycleService

import datetime as dt


class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaintenanceRepository(db)
        self.lifecycle = AssetLifecycleService(db)

    def _require_status(self, request: MaintenanceRequest, expected: MaintenanceStatusEnum) -> None:
        if request.status != expected:
            raise ValidationException(
                f"Maintenance request {request.id} must be in '{expected.value}' state for this action "
                f"(currently '{request.status.value}')."
            )

    def create_request(self, payload: MaintenanceRequestCreate, actor: User) -> MaintenanceRequest:
        asset = self.db.get(Asset, payload.asset_id)
        if asset is None:
            raise NotFoundException(f"Asset {payload.asset_id} not found.")
        if asset.status != AssetStatusEnum.AVAILABLE:
            raise ValidationException(
                f"Asset {asset.asset_tag} is '{asset.status.value}'. Maintenance can only be requested "
                "for an AVAILABLE asset (return or resolve any active allocation/booking first)."
            )

        request = MaintenanceRequest(
            asset_id=payload.asset_id,
            raised_by_id=actor.id,
            issue_description=payload.issue_description,
            priority=payload.priority,
            photo_url=payload.photo_url,
            status=MaintenanceStatusEnum.PENDING,
        )
        self.repo.create(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def approve(self, request_id: int, actor: User) -> MaintenanceRequest:
        request = self.repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException(f"Maintenance request {request_id} not found.")
        self._require_status(request, MaintenanceStatusEnum.PENDING)

        request.approved_by_id = actor.id
        request.approved_at = dt.datetime.utcnow()
        request.status = MaintenanceStatusEnum.APPROVED

        self.lifecycle.transition(
            asset_id=request.asset_id,
            to_status=AssetStatusEnum.UNDER_MAINTENANCE,
            changed_by_id=actor.id,
            reason=f"Approved maintenance request #{request.id}",
        )
        # transition() commits internally — no separate commit here.
        self.db.refresh(request)
        return request

    def reject(self, request_id: int, payload: MaintenanceRejection, actor: User) -> MaintenanceRequest:
        request = self.repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException(f"Maintenance request {request_id} not found.")
        self._require_status(request, MaintenanceStatusEnum.PENDING)

        request.status = MaintenanceStatusEnum.REJECTED
        request.rejection_reason = payload.rejection_reason
        self.db.commit()
        self.db.refresh(request)
        return request

    def assign_technician(self, request_id: int, payload: TechnicianAssignment, actor: User) -> MaintenanceRequest:
        request = self.repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException(f"Maintenance request {request_id} not found.")
        self._require_status(request, MaintenanceStatusEnum.APPROVED)

        request.technician_name = payload.technician_name
        request.assigned_at = dt.datetime.utcnow()
        request.status = MaintenanceStatusEnum.TECHNICIAN_ASSIGNED
        self.db.commit()
        self.db.refresh(request)
        return request

    def start_work(self, request_id: int, actor: User) -> MaintenanceRequest:
        request = self.repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException(f"Maintenance request {request_id} not found.")
        self._require_status(request, MaintenanceStatusEnum.TECHNICIAN_ASSIGNED)

        request.started_at = dt.datetime.utcnow()
        request.status = MaintenanceStatusEnum.IN_PROGRESS
        self.db.commit()
        self.db.refresh(request)
        return request

    def resolve(self, request_id: int, payload: MaintenanceResolution, actor: User) -> MaintenanceRequest:
        request = self.repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException(f"Maintenance request {request_id} not found.")
        self._require_status(request, MaintenanceStatusEnum.IN_PROGRESS)

        request.resolved_at = dt.datetime.utcnow()
        request.resolution_notes = payload.resolution_notes
        request.status = MaintenanceStatusEnum.RESOLVED

        self.lifecycle.transition(
            asset_id=request.asset_id,
            to_status=payload.resulting_status,
            changed_by_id=actor.id,
            reason=f"Resolved maintenance request #{request.id}",
        )
        # transition() commits internally — no separate commit here.
        self.db.refresh(request)
        return request

    def get_request(self, request_id: int) -> MaintenanceRequest:
        request = self.repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException(f"Maintenance request {request_id} not found.")
        return request

    def list_requests(
        self,
        asset_id: Optional[int] = None,
        status: Optional[MaintenanceStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[MaintenanceRequest]:
        return self.repo.list_filtered(asset_id, status, skip, limit)