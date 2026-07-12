"""
Consistent response envelope for the whole API.
"""
from typing import Any, Optional


def success_envelope(data: Any = None, message: str = "Success") -> dict:
    return {"success": True, "message": message, "data": data}


def error_envelope(code: str, message: str, detail: Optional[Any] = None) -> dict:
    payload = {"success": False, "error_code": code, "message": message}
    if detail is not None:
        payload["detail"] = detail
    return payload