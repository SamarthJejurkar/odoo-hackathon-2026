from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from database.database import get_db
from core.security import decode_access_token
from core.exceptions import UnauthorizedException, ForbiddenException
from repositories.user_repository import UserRepository
from models.user import User
from models.enums import RoleEnum, ActiveStatusEnum



from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException()
    except JWTError:
        raise UnauthorizedException()

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or user.status != ActiveStatusEnum.ACTIVE:
        raise UnauthorizedException()
    return user


def require_role(*allowed_roles: RoleEnum):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException()
        return current_user
    return checker