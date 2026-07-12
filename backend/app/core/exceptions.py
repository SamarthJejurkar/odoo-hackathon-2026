"""
Custom exception hierarchy.

Master Prompt rule: "Never expose internal errors. Return meaningful error
messages." Services should never let a raw SQLAlchemy/Python exception
bubble up to the client. Instead, services raise one of these, and a single
global exception handler (registered in app/main.py) converts it into the
standard response envelope with the correct HTTP status code.

This keeps routers thin: they never need try/except for business errors —
that translation happens in exactly one place, application-wide.
"""


class AppException(Exception):
    """Base class for all deliberate, business-meaningful exceptions."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(message)


class NotFoundException(AppException):
    status_code = 404
    error_code = "not_found"


class ValidationException(AppException):
    """Business rule / invariant violation (e.g. invalid asset state transition)."""
    status_code = 422
    error_code = "validation_error"


class ConflictException(AppException):
    """Duplicate resource, overlapping booking, concurrent state change, etc."""
    status_code = 409
    error_code = "conflict"


class UnauthorizedException(AppException):
    """Missing or invalid credentials (not logged in / bad or expired token)."""
    status_code = 401
    error_code = "unauthorized"


class ForbiddenException(AppException):
    """Authenticated, but not permitted to perform this action (RBAC failure)."""
    status_code = 403
    error_code = "forbidden"
