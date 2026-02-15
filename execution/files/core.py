"""
Core logic for file/audio asset management.
Handles upload, deletion, and access control for MP3/PDF files.
"""
import os
import hashlib
import secrets
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from audit import log_audit_event

# Storage configuration
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "assets")
MAX_SIZE_MP3 = 20 * 1024 * 1024  # 20MB
MAX_SIZE_PDF = 10 * 1024 * 1024  # 10MB
ALLOWED_MIMES = {
    'audio/mpeg': ('.mp3', MAX_SIZE_MP3),
    'application/pdf': ('.pdf', MAX_SIZE_PDF),
}

# Error keys
ERR_INVALID_FILE_TYPE = "files.invalid_type"
ERR_FILE_TOO_LARGE = "files.too_large"
ERR_UPLOAD_FAILED = "files.upload_failed"
ERR_NOT_FOUND = "files.not_found"
ERR_DELETE_FAILED = "files.delete_failed"
ERR_ACCESS_DENIED = "files.access_denied"

def ensure_storage_dir():
    """Ensure storage directory exists."""
    os.makedirs(STORAGE_DIR, exist_ok=True)

def calculate_checksum(file_content: bytes) -> str:
    """Calculate SHA256 checksum of file content."""
    return hashlib.sha256(file_content).hexdigest()

def generate_storage_path(extension: str) -> str:
    """Generate randomized storage path."""
    random_name = secrets.token_urlsafe(32)
    return f"{random_name}{extension}"

def upload_asset_core(uploader_id: int, filename: str, file_content: bytes, mime_type: str) -> dict:
    """
    Upload a file asset.
    Returns: {ok, data: {asset_id, message}, error_key}
    """
    # Validate mime type
    if mime_type not in ALLOWED_MIMES:
        return {"ok": False, "data": None, "error_key": ERR_INVALID_FILE_TYPE}
    
    extension, max_size = ALLOWED_MIMES[mime_type]
    
    # Validate size
    if len(file_content) > max_size:
        return {"ok": False, "data": None, "error_key": ERR_FILE_TOO_LARGE}
    
    # Ensure storage directory exists
    ensure_storage_dir()
    
    # Generate storage path and checksum
    storage_path = generate_storage_path(extension)
    checksum = calculate_checksum(file_content)
    
    try:
        # Write file to storage
        full_path = os.path.join(STORAGE_DIR, storage_path)
        with open(full_path, 'wb') as f:
            f.write(file_content)
        
        # Insert into database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assets (filename, storage_path, size_bytes, mime_type, checksum, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (filename, storage_path, len(file_content), mime_type, checksum, uploader_id))
            asset_id = cursor.lastrowid
            conn.commit()
        
        # Audit log
        log_audit_event(
            actor_id=uploader_id,
            action_type="ASSET_UPLOAD",
            metadata=f"Uploaded {filename} ({mime_type}, {len(file_content)} bytes)"
        )
        
        return {
            "ok": True,
            "data": {"asset_id": asset_id, "message": "files.upload_success"},
            "error_key": None
        }
    
    except Exception as e:
        print(f"Upload error: {e}")
        return {"ok": False, "data": None, "error_key": ERR_UPLOAD_FAILED}

def delete_asset_core(deleter_id: int, asset_id: int) -> dict:
    """
    Soft-delete an asset.
    Returns: {ok, data: {message}, error_key}
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if asset exists
            cursor.execute("SELECT id, filename, deleted_at FROM assets WHERE id = ?", (asset_id,))
            asset = cursor.fetchone()
            
            if not asset:
                return {"ok": False, "data": None, "error_key": ERR_NOT_FOUND}
            
            if asset['deleted_at']:
                return {"ok": False, "data": None, "error_key": ERR_NOT_FOUND}
            
            # Soft delete
            cursor.execute("""
                UPDATE assets SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (asset_id,))
            conn.commit()
        
        # Audit log
        log_audit_event(
            actor_id=deleter_id,
            action_type="ASSET_DELETE",
            metadata=f"Deleted asset {asset_id} ({asset['filename']})"
        )
        
        return {
            "ok": True,
            "data": {"message": "files.delete_success"},
            "error_key": None
        }
    
    except Exception as e:
        print(f"Delete error: {e}")
        return {"ok": False, "data": None, "error_key": ERR_DELETE_FAILED}

def get_asset_path_core(viewer_id: int, asset_id: int) -> dict:
    """
    Get file path for asset (for controlled access).
    Returns: {ok, data: {storage_path, filename, mime_type}, error_key}
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT storage_path, filename, mime_type, deleted_at
                FROM assets WHERE id = ?
            """, (asset_id,))
            asset = cursor.fetchone()
            
            if not asset or asset['deleted_at']:
                return {"ok": False, "data": None, "error_key": ERR_NOT_FOUND}
            
            # Audit log download
            log_audit_event(
                actor_id=viewer_id,
                action_type="ASSET_DOWNLOAD",
                metadata=f"Downloaded asset {asset_id} ({asset['filename']})"
            )
            
            return {
                "ok": True,
                "data": {
                    "storage_path": asset['storage_path'],
                    "filename": asset['filename'],
                    "mime_type": asset['mime_type']
                },
                "error_key": None
            }
    
    except Exception as e:
        print(f"Get asset error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}
