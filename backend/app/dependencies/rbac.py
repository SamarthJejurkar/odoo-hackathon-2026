"""
Role-based access control guard.

Usage in a router:

    @router.post("/assets/{id}/transfer")
    def initiate_transfer(
        ...,
        current_user: UserDraft = Depends(require_roles(Role.ASSET_MANAGER, Role.ADMIN)),
    ):
        ...

Master Prompt rule: "Never trust frontend roles. Always validate
permissions in backend." This is the single enforcement point — every
protected, role-restricted endpoint goes through this, so permission logic
never gets duplicated (or forgotten) inside individual services.
"""

from fastapi import Depends

from app.core.enums import Role
from app.core.exceptions import ForbiddenException
from app.dependencies.auth import get_current_user
from app.models.user_draft import UserDraft  # TEMPORARY — see auth.py docstring


def require_roles(*allowed_roles: Role):
    def dependency(current_user: UserDraft = Depends(get_current_user)) -> UserDraft:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"This action requires one of the following roles: "
                f"{', '.join(r.value for r in allowed_roles)}"
            )
        return current_user

    return dependency
