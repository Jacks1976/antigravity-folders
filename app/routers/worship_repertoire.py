"""Worship repertoire router."""
from fastapi import APIRouter, Depends
from app.schemas.common import ResponseEnvelope
from app.schemas.worship import SongCreateRequest, SongUpdateRequest, SongAssetAddRequest
from app.core.dependencies import require_active_user
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from execution.music_repertoire.core import (
    create_song_core, update_song_core, list_songs_core,
    add_song_asset_core, remove_song_asset_core
)

router = APIRouter(prefix="/worship/repertoire", tags=["worship-repertoire"])

@router.post("/songs", response_model=ResponseEnvelope)
async def create_song(
    request: SongCreateRequest,
    current_user: dict = Depends(require_active_user)
):
    """Create a new song in repertoire."""
    result = create_song_core(
        creator_id=current_user['id'],
        title=request.title,
        artist=request.artist,
        bpm=request.bpm,
        default_key=request.default_key
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.get("/songs", response_model=ResponseEnvelope)
async def list_songs(
    search: str = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(require_active_user)
):
    """List songs with optional search."""
    result = list_songs_core(current_user['id'], search, limit, offset)
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.patch("/songs/{song_id}", response_model=ResponseEnvelope)
async def update_song(
    song_id: int,
    request: SongUpdateRequest,
    current_user: dict = Depends(require_active_user)
):
    """Update song details."""
    result = update_song_core(
        updater_id=current_user['id'],
        song_id=song_id,
        updates=request.dict(exclude_unset=True)
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.post("/songs/{song_id}/assets", response_model=ResponseEnvelope)
async def add_song_asset(
    song_id: int,
    request: SongAssetAddRequest,
    current_user: dict = Depends(require_active_user)
):
    """Add asset (link or file) to song."""
    result = add_song_asset_core(
        adder_id=current_user['id'],
        song_id=song_id,
        asset_type=request.type,
        url=request.url,
        asset_id=request.asset_id,
        label=request.label,
        instrument_tag_ids=request.instrument_tag_ids
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.delete("/song-assets/{song_asset_id}", response_model=ResponseEnvelope)
async def remove_song_asset(
    song_asset_id: int,
    current_user: dict = Depends(require_active_user)
):
    """Remove song asset."""
    result = remove_song_asset_core(current_user['id'], song_asset_id)
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )
