"""
Members-related request/response schemas.
"""
from pydantic import BaseModel
from typing import Optional

class UpdateProfileRequest(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[str] = None
    bio: Optional[str] = None
    share_phone: Optional[bool] = None
    profile_pic_url: Optional[str] = None

class AssignMinistryRequest(BaseModel):
    user_id: int
    ministry_id: int
    role: str
    is_lead: bool = False
