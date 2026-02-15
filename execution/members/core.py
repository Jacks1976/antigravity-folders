"""
Core members business logic (importable, no argparse).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from infra.audit_logger import log_audit_event

def get_directory_core(viewer_id: int, page: int = 1, limit: int = 20, search: str = None, offset: int = None) -> dict:
    """
    Core directory listing logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get viewer info
        cursor.execute("SELECT role, status FROM users WHERE id = ?", (viewer_id,))
        viewer = cursor.fetchone()
        
        if not viewer or viewer['status'] != 'Active':
            return {"ok": False, "data": None, "error_key": "auth.account_pending"}
        
        viewer_role = viewer['role']
        
        # Calculate offset
        if offset is None:
            offset = (page - 1) * limit
        
        # Query members
        query = """
            SELECT u.id, u.email, u.role, u.status,
                   p.full_name, p.phone, p.address, p.dob, p.bio, p.share_phone, p.profile_pic_url
            FROM users u
            LEFT JOIN member_profiles p ON u.id = p.user_id
            WHERE u.deleted_at IS NULL
        """
        params = []
        
        if search:
            query += " AND (p.full_name LIKE ? OR u.email LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " ORDER BY p.full_name ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            is_self = (row['id'] == viewer_id)
            is_admin = (viewer_role in ('Admin', 'Staff'))
            
            member = {
                "id": row['id'],
                "full_name": row['full_name'],
                "email": row['email'],
                "bio": row['bio'],
                "profile_pic_url": row['profile_pic_url']
            }
            
            # Phone visibility
            if is_admin or is_self or row['share_phone']:
                member['phone'] = row['phone']
            
            # Address (PII - Admin/Self only)
            if is_admin or is_self:
                member['address'] = row['address']
            
            # DOB masking
            if row['dob']:
                if is_admin or is_self:
                    member['dob'] = row['dob']
                else:
                    parts = row['dob'].split('-')
                    if len(parts) == 3:
                        member['dob'] = f"{parts[1]}-{parts[2]}"
            
            results.append(member)
        
        return {"ok": True, "data": {"results": results, "page": page, "limit": limit, "offset": offset}, "error_key": None}

def update_profile_core(user_id: int, updates: dict) -> dict:
    """
    Core profile update logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    allowed_fields = ['phone', 'address', 'dob', 'bio', 'share_phone', 'profile_pic_url']
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not filtered_updates:
        return {"ok": True, "data": {"message": "profile.no_changes"}, "error_key": None}
    
    # Convert share_phone to int
    if 'share_phone' in filtered_updates:
        filtered_updates['share_phone'] = 1 if filtered_updates['share_phone'] else 0
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in filtered_updates.keys()])
            values = list(filtered_updates.values())
            values.append(user_id)
            
            cursor.execute(f"UPDATE member_profiles SET {set_clause} WHERE user_id = ?", values)
            
            if cursor.rowcount == 0:
                return {"ok": False, "data": None, "error_key": "profile.not_found"}
            
            conn.commit()
            
            log_audit_event(user_id, 'MEMBER_PROFILE_UPDATE', 'user', user_id, {'fields': list(filtered_updates.keys())})
            
            return {"ok": True, "data": {"message": "profile.updated"}, "error_key": None}
    
    except Exception as e:
        return {"ok": False, "data": None, "error_key": "internal_error"}

def assign_ministry_core(admin_id: int, user_id: int, ministry_id: int, role: str, is_lead: bool = False) -> dict:
    """
    Core ministry assignment logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ministry_assignments (user_id, ministry_id, role, is_lead, assigned_by)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, ministry_id, role, 1 if is_lead else 0, admin_id))
            
            conn.commit()
            
            log_audit_event(admin_id, 'MINISTRY_ASSIGN', 'ministry_assignment', cursor.lastrowid,
                          {'user_id': user_id, 'ministry_id': ministry_id})
            
            return {"ok": True, "data": {"message": "ministry.assigned"}, "error_key": None}
    
    except Exception as e:
        return {"ok": False, "data": None, "error_key": "internal_error"}
