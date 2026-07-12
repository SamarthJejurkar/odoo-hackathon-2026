"""
Shared enums.

Master Prompt rule: "Use enums instead of strings where applicable."

IMPORTANT — Role is backend-authoritative:
Permission decisions are NEVER made from a role the frontend claims to have.
A user's role is only ever trusted when it comes from (a) the validated JWT
payload, or (b) a fresh DB lookup. See app/dependencies/rbac.py.

Placed in core/ rather than models/ because these enums are vocabulary
shared by models, schemas, and services alike — keeping them here avoids
circular imports once Tanmay's models start referencing them too.
"""

from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    ASSET_MANAGER = "asset_manager"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"


class UserStatus(str, Enum):
    """Soft-delete / lifecycle status for the User entity (never hard-delete)."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AssetStatus(str, Enum):
    """
    Declared here now (ahead of the Asset module build) so schemas/services
    can reference a stable import path. Final ownership of the Asset model
    itself is Tanmay's per the ER diagram.
    """
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    UNDER_MAINTENANCE = "under_maintenance"
    LOST = "lost"
    RETIRED = "retired"
    DISPOSED = "disposed"
