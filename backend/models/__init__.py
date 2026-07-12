"""
Import every model here so `from database.database import Base` followed
by `import app.models` registers all tables on Base.metadata. Alembic's
env.py does exactly this before calling autogenerate - if a model isn't
imported somewhere in this chain, autogenerate silently won't see it and
will try to DROP its table on the next migration. This file is the single
place that must stay in sync with the models/ directory.
"""
from models.activity import ActivityLog, Notification
from models.allocation import AssetAllocation
from models.asset import Asset, AssetStatusHistory
from models.audit import AuditCycle, AuditCycleAuditor, AuditItem
from models.booking import Booking
from models.category import AssetCategory
from models.department import Department
from models.maintenance import MaintenanceRequest
from models.transfer import AssetTransferRequest
from models.user import PasswordResetToken, User

__all__ = [
    "ActivityLog",
    "Notification",
    "AssetAllocation",
    "Asset",
    "AssetStatusHistory",
    "AuditCycle",
    "AuditCycleAuditor",
    "AuditItem",
    "Booking",
    "AssetCategory",
    "Department",
    "MaintenanceRequest",
    "AssetTransferRequest",
    "PasswordResetToken",
    "User",
]
