"""
Domain enums.

DATABASE RULE: use enums instead of free-text strings wherever the set of
values is closed and business-meaningful (statuses, roles, priorities).
Each of these becomes a native PostgreSQL ENUM type via SQLAlchemy's
Enum(..., native_enum=True), which means:
  - invalid values are rejected at the DB layer, not just in Pydantic
  - the state machine's legal states are visible directly in \\d+ on the table
  - ALTER TYPE ... ADD VALUE handles future growth without a data migration

str + Enum inheritance keeps these JSON-serializable for free, so Pydantic
schemas and FastAPI responses don't need a separate mapping layer.
"""
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    ASSET_MANAGER = "asset_manager"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"


class ActiveStatusEnum(str, enum.Enum):
    """Generic active/inactive - used by users, departments, categories."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class AssetConditionEnum(str, enum.Enum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"


class AssetStatusEnum(str, enum.Enum):
    """The asset lifecycle state machine. Legal transitions are enforced
    in the service layer (see AssetLifecycleService) - the DB only
    guarantees the value is one of these seven."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    UNDER_MAINTENANCE = "under_maintenance"
    LOST = "lost"
    RETIRED = "retired"
    DISPOSED = "disposed"


class AllocationStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"


class TransferStatusEnum(str, enum.Enum):
    REQUESTED = "requested"
    DEPT_HEAD_APPROVED = "dept_head_approved"
    ASSET_MANAGER_APPROVED = "asset_manager_approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class BookingStatusEnum(str, enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenancePriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TECHNICIAN_ASSIGNED = "technician_assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class AuditCycleStatusEnum(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class AuditItemStatusEnum(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    MISSING = "missing"
    DAMAGED = "damaged"


class NotificationTypeEnum(str, enum.Enum):
    ALLOCATION = "allocation"
    TRANSFER = "transfer"
    MAINTENANCE = "maintenance"
    BOOKING = "booking"
    AUDIT = "audit"
    OVERDUE_RETURN = "overdue_return"
