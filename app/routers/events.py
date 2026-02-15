"""
Events router - handles event management endpoints.
All endpoints return HTTP 200 with response envelope.
Timestamps are interpreted as UTC (ISO-8601 with Z suffix preferred).
"""
from fastapi import APIRouter, Depends, Path, Query, Response
from app.schemas.events import CreateEventRequest, RSVPRequest
from app.services import events_service
from app.core.dependencies import get_current_admin_user, get_current_active_user, get_optional_user, get_org_context
from fastapi import Query

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/")
async def create_event(req: CreateEventRequest, current_user: dict = Depends(get_current_admin_user), org_id: int | None = Depends(get_org_context), response: Response = None):
    """Create event (Admin only). Timestamps are UTC."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    admin_id = current_user['sub']
    org_id: int | None = Depends(get_org_context)
    result = events_service.create_event(
        admin_id, req.title, req.start_at, req.end_at,
        req.description, req.location, req.is_public, req.target_ministry_ids, org_id
    )
    response.status_code = 200
    return result

@router.get("/")
async def list_events(
    from_date: str = Query(None, alias="from", description="UTC ISO-8601 timestamp"),
    to_date: str = Query(None, alias="to", description="UTC ISO-8601 timestamp"),
    org_id: int | None = Depends(get_org_context),
    current_user: dict = Depends(get_optional_user),
    response: Response = None
):
    """List events (token optional, filters by status and date range). Timestamps are UTC."""
    viewer_id = current_user['sub'] if current_user else None
    org_id: int | None = Depends(get_org_context)

    result = events_service.list_events(viewer_id, from_date, to_date, org_id)
    response.status_code = 200
    return result

@router.post("/{event_id}/rsvp")
async def rsvp_event(
    event_id: int = Path(...),
    req: RSVPRequest = ...,
    current_user: dict = Depends(get_current_active_user),
    response: Response = None
):
    """RSVP to event (Active users only)."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    user_id = current_user['sub']
    result = events_service.rsvp_event(user_id, event_id, req.status)
    response.status_code = 200
    return result
