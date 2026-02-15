"""
Core logic for music repertoire management.
Handles songs, song assets (links/files), and instrument tags.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from audit import log_audit_event

# Error keys
ERR_SONG_NOT_FOUND = "song.not_found"
ERR_INVALID_ASSET_TYPE = "song.invalid_asset_type"
ERR_ASSET_NOT_FOUND = "song.asset_not_found"

def create_song_core(creator_id: int, title: str, artist: str = None, bpm: int = None, default_key: str = None) -> dict:
    """Create a new song in the repertoire."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO songs (title, artist, bpm, default_key, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (title, artist, bpm, default_key, creator_id))
            song_id = cursor.lastrowid
            conn.commit()
        
        log_audit_event(creator_id, "SONG_CREATE", metadata=f"Created song: {title}")
        
        return {
            "ok": True,
            "data": {"song_id": song_id, "message": "song.created_success"},
            "error_key": None
        }
    except Exception as e:
        print(f"Create song error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def update_song_core(updater_id: int, song_id: int, updates: dict) -> dict:
    """Update song details."""
    allowed_fields = ['title', 'artist', 'bpm', 'default_key']
    filtered = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not filtered:
        return {"ok": True, "data": {"message": "song.no_changes"}, "error_key": None}
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check song exists
            cursor.execute("SELECT id FROM songs WHERE id = ? AND deleted_at IS NULL", (song_id,))
            if not cursor.fetchone():
                return {"ok": False, "data": None, "error_key": ERR_SONG_NOT_FOUND}
            
            # Update
            set_clause = ", ".join([f"{k} = ?" for k in filtered.keys()])
            values = list(filtered.values()) + [song_id]
            cursor.execute(f"""
                UPDATE songs SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
        
        log_audit_event(updater_id, "SONG_UPDATE", metadata=f"Updated song {song_id}")
        
        return {
            "ok": True,
            "data": {"message": "song.updated_success"},
            "error_key": None
        }
    except Exception as e:
        print(f"Update song error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def list_songs_core(viewer_id: int, search: str = None, limit: int = 50, offset: int = 0) -> dict:
    """List songs with optional search."""
    try:
        with get_db_connection() as conn:
            conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
            cursor = conn.cursor()
            
            query = "SELECT * FROM songs WHERE deleted_at IS NULL"
            params = []
            
            if search:
                query += " AND (title LIKE ? OR artist LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])
            
            query += " ORDER BY title ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            songs = cursor.fetchall()
            
            return {
                "ok": True,
                "data": {"results": songs, "limit": limit, "offset": offset},
                "error_key": None
            }
    except Exception as e:
        print(f"List songs error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def add_song_asset_core(adder_id: int, song_id: int, asset_type: str, url: str = None, 
                       asset_id: int = None, label: str = None, instrument_tag_ids: list = None) -> dict:
    """Add an asset (link or file) to a song."""
    if asset_type not in ['LINK', 'FILE']:
        return {"ok": False, "data": None, "error_key": ERR_INVALID_ASSET_TYPE}
    
    if asset_type == 'LINK' and not url:
        return {"ok": False, "data": None, "error_key": "song.missing_url"}
    
    if asset_type == 'FILE' and not asset_id:
        return {"ok": False, "data": None, "error_key": "song.missing_asset_id"}
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check song exists
            cursor.execute("SELECT id FROM songs WHERE id = ? AND deleted_at IS NULL", (song_id,))
            if not cursor.fetchone():
                return {"ok": False, "data": None, "error_key": ERR_SONG_NOT_FOUND}
            
            # Insert asset
            tags_json = json.dumps(instrument_tag_ids if instrument_tag_ids else [])
            cursor.execute("""
                INSERT INTO song_assets (song_id, type, url, asset_id, label, instrument_tag_ids)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (song_id, asset_type, url, asset_id, label, tags_json))
            song_asset_id = cursor.lastrowid
            conn.commit()
        
        log_audit_event(adder_id, "SONG_ASSET_ADD", metadata=f"Added {asset_type} asset to song {song_id}")
        
        return {
            "ok": True,
            "data": {"song_asset_id": song_asset_id, "message": "song.asset_added"},
            "error_key": None
        }
    except Exception as e:
        print(f"Add song asset error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def remove_song_asset_core(remover_id: int, song_asset_id: int) -> dict:
    """Soft-delete a song asset."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM song_assets WHERE id = ? AND deleted_at IS NULL", (song_asset_id,))
            if not cursor.fetchone():
                return {"ok": False, "data": None, "error_key": ERR_ASSET_NOT_FOUND}
            
            cursor.execute("UPDATE song_assets SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (song_asset_id,))
            conn.commit()
        
        log_audit_event(remover_id, "SONG_ASSET_REMOVE", metadata=f"Removed song asset {song_asset_id}")
        
        return {
            "ok": True,
            "data": {"message": "song.asset_removed"},
            "error_key": None
        }
    except Exception as e:
        print(f"Remove song asset error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}
