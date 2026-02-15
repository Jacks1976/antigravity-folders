"""Worship-related Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List

# File/Asset schemas
class AssetUploadRequest(BaseModel):
    filename: str

class AssetUploadResponse(BaseModel):
    asset_id: int
    message: str

class AssetLinkResponse(BaseModel):
    download_url: str
    filename: str
    mime_type: str

# Music Repertoire schemas
class SongCreateRequest(BaseModel):
    title: str
    artist: Optional[str] = None
    bpm: Optional[int] = None
    default_key: Optional[str] = None

class SongUpdateRequest(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    bpm: Optional[int] = None
    default_key: Optional[str] = None

class SongAssetAddRequest(BaseModel):
    type: str  # 'LINK' or 'FILE'
    url: Optional[str] = None
    asset_id: Optional[int] = None
    label: Optional[str] = None
    instrument_tag_ids: Optional[List[str]] = None

# Music Scheduling schemas
class ServicePlanCreateRequest(BaseModel):
    date: str  # ISO date
    event_id: Optional[int] = None
    notes: Optional[str] = None

class SetlistSongAddRequest(BaseModel):
    song_id: int
    order_index: int

class RosterAssignRequest(BaseModel):
    musician_id: int
    instrument: str

class RosterStatusUpdateRequest(BaseModel):
    status: str  # 'pending', 'confirmed', 'declined'
