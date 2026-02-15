"""
Members router - handles member management endpoints.
All endpoints return HTTP 200 with response envelope.
"""
from fastapi import APIRouter, Depends, Query, Response
from app.schemas.members import UpdateProfileRequest, AssignMinistryRequest
from app.services import members_service
from app.core.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/members", tags=["members"])

@router.get("/directory")
async def get_directory(
    search: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user),
    response: Response = None
):
    """Get member directory (Active users only) with search and pagination."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    viewer_id = current_user['sub']
    result = members_service.get_directory(viewer_id, page=1, limit=limit, search=search, offset=offset)
    response.status_code = 200
    return result

@router.patch("/me")
async def update_me(req: UpdateProfileRequest, current_user: dict = Depends(get_current_active_user), response: Response = None):
    """Update own profile."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    user_id = current_user['sub']
    updates = req.model_dump(exclude_unset=True)
    result = members_service.update_profile(user_id, updates)
    response.status_code = 200
    return result

@router.post("/assign-ministry")
async def assign_ministry(req: AssignMinistryRequest, current_user: dict = Depends(get_current_admin_user), response: Response = None):
    """Assign user to ministry (Admin only)."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    admin_id = current_user['sub']
    result = members_service.assign_ministry(admin_id, req.user_id, req.ministry_id, req.role, req.is_lead)
    response.status_code = 200
    return result
