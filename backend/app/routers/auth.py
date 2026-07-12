"""
Auth router — thin. Validates request shape via Pydantic, calls the
service, wraps the result in the standard response envelope.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserRegisterRequest, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.utils.response import success_envelope
from app.models.user_draft import UserDraft

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(email=payload.email, password=payload.password)
    return success_envelope(UserResponse.model_validate(user).model_dump())


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # NOTE: OAuth2PasswordRequestForm's field is called "username" by the
    # OAuth2 spec itself — we treat it as the email. This is why the
    # Swagger /docs login form shows "username" instead of "email".
    service = AuthService(db)
    token = service.authenticate(email=form_data.username, password=form_data.password)
    return success_envelope(TokenResponse(access_token=token).model_dump())


@router.get("/me")
def me(current_user: UserDraft = Depends(get_current_user)):
    return success_envelope(UserResponse.model_validate(current_user).model_dump())