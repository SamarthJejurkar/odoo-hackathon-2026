"""
Authentication dependency: resolves the current user from the JWT Bearer
token on every protected request.

*** TEMPORARY: imports UserDraft (see app/models/user_draft.py) ***
Swap this import to the real User model the moment Tanmay's version lands.
Nothing outside this file (routers, services) should need to change when
that swap happens — they only ever depend on `get_current_user`, never on
the model directly.

Security notes:
  - We re-fetch the user from the DB on every request (not just trusting
    the token's `role` claim) so a role change or deactivation takes
    effect immediately, not only after the token expires.
  - Inactive/suspended users are rejected even with a technically-valid
    token.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.core.enums import UserStatus
from app.dependencies.database import get_db
from app.models.user_draft import UserDraft  # TEMPORARY — see docstring

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserDraft:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Token missing subject claim")

    user = db.query(UserDraft).filter(UserDraft.id == int(user_id)).first()
    if user is None:
        raise UnauthorizedException("User not found")

    if user.status != UserStatus.ACTIVE:
        raise UnauthorizedException("User account is not active")

    return user
