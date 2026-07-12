"""Raw DB access for AssetTransferRequest — no business rules."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.transfer import AssetTransferRequest
from models.enums import TransferStatusEnum


class TransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transfer: AssetTransferRequest) -> AssetTransferRequest:
        self.db.add(transfer)
        self.db.flush()
        return transfer

    def get_by_id(self, transfer_id: int) -> Optional[AssetTransferRequest]:
        return self.db.get(AssetTransferRequest, transfer_id)

    def list_filtered(
        self,
        asset_id: Optional[int] = None,
        status: Optional[TransferStatusEnum] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[AssetTransferRequest]:
        stmt = select(AssetTransferRequest)
        if asset_id is not None:
            stmt = stmt.where(AssetTransferRequest.asset_id == asset_id)
        if status is not None:
            stmt = stmt.where(AssetTransferRequest.status == status)
        stmt = stmt.order_by(AssetTransferRequest.created_at.desc()).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()