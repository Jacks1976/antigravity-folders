"""
Core logic for music scheduling (service plans, setlists, roster).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from audit import log_audit_event

# Error keys
ERR_PLAN_NOT_FOUND = "schedule.plan_not_found"
ERR_SONG_NOT_FOUND = "schedule.song_not_found"
ERR_ROSTER_NOT_FOUND = "schedule.roster_not_found"
ERR_INVALID_STATUS = "schedule.invalid_status"

def create_service_plan_core(creator_id: int, date: str, event_id: int = None, notes: str = None) -> dict:
    """Create a new service plan."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO service_plans (date, event_id, notes, created_by)
                VALUES (?, ?, ?, ?)
            """, (date, event_id, notes, creator_id))
            plan_id = cursor.lastrowid
            conn.commit()
        
        log_audit_event(creator_id, "ROSTER_CREATE", metadata=f"Created service plan for {date}")
        
        return {
            "ok": True,
            "data": {"plan_id": plan_id, "message": "schedule.plan_created"},
            "error_key": None
        }
    except Exception as e:
        print(f"Create plan error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def add_setlist_song_core(adder_id: int, plan_id: int, song_id: int, order_index: int) -> dict:
    """Add a song to service setlist."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check plan exists
            cursor.execute("SELECT id FROM service_plans WHERE id = ? AND deleted_at IS NULL", (plan_id,))
            if not cursor.fetchone():
                return {"ok": False, "data": None, "error_key": ERR_PLAN_NOT_FOUND}
            
            # Check song exists
            cursor.execute("SELECT id FROM songs WHERE id = ? AND deleted_at IS NULL", (song_id,))
            if not cursor.fetchone():
                return {"ok": False, "data": None, "error_key": ERR_SONG_NOT_FOUND}
            
            # Insert
            cursor.execute("""
                INSERT INTO service_setlist (plan_id, song_id, order_index)
                VALUES (?, ?, ?)
            """, (plan_id, song_id, order_index))
            conn.commit()
        
        log_audit_event(adder_id, "SETLIST_UPDATE", metadata=f"Added song {song_id} to plan {plan_id}")
        
        return {
            "ok": True,
            "data": {"message": "schedule.setlist_updated"},
            "error_key": None
        }
    except Exception as e:
        print(f"Add setlist song error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def assign_roster_entry_core(assigner_id: int, plan_id: int, musician_id: int, instrument: str) -> dict:
    """Assign a musician to the roster."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check plan exists
            cursor.execute("SELECT id FROM service_plans WHERE id = ? AND deleted_at IS NULL", (plan_id,))
            if not cursor.fetchone():
                return {"ok": False, "data": None, "error_key": ERR_PLAN_NOT_FOUND}
            
            # Insert roster entry
            cursor.execute("""
                INSERT INTO roster_entries (plan_id, musician_id, instrument, status)
                VALUES (?, ?, ?, 'pending')
            """, (plan_id, musician_id, instrument))
            roster_id = cursor.lastrowid
            conn.commit()
        
        log_audit_event(assigner_id, "ROSTER_ASSIGN", metadata=f"Assigned musician {musician_id} to plan {plan_id}")
        
        return {
            "ok": True,
            "data": {"roster_id": roster_id, "message": "schedule.roster_assigned"},
            "error_key": None
        }
    except Exception as e:
        print(f"Assign roster error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def update_roster_status_core(updater_id: int, roster_id: int, status: str, is_lead: bool = False) -> dict:
    """Update roster entry status."""
    if status not in ['pending', 'confirmed', 'declined']:
        return {"ok": False, "data": None, "error_key": ERR_INVALID_STATUS}
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get roster entry
            cursor.execute("SELECT musician_id FROM roster_entries WHERE id = ?", (roster_id,))
            entry = cursor.fetchone()
            
            if not entry:
                return {"ok": False, "data": None, "error_key": ERR_ROSTER_NOT_FOUND}
            
            # Check permission: own entry or lead override
            if entry['musician_id'] != updater_id and not is_lead:
                return {"ok": False, "data": None, "error_key": "auth.forbidden"}
            
            # Update
            cursor.execute("""
                UPDATE roster_entries SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, roster_id))
            conn.commit()
        
        event_type = "ROSTER_OVERRIDE" if is_lead else f"ROSTER_{status.upper()}"
        log_audit_event(updater_id, event_type, metadata=f"Updated roster {roster_id} to {status}")
        
        return {
            "ok": True,
            "data": {"message": "schedule.roster_updated"},
            "error_key": None
        }
    except Exception as e:
        print(f"Update roster status error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}

def list_plans_core(viewer_id: int, from_date: str = None, to_date: str = None) -> dict:
    """List service plans with optional date range."""
    try:
        with get_db_connection() as conn:
            conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
            cursor = conn.cursor()
            
            query = "SELECT * FROM service_plans WHERE deleted_at IS NULL"
            params = []
            
            if from_date:
                query += " AND date >= ?"
                params.append(from_date)
            if to_date:
                query += " AND date <= ?"
                params.append(to_date)
            
            query += " ORDER BY date ASC"
            
            cursor.execute(query, params)
            plans = cursor.fetchall()
            
            return {
                "ok": True,
                "data": {"results": plans},
                "error_key": None
            }
    except Exception as e:
        print(f"List plans error: {e}")
        return {"ok": False, "data": None, "error_key": "internal_error"}
