"""
Auth router - handles authentication endpoints.
All endpoints return HTTP 200 with response envelope.
"""
from fastapi import APIRouter, Depends, Response
from app.schemas.auth import RegisterRequest, LoginRequest, ApproveRequest
from app.services import auth_service
from app.core.dependencies import get_current_admin_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(req: RegisterRequest, response: Response):
    """Register a new user."""
    result = auth_service.register_user(req.email, req.password, req.full_name, getattr(req, 'organization_slug', None))
    response.status_code = 200
    return result

@router.post("/login")
async def login(req: LoginRequest, response: Response):
    """Login and get JWT token."""
    result = auth_service.login_user(req.email, req.password, getattr(req, 'organization_slug', None))
    response.status_code = 200
    return result

@router.post("/approve")
async def approve(req: ApproveRequest, current_user: dict = Depends(get_current_admin_user), response: Response = None):
    """Approve a pending user (Admin only)."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    admin_id = current_user['sub']
    result = auth_service.approve_user(admin_id, req.email)
    response.status_code = 200
    return result
