"""
Business logic for AssetTransferRequest.

Completion never touches Asset.status — the asset stays ALLOCATED
throughout a transfer, only the holder changes. Two allocation rows
are written atomically: the old one closed, the new one opened.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException, ValidationException
from models.allocation import AssetAllocation
from models.asset import Asset
from models.department import Department
from models.enums import AllocationStatusEnum, TransferStatusEnum
from models.transfer import AssetTransferRequest
from models.user import User
from repositories.allocation_repository import AllocationRepository
from repositories.transfer_repository import TransferRepository
from schemas.transfer import TransferCreate, TransferRejection


class TransferService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TransferRepository(db)
        self.allocation_repo = AllocationRepository(db)

    def create_transfer(self, payload: TransferCreate, actor: User) -> AssetTransferRequest:
        asset = self.db.get(Asset, payload.asset_id)
        if asset is None:
            raise NotFoundException(f"Asset {payload.asset_id} not found.")

        active_allocation = self.allocation_repo.get_active_for_asset(payload.asset_id)
        if active_allocation is None:
            raise ValidationException(
                f"Asset {asset.asset_tag} has no active allocation to transfer. Allocate it first."
            )

        if payload.requested_to_employee_id is not None:
            if self.db.get(User, payload.requested_to_employee_id) is None:
                raise NotFoundException(f"Employee {payload.requested_to_employee_id} not found.")
            if active_allocation.employee_id == payload.requested_to_employee_id:
                raise ValidationException("Asset is already allocated to this employee.")
        if payload.requested_to_department_id is not None:
            if self.db.get(Department, payload.requested_to_department_id) is None:
                raise NotFoundException(f"Department {payload.requested_to_department_id} not found.")
            if active_allocation.department_id == payload.requested_to_department_id:
                raise ValidationException("Asset is already allocated to this department.")

        transfer = AssetTransferRequest(
            asset_id=payload.asset_id,
            current_allocation_id=active_allocation.id,
            requested_by_id=actor.id,
            requested_to_employee_id=payload.requested_to_employee_id,
            requested_to_department_id=payload.requested_to_department_id,
            reason=payload.reason,
            status=TransferStatusEnum.REQUESTED,
        )
        self.repo.create(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def _get_open_transfer(self, transfer_id: int) -> AssetTransferRequest:
        transfer = self.repo.get_by_id(transfer_id)
        if transfer is None:
            raise NotFoundException(f"Transfer request {transfer_id} not found.")
        if transfer.status in (TransferStatusEnum.COMPLETED, TransferStatusEnum.REJECTED):
            raise ConflictException(
                f"Transfer request {transfer_id} is already '{transfer.status.value}' and cannot be modified."
            )
        return transfer

    def approve_dept_head(self, transfer_id: int, actor: User) -> AssetTransferRequest:
        transfer = self._get_open_transfer(transfer_id)
        if transfer.status != TransferStatusEnum.REQUESTED:
            raise ValidationException(
                f"Transfer must be in REQUESTED state for dept-head approval (currently '{transfer.status.value}')."
            )
        transfer.dept_head_approved_by_id = actor.id
        transfer.dept_head_approved_at = datetime.utcnow()
        transfer.status = TransferStatusEnum.DEPT_HEAD_APPROVED
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def approve_asset_manager(self, transfer_id: int, actor: User) -> AssetTransferRequest:
        transfer = self._get_open_transfer(transfer_id)
        if transfer.status != TransferStatusEnum.DEPT_HEAD_APPROVED:
            raise ValidationException(
                "Transfer must have Department Head approval before Asset Manager approval "
                f"(currently '{transfer.status.value}')."
            )
        transfer.asset_manager_approved_by_id = actor.id
        transfer.asset_manager_approved_at = datetime.utcnow()
        transfer.status = TransferStatusEnum.ASSET_MANAGER_APPROVED

        self._complete_transfer(transfer, actor)

        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def _complete_transfer(self, transfer: AssetTransferRequest, actor: User) -> None:
        old_allocation = self.allocation_repo.get_by_id(transfer.current_allocation_id)
        if old_allocation is None or old_allocation.status != AllocationStatusEnum.ACTIVE:
            raise ConflictException(
                "The allocation backing this transfer is no longer active — it may have been "
                "returned independently. Reject this transfer and re-allocate manually."
            )

        old_allocation.status = AllocationStatusEnum.RETURNED
        old_allocation.returned_at = datetime.utcnow()
        old_allocation.return_notes = f"Closed by transfer request #{transfer.id}."

        new_allocation = AssetAllocation(
            asset_id=transfer.asset_id,
            employee_id=transfer.requested_to_employee_id,
            department_id=transfer.requested_to_department_id,
            allocated_by_id=actor.id,
            allocated_at=datetime.utcnow(),
            expected_return_date=old_allocation.expected_return_date,
            status=AllocationStatusEnum.ACTIVE,
        )
        self.db.add(new_allocation)
        self.db.flush()

        transfer.status = TransferStatusEnum.COMPLETED
        transfer.completed_at = datetime.utcnow()

    def reject(self, transfer_id: int, payload: TransferRejection, actor: User) -> AssetTransferRequest:
        transfer = self._get_open_transfer(transfer_id)
        transfer.status = TransferStatusEnum.REJECTED
        transfer.rejection_reason = payload.rejection_reason
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def get_transfer(self, transfer_id: int) -> AssetTransferRequest:
        transfer = self.repo.get_by_id(transfer_id)
        if transfer is None:
            raise NotFoundException(f"Transfer request {transfer_id} not found.")
        return transfer

    def list_transfers(
        self,
        asset_id: Optional[int] = None,
        status: Optional[TransferStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[AssetTransferRequest]:
        return self.repo.list_filtered(asset_id, status, skip, limit)