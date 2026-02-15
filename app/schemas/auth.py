"""
Auth-related request/response schemas.
"""
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_slug: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    organization_slug: str | None = None

class ApproveRequest(BaseModel):
    email: EmailStr

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

class PasswordResetConfirmSchema(BaseModel):
    token: str
    new_password: str
