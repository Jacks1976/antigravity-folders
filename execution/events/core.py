"""
Core events business logic (importable, no argparse).
"""
import sys
import os
import json
import datetime
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from infra.audit_logger import log_audit_event

def create_event_core(admin_id: int, title: str, start_at: str, end_at: str, description: str = None, 
                     location: str = None, is_public: bool = False, target_ministry_ids: list = None, organization_id: int = 1) -> dict:
    """
    Core event creation logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    # Validate dates
    try:
        start_dt = datetime.datetime.fromisoformat(start_at.replace('Z', '+00:00'))
        end_dt = datetime.datetime.fromisoformat(end_at.replace('Z', '+00:00'))
        
        if end_dt <= start_dt:
            return {"ok": False, "data": None, "error_key": "event.invalid_dates"}
    except:
        return {"ok": False, "data": None, "error_key": "event.invalid_date_format"}
    
    # Convert target_ministry_ids to JSON
    targets_json = json.dumps(target_ministry_ids if target_ministry_ids else [])
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO events (title, description, start_at, end_at, location, is_public, target_ministry_ids, created_by, organization_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, start_at, end_at, location, 1 if is_public else 0, targets_json, admin_id, organization_id))
            
            event_id = cursor.lastrowid
            conn.commit()
            
            log_audit_event(admin_id, 'EVENT_CREATE', 'event', event_id, {'title': title})
            
            return {"ok": True, "data": {"event_id": event_id, "message": "event.created_success"}, "error_key": None}
    
    except Exception as e:
        return {"ok": False, "data": None, "error_key": "internal_error"}

def list_events_core(viewer_id: int = None, from_date: str = None, to_date: str = None, organization_id: int = None) -> dict:
    """
    Core event listing logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    viewer_status = 'Public'
    viewer_ministries = set()
    
    if viewer_id:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM users WHERE id = ?", (viewer_id,))
            row = cursor.fetchone()
            if row:
                viewer_status = row['status']
                
                if viewer_status == 'Active':
                    cursor.execute("SELECT ministry_id FROM ministry_assignments WHERE user_id = ? AND deleted_at IS NULL", (viewer_id,))
                    viewer_ministries = {str(r[0]) for r in cursor.fetchall()}
    
    query = "SELECT * FROM events WHERE deleted_at IS NULL"
    params = []
    
    if organization_id is not None:
        query += " AND organization_id = ?"
        params.append(organization_id)

    if viewer_status != 'Active':
        query += " AND is_public = 1"
    
    if from_date:
        query += " AND start_at >= ?"
        params.append(from_date)
    
    if to_date:
        query += " AND start_at <= ?"
        params.append(to_date)
    
    query += " ORDER BY start_at ASC"
    
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            event = dict(row)
            is_public = bool(event['is_public'])
            
            # Internal event visibility check
            if not is_public and viewer_status == 'Active':
                try:
                    targets = json.loads(event['target_ministry_ids'])
                except:
                    targets = []
                
                if targets and not set(targets).intersection(viewer_ministries):
                    continue
            
            results.append({
                "id": event['id'],
                "title": event['title'],
                "description": event['description'],
                "start": event['start_at'],
                "end": event['end_at'],
                "location": event['location'],
                "public": is_public
            })
        
        return {"ok": True, "data": {"results": results}, "error_key": None}

def rsvp_event_core(user_id: int, event_id: int, status: str) -> dict:
    """
    Core RSVP logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    if status not in ('going', 'maybe', 'not_going'):
        return {"ok": False, "data": None, "error_key": "event.invalid_rsvp_status"}
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify event exists
            cursor.execute("SELECT id, organization_id FROM events WHERE id = ?", (event_id,))
            ev = cursor.fetchone()
            if not ev:
                return {"ok": False, "data": None, "error_key": "event.not_found"}

            # Verify user's organization matches event's organization
            cursor.execute("SELECT organization_id FROM users WHERE id = ?", (user_id,))
            u = cursor.fetchone()
            if not u or u['organization_id'] != ev['organization_id']:
                return {"ok": False, "data": None, "error_key": "auth.forbidden"}
            
            # Upsert RSVP
            cursor.execute("""
                INSERT INTO event_rsvps (event_id, user_id, status)
                VALUES (?, ?, ?)
                ON CONFLICT(event_id, user_id) DO UPDATE SET
                    status = excluded.status,
                    updated_at = CURRENT_TIMESTAMP
            """, (event_id, user_id, status))
            
            conn.commit()
            
            log_audit_event(user_id, 'RSVP_CHANGE', 'event', event_id, {'status': status})
            
            return {"ok": True, "data": {"message": "event.rsvp_saved"}, "error_key": None}
    
    except Exception as e:
        return {"ok": False, "data": None, "error_key": "internal_error"}
