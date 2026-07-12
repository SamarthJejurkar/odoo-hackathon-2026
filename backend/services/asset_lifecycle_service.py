"""
The Asset lifecycle state machine. This is the ONLY place status
transitions are validated and applied — no other service should ever
write directly to Asset.status. Other modules (Allocation, Booking,
Maintenance) call transition() to move an asset through its lifecycle
as a side effect of their own workflow.
"""
from sqlalchemy.orm import Session

from repositories.asset_repository import AssetRepository
from models.enums import AssetStatusEnum
from core.exceptions import ValidationException, NotFoundException

# Explicit transition table — the single source of truth for what's legal.
# DISPOSED has no outgoing edges: fully terminal.
_ALLOWED_TRANSITIONS: dict[AssetStatusEnum, set[AssetStatusEnum]] = {
    AssetStatusEnum.AVAILABLE: {
        AssetStatusEnum.ALLOCATED,
        AssetStatusEnum.RESERVED,
        AssetStatusEnum.UNDER_MAINTENANCE,
        AssetStatusEnum.LOST,
        AssetStatusEnum.RETIRED,
    },
    AssetStatusEnum.ALLOCATED: {AssetStatusEnum.AVAILABLE, AssetStatusEnum.LOST},
    AssetStatusEnum.RESERVED: {AssetStatusEnum.AVAILABLE, AssetStatusEnum.ALLOCATED},
    AssetStatusEnum.UNDER_MAINTENANCE: {
        AssetStatusEnum.AVAILABLE,
        AssetStatusEnum.LOST,
        AssetStatusEnum.RETIRED,
        AssetStatusEnum.DISPOSED,
    },
    AssetStatusEnum.LOST: {AssetStatusEnum.AVAILABLE},
    AssetStatusEnum.RETIRED: {AssetStatusEnum.DISPOSED},
    AssetStatusEnum.DISPOSED: set(),
}


class AssetLifecycleService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AssetRepository(db)

    def transition(self, asset_id: int, *, to_status: AssetStatusEnum, changed_by_id: int, reason: str | None = None):
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            raise NotFoundException("Asset not found.")

        from_status = asset.status
        self._validate_transition(from_status, to_status)

        asset.status = to_status
        self.repo.add_status_history(
            asset_id=asset.id,
            from_status=from_status,
            to_status=to_status,
            changed_by_id=changed_by_id,
            reason=reason,
        )
        # Single commit — status change and history write happen atomically.
        return self.repo.save(asset)

    def _validate_transition(self, from_status: AssetStatusEnum, to_status: AssetStatusEnum):
        if from_status == to_status:
            raise ValidationException(f"Asset is already in status '{to_status.value}'.")

        allowed = _ALLOWED_TRANSITIONS.get(from_status, set())
        if to_status not in allowed:
            raise ValidationException(
                f"Cannot transition asset from '{from_status.value}' to '{to_status.value}'. "
                f"Allowed next states: {', '.join(s.value for s in allowed) or 'none (terminal state)'}."
            )