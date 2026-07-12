"""
Auth business logic: registration + login.

Rule from Master Prompt: never reveal WHICH part of a login attempt was
wrong (email vs password) — that's an account-enumeration leak. Both
failure modes return the exact same generic message.
"""

from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user_draft import UserDraft
from app.core.enums import Role, UserStatus
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictException, UnauthorizedException


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register(self, email: str, password: str, role: Role = Role.EMPLOYEE) -> UserDraft:
        existing = self.repo.get_by_email(email)
        if existing:
            raise ConflictException(
                "A user with this email already exists", error_code="email_exists"
            )

        user = UserDraft(
            email=email,
            hashed_password=hash_password(password),
            role=role,
            status=UserStatus.ACTIVE,
        )
        return self.repo.create(user)

    def authenticate(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException("Invalid email or password")

        return create_access_token(subject=str(user.id), role=user.role.value)