"""
Core authentication business logic (importable, no argparse).
"""
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import hash_password, verify_password, validate_password_strength, create_access_token
from auth.utils import ERR_PASSWORD_WEAK, ERR_INVALID_CREDENTIALS, ERR_ACCOUNT_PENDING, ERR_ACCOUNT_BANNED
from infra.audit_logger import log_audit_event

def register_user_core(email: str, password: str, full_name: str, organization_slug: str = None) -> dict:
    """
    Core registration logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    if not validate_password_strength(password):
        return {"ok": False, "data": None, "error_key": ERR_PASSWORD_WEAK}
    
    pwd_hash = hash_password(password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Resolve organization id from slug if provided (fallback to default org 1)
            org_id = 1
            if organization_slug:
                cursor.execute("SELECT id FROM organizations WHERE slug = ?", (organization_slug,))
                r = cursor.fetchone()
                if r:
                    org_id = r['id']
            
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, status, organization_id)
                VALUES (?, ?, 'Pending', 'Pending', ?)
            """, (email, pwd_hash, org_id))
            user_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO member_profiles (user_id, full_name, organization_id)
                VALUES (?, ?, ?)
            """, (user_id, full_name, org_id))
            
            conn.commit()
            
            log_audit_event(
                actor_id=user_id,
                action_type='AUTH_REGISTER',
                resource_type='user',
                resource_id=user_id,
                metadata={'email': email}
            )
            
            return {
                "ok": True,
                "data": {"user_id": user_id, "message": "auth.register_success"},
                "error_key": None
            }
            
    except Exception as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            return {"ok": False, "data": None, "error_key": "auth.email_already_registered"}
        return {"ok": False, "data": None, "error_key": "internal_error"}

def login_user_core(email: str, password: str) -> dict:
    """
    Core login logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
def login_user_core(email: str, password: str, organization_slug: str = None) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        org_id = None
        if organization_slug:
            cursor.execute("SELECT id FROM organizations WHERE slug = ?", (organization_slug,))
            r = cursor.fetchone()
            if r:
                org_id = r['id']

        if org_id is not None:
            cursor.execute("SELECT id, password_hash, role, status FROM users WHERE email = ? AND organization_id = ?", (email, org_id))
        else:
            cursor.execute("SELECT id, password_hash, role, status FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user or not verify_password(user['password_hash'], password):
            log_audit_event(None, 'AUTH_LOGIN_FAIL', metadata={'email': email})
            return {"ok": False, "data": None, "error_key": ERR_INVALID_CREDENTIALS}
        
        if user['status'] == 'Pending':
            return {"ok": False, "data": None, "error_key": ERR_ACCOUNT_PENDING}
        
        if user['status'] == 'Banned':
            return {"ok": False, "data": None, "error_key": ERR_ACCOUNT_BANNED}
        
        # Create token (include organization id for tenant scoping)
        org_id = user.get('organization_id') if 'organization_id' in user else None
        token_data = {"sub": user['id'], "role": user['role'], "org": org_id}
        token = create_access_token(token_data, datetime.timedelta(minutes=60*24))
        
        log_audit_event(user['id'], 'AUTH_LOGIN_SUCCESS', resource_type='user', resource_id=user['id'])
        
        return {
            "ok": True,
            "data": {"token": token, "user_id": user['id'], "role": user['role']},
            "error_key": None
        }

def approve_user_core(admin_id: int, email: str) -> dict:
    """
    Core user approval logic.
    Returns: {"ok": bool, "data": dict|None, "error_key": str|None}
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, status FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            return {"ok": False, "data": None, "error_key": "user.not_found"}
        
        if user['status'] != 'Pending':
            return {"ok": False, "data": None, "error_key": "user.already_approved"}
        
        cursor.execute("UPDATE users SET status = 'Active', role = 'Member' WHERE id = ?", (user['id'],))
        conn.commit()
        
        log_audit_event(admin_id, 'AUTH_APPROVE', resource_type='user', resource_id=user['id'])
        
        return {"ok": True, "data": {"message": "auth.user_approved"}, "error_key": None}
