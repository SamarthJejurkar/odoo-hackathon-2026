"""
Security utilities: password hashing and JWT encode/decode.

Uses Tanmay's existing Settings fields exactly as defined
(SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES) — no renaming.

Business rules enforced here:
  - Passwords are never stored or compared in plaintext (bcrypt via passlib).
  - Tokens carry only the minimum claims needed to identify + authorize the
    user (subject id, role) — never sensitive data.
  - Token expiry is always set; there is no "never expires" path.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str, extra_claims: dict[str, Any] | None = None) -> str:
    """
    subject: the user's id (as string) — becomes the JWT `sub` claim.
    role:    the user's Role value at time of issuance. Note this is a
             snapshot — services that need the *current* role for a
             sensitive operation should still re-check against the DB
             rather than trusting a token issued hours ago if the role
             may have changed (see rbac.py notes).
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Raises UnauthorizedException (never a raw JWTError) on any failure —
    expired, malformed, or bad signature all collapse to the same
    client-facing 401 so we don't leak which failure mode occurred.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid or expired authentication token")
