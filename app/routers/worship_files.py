"""Worship files/assets router."""
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from app.schemas.common import ResponseEnvelope
from app.schemas.worship import AssetUploadResponse, AssetLinkResponse
from app.core.dependencies import require_active_user
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from execution.files.core import upload_asset_core, delete_asset_core, get_asset_path_core, STORAGE_DIR

router = APIRouter(prefix="/worship/files", tags=["worship-files"])

@router.post("/upload", response_model=ResponseEnvelope[AssetUploadResponse])
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_active_user)
):
    """Upload MP3 or PDF file."""
    # Read file content
    content = await file.read()
    
    # Upload
    result = upload_asset_core(
        uploader_id=current_user['id'],
        filename=file.filename,
        file_content=content,
        mime_type=file.content_type
    )
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )

@router.get("/{asset_id}/download")
async def download_file(
    asset_id: int,
    current_user: dict = Depends(require_active_user)
):
    """Download file asset."""
    result = get_asset_path_core(current_user['id'], asset_id)
    
    if not result['ok']:
        return ResponseEnvelope(
            ok=False,
            data=None,
            error_key=result['error_key']
        )
    
    # Return file
    file_path = os.path.join(STORAGE_DIR, result['data']['storage_path'])
    return FileResponse(
        path=file_path,
        filename=result['data']['filename'],
        media_type=result['data']['mime_type']
    )

@router.delete("/{asset_id}", response_model=ResponseEnvelope)
async def delete_file(
    asset_id: int,
    current_user: dict = Depends(require_active_user)
):
    """Delete file asset."""
    result = delete_asset_core(current_user['id'], asset_id)
    
    return ResponseEnvelope(
        ok=result['ok'],
        data=result['data'],
        error_key=result['error_key']
    )
