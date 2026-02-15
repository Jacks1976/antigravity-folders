"""
Events-related request/response schemas.
"""
from pydantic import BaseModel
from typing import Optional, List

class CreateEventRequest(BaseModel):
    title: str
    start_at: str
    end_at: str
    description: Optional[str] = None
    location: Optional[str] = None
    is_public: bool = False
    target_ministry_ids: Optional[List[int]] = None

class RSVPRequest(BaseModel):
    status: str  # going, maybe, not_going
