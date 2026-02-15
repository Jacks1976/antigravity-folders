"""Worship scheduling router."""
from fastapi import APIRouter, Depends
from app.schemas.common import ResponseEnvelope
from app.schemas.worship import (
    ServicePlanCreateRequest, SetlistSongAddRequest,
    RosterAssignRequest, RosterStatusUpdateRequest
)
from app.core.dependencies import require_active_user
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from execution.music_scheduling.core import (
    create_service_plan_core, add_setlist_song_core,
    assign_roster_entry_core, update_roster_status_core, list_plans_core
)

router = APIRouter(prefix="/worship/schedule", tags=["worship-schedule"])

@router.post("/plans", response_model=ResponseEnvelope)
async def create_plan(
    request: ServicePlanCreateRequest,
    current_user: dict = Depends(require_active_user)
):
    """Create a new service plan."""
    result = create_service_plan_core(
        creator_id=current_user['id'],
        date=request.date,
        event_id=request.event_id,
        notes=request.notes
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.get("/plans", response_model=ResponseEnvelope)
async def list_plans(
    from_date: str = None,
    to_date: str = None,
    current_user: dict = Depends(require_active_user)
):
    """List service plans with optional date range."""
    result = list_plans_core(current_user['id'], from_date, to_date)
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.post("/plans/{plan_id}/setlist", response_model=ResponseEnvelope)
async def add_setlist_song(
    plan_id: int,
    request: SetlistSongAddRequest,
    current_user: dict = Depends(require_active_user)
):
    """Add song to service setlist."""
    result = add_setlist_song_core(
        adder_id=current_user['id'],
        plan_id=plan_id,
        song_id=request.song_id,
        order_index=request.order_index
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.post("/plans/{plan_id}/roster", response_model=ResponseEnvelope)
async def assign_roster(
    plan_id: int,
    request: RosterAssignRequest,
    current_user: dict = Depends(require_active_user)
):
    """Assign musician to roster."""
    result = assign_roster_entry_core(
        assigner_id=current_user['id'],
        plan_id=plan_id,
        musician_id=request.musician_id,
        instrument=request.instrument
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.post("/roster/{roster_id}/status", response_model=ResponseEnvelope)
async def update_roster_status(
    roster_id: int,
    request: RosterStatusUpdateRequest,
    current_user: dict = Depends(require_active_user)
):
    """Update roster entry status."""
    # Check if user is worship lead (simplified - would check ministry_assignments in production)
    is_lead = current_user.get('role') in ['Admin', 'Staff']
    
    result = update_roster_status_core(
        updater_id=current_user['id'],
        roster_id=roster_id,
        status=request.status,
        is_lead=is_lead
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )
