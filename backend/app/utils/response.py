"""
Standard API response envelope.

Why this exists: Rajdeep (frontend integration) needs one predictable shape
to parse, regardless of which module or which of us wrote the endpoint.
Without this, every router ends up improvising its own success/error
format, and every frontend service file needs bespoke unwrapping logic.

Convention:
    Success -> {"success": true,  "data": <payload>, "meta": <optional>}
    Error   -> {"success": false, "error": {"code": str, "message": str}}

`meta` is used for pagination info (page, page_size, total, total_pages)
and is omitted (None) for non-paginated responses.
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: PaginationMeta | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


def success_envelope(data: Any, meta: PaginationMeta | None = None) -> dict:
    """Build a success envelope dict directly (used inside routers)."""
    payload: dict[str, Any] = {"success": True, "data": data}
    if meta is not None:
        payload["meta"] = meta.model_dump()
    return payload


def error_envelope(code: str, message: str) -> dict:
    """Build an error envelope dict directly (used by the global exception handler)."""
    return {"success": False, "error": {"code": code, "message": message}}
