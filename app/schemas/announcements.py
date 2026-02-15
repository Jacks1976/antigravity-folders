"""
Announcements-related request/response schemas.
"""
from pydantic import BaseModel
from typing import Optional

class PostAnnouncementRequest(BaseModel):
    title: str
    body: Optional[str] = None
    target_type: str = 'Global'  # Global, Role, Ministry
    target_id: Optional[str] = None
    expires_at: Optional[str] = None
    is_pinned: bool = False
