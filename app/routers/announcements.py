"""
Announcements router - handles announcement endpoints.
All endpoints return HTTP 200 with response envelope.
"""
from fastapi import APIRouter, Depends, Query, Response
from app.schemas.announcements import PostAnnouncementRequest
from app.services import announcements_service
from app.core.dependencies import get_current_active_user, get_org_context
from fastapi import Query

router = APIRouter(prefix="/announcements", tags=["announcements"])

@router.post("/")
async def post_announcement(req: PostAnnouncementRequest, current_user: dict = Depends(get_current_active_user), org_id: int | None = Depends(get_org_context), response: Response = None):
    """Post announcement (Admin/Lead based on target)."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    actor_id = current_user['sub']
    actor_role = current_user['role']
    org_id = current_user.get('org')
    
    result = announcements_service.post_announcement(
        actor_id, actor_role, req.title, req.body,
        req.target_type, req.target_id, req.expires_at, req.is_pinned, org_id
    )
    response.status_code = 200
    return result

@router.get("/feed")
async def get_feed(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    org_id: int | None = Depends(get_org_context),
    current_user: dict = Depends(get_current_active_user),
    response: Response = None
):
    """Get announcement feed (Active users only) with pagination."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    user_id = current_user['sub']
    user_role = current_user['role']

    result = announcements_service.get_feed(user_id, user_role, limit, offset, org_id)
    response.status_code = 200
    return result
