"""
Custom exception hierarchy for AssetFlow.
Raise these from services/dependencies instead of raw HTTPException,
so every error response goes through the same JSON envelope
(see utils/response.py) instead of FastAPI's default {"detail": ...}.

`detail` is an optional structured payload for cases where the message
string alone isn't enough for the frontend to act on — e.g. a 409 that
needs to name exactly who currently holds a conflicting resource.
"""
from typing import Any, Optional


class AppException(Exception):
    """Base class for all application-level errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.", detail: Optional[Any] = None):
        super().__init__(message, status_code=404, error_code="NOT_FOUND", detail=detail)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists.", detail: Optional[Any] = None):
        super().__init__(message, status_code=409, error_code="CONFLICT", detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Could not validate credentials.", detail: Optional[Any] = None):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED", detail=detail)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action.", detail: Optional[Any] = None):
        super().__init__(message, status_code=403, error_code="FORBIDDEN", detail=detail)


class ValidationException(AppException):
    def __init__(self, message: str = "Invalid request data.", detail: Optional[Any] = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR", detail=detail)