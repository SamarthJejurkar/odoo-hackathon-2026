from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from schemas.user import UserCreate
from schemas.auth import LoginRequest
from core.security import verify_password, create_access_token
from core.exceptions import ConflictException, UnauthorizedException, ForbiddenException
from models.enums import ActiveStatusEnum


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, payload: UserCreate):
        if self.repo.get_by_email(payload.email):
            raise ConflictException("A user with this email already exists.")
        return self.repo.create(
            full_name=payload.full_name,
            email=payload.email,
            password=payload.password,
            department_id=payload.department_id,
        )

    def login(self, payload: LoginRequest):
        user = self.repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password.")
        if user.status != ActiveStatusEnum.ACTIVE:
            raise ForbiddenException("This account has been deactivated.")
        token = create_access_token(subject=str(user.id), role=user.role.value)
        return token, user