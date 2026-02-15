"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Auth schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ApproveRequest(BaseModel):
    email: EmailStr

# Members schemas
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

# Events schemas
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

# Announcements schemas
class PostAnnouncementRequest(BaseModel):
    title: str
    body: Optional[str] = None
    target_type: str = 'Global'  # Global, Role, Ministry
    target_id: Optional[str] = None
    expires_at: Optional[str] = None
    is_pinned: bool = False
