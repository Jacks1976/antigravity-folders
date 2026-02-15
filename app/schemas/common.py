"""
Common response schemas.
"""
from pydantic import BaseModel
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    ok: bool
    data: Optional[T] = None
    error_key: Optional[str] = None

