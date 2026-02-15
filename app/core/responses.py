"""
Standard response models for consistent API responses.
"""
from typing import Optional, Any
from pydantic import BaseModel

class APIResponse(BaseModel):
    """Standard response envelope for all API endpoints."""
    ok: bool
    data: Optional[Any] = None
    error_key: Optional[str] = None

def success_response(data: Any = None) -> dict:
    """Create a success response."""
    return {"ok": True, "data": data, "error_key": None}

def error_response(error_key: str) -> dict:
    """Create an error response."""
    return {"ok": False, "data": None, "error_key": error_key}
