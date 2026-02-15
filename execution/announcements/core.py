"""
Core announcements business logic (importable, no argparse).
"""
import sys
import os
import json
import datetime
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from infra.audit_logger import log_audit_event

def post_announcement_core(actor_id: int, actor_role: str, title: str, body: str = None, 
                          target_type: str = 'Global', target_id: str = None, 
                          expires_at: str = None, is_pinned: bool = False, organization_id: int = 1) -> dict:
    """
    Core announcement posting logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    if target_type not in ('Global', 'Role', 'Ministry'):
        return {"ok": False, "data": None, "error_key": "announcement.invalid_target_type"}
    
    # Permission checks
    if target_type == 'Global':
        if actor_role not in ('Admin', 'Staff'):
            return {"ok": False, "data": None, "error_key": "auth.forbidden"}
        target_id = None
    
    elif target_type == 'Role':
        if actor_role not in ('Admin', 'Staff'):
            return {"ok": False, "data": None, "error_key": "auth.forbidden"}
        if not target_id:
            return {"ok": False, "data": None, "error_key": "announcement.missing_target_id"}
    
    elif target_type == 'Ministry':
        if not target_id:
            return {"ok": False, "data": None, "error_key": "announcement.missing_target_id"}
        
        # Check if Admin or Ministry Lead
        allowed = (actor_role in ('Admin', 'Staff'))
        if not allowed:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM ministry_assignments 
                    WHERE user_id = ? AND ministry_id = ? AND is_lead = 1 AND deleted_at IS NULL
                """, (actor_id, target_id))
                if cursor.fetchone():
                    allowed = True
        
        if not allowed:
            return {"ok": False, "data": None, "error_key": "auth.forbidden"}
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO announcements (title, body, target_type, target_id, is_pinned, expires_at, created_by, organization_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, body, target_type, target_id, 1 if is_pinned else 0, expires_at, actor_id, organization_id))
            
            announcement_id = cursor.lastrowid
            conn.commit()
            
            log_audit_event(actor_id, 'ANNOUNCEMENT_CREATE', 'announcement', announcement_id, {'title': title})
            
            return {"ok": True, "data": {"announcement_id": announcement_id, "message": "announcement.created_success"}, "error_key": None}
    
    except Exception as e:
        return {"ok": False, "data": None, "error_key": "internal_error"}

def get_feed_core(user_id: int, user_role: str, limit: int = 50, offset: int = 0, organization_id: int = None) -> dict:
    """
    Core announcement feed logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user's ministries
        cursor.execute("SELECT ministry_id FROM ministry_assignments WHERE user_id = ? AND deleted_at IS NULL", (user_id,))
        ministry_ids = [str(r[0]) for r in cursor.fetchall()]
        
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Build query
        if ministry_ids:
            min_placeholders = ",".join(["?"] * len(ministry_ids))
            ministry_clause = f"(target_type = 'Ministry' AND target_id IN ({min_placeholders}))"
            params = ministry_ids
        else:
            ministry_clause = "0"
            params = []
        
        query = f"""
            SELECT * FROM announcements
            WHERE deleted_at IS NULL
            AND (expires_at IS NULL OR expires_at > ?)
        """
        params = [now_str]

        if organization_id is not None:
            query += " AND organization_id = ?"
            params.append(organization_id)

        query += f" AND ( (target_type = 'Global') OR (target_type = 'Role' AND target_id = ?) OR {ministry_clause} )"
        
        final_params = params + [user_role] + params[1:] if params and len(params) > 1 else [now_str, user_role]
        # The above manipulation keeps compatibility when ministry params exist
        final_params = [now_str, user_role] + ( [p for p in params[1:]] if len(params) > 1 else [] )
        final_params += [limit, offset]

        cursor.execute(query, final_params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row['id'],
                "title": row['title'],
                "body": row['body'],
                "target_type": row['target_type'],
                "is_pinned": bool(row['is_pinned']),
                "created_at": row['created_at']
            })
        
        return {"ok": True, "data": {"results": results, "limit": limit, "offset": offset}, "error_key": None}
