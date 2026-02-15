"""
Events router - handles event management endpoints.
All endpoints return HTTP 200 with response envelope.
Timestamps are interpreted as UTC (ISO-8601 with Z suffix preferred).
"""
from fastapi import APIRouter, Depends, Path, Query, Response
from app.schemas.events import EventCreate, EventUpdate, EventInDB
from app.schemas.rsvp import RSVPCreate, RSVPInDB
from app.services import events_service
from app.core.dependencies import get_current_admin_user, get_current_active_user, get_optional_user, get_org_context
from fastapi import Query
from typing import Optional, List

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventInDB)
async def create_event(
    req: EventCreate,
    current_user: dict = Depends(get_current_admin_user),
    org_id: Optional[int] = Depends(get_org_context),
    response: Response = None
):
    """Create event (Admin only). Timestamps are UTC."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    admin_id = current_user['sub']
    result = events_service.create_event(
        admin_id, 
        req.title, 
        req.start_time,  # Mudado de start_at para start_time
        req.end_time,    # Mudado de end_at para end_time
        req.description, 
        req.location, 
        True,  # is_public (ajuste conforme necessário)
        None,  # target_ministry_ids (ajuste conforme necessário)
        org_id
    )
    response.status_code = 200
    return result

@router.get("/", response_model=List[EventInDB])
async def list_events(
    from_date: str = Query(None, alias="from", description="UTC ISO-8601 timestamp"),
    to_date: str = Query(None, alias="to", description="UTC ISO-8601 timestamp"),
    org_id: Optional[int] = Depends(get_org_context),
    current_user: dict = Depends(get_optional_user),
    response: Response = None
):
    """List events (token optional, filters by status and date range). Timestamps are UTC."""
    viewer_id = current_user['sub'] if current_user else None
    
    result = events_service.list_events(viewer_id, from_date, to_date, org_id)
    response.status_code = 200
    return result

@router.post("/{event_id}/rsvp", response_model=RSVPInDB)
async def rsvp_event(
    event_id: int = Path(...),
    req: RSVPCreate = None,
    current_user: dict = Depends(get_current_active_user),
    response: Response = None
):
    """RSVP to event (Active users only)."""
    # Check for auth error
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    user_id = current_user['sub']
    
    # Se não veio req, criar um padrão
    if req is None:
        req = RSVPCreate(event_id=event_id, status="confirmed", guests_count=1)
    else:
        req.event_id = event_id
    
    result = events_service.rsvp_event(user_id, event_id, req.status)
    response.status_code = 200
    return result

@router.get("/{event_id}", response_model=EventInDB)
async def get_event(
    event_id: int = Path(...),
    current_user: dict = Depends(get_optional_user),
    response: Response = None
):
    """Get event details by ID."""
    viewer_id = current_user['sub'] if current_user else None
    result = events_service.get_event_by_id(event_id, viewer_id)
    response.status_code = 200
    return result

@router.put("/{event_id}", response_model=EventInDB)
async def update_event(
    event_id: int = Path(...),
    req: EventUpdate = None,
    current_user: dict = Depends(get_current_admin_user),
    response: Response = None
):
    """Update event (Admin only)."""
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    admin_id = current_user['sub']
    result = events_service.update_event(event_id, admin_id, req.dict(exclude_unset=True))
    response.status_code = 200
    return result

@router.delete("/{event_id}")
async def delete_event(
    event_id: int = Path(...),
    current_user: dict = Depends(get_current_admin_user),
    response: Response = None
):
    """Delete event (Admin only)."""
    if current_user.get("_error"):
        response.status_code = 200
        return current_user
    
    admin_id = current_user['sub']
    result = events_service.delete_event(event_id, admin_id)
    response.status_code = 200
    return result