import sys
import os
import argparse
import json
import datetime

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token
from infra.audit_logger import log_audit_event

def post_message(token, title, body, target_type='Global', target_id=None, expires_at=None, is_pinned=False):
    payload = decode_access_token(token)
    if not payload:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    actor_id = payload['sub']
    actor_role = payload['role']
    
    # Validation
    if target_type not in ('Global', 'Role', 'Ministry'):
         print(json.dumps({"error": "announcement.invalid_target_type"}))
         return

    # Parse target_id
    # If Global, target_id should be None
    if target_type == 'Global':
        target_id = None
        # Permission: Admin Only
        if actor_role not in ('Admin', 'Staff'):
             print(json.dumps({"error": "auth.forbidden"}))
             return
             
    elif target_type == 'Role':
        if not target_id:
            print(json.dumps({"error": "announcement.missing_target_id"}))
            return
        # Permission: Admin Only
        if actor_role not in ('Admin', 'Staff'):
             print(json.dumps({"error": "auth.forbidden"}))
             return

    elif target_type == 'Ministry':
        if not target_id:
            print(json.dumps({"error": "announcement.missing_target_id"}))
            return
        # Permission: Admin OR Ministry Lead of this ministry
        # Start with Admin check
        allowed = (actor_role in ('Admin', 'Staff'))
        if not allowed:
            # Check Lead
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM ministry_assignments 
                    WHERE user_id = ? AND ministry_id = ? AND is_lead = 1 AND deleted_at IS NULL
                """, (actor_id, target_id))
                if cursor.fetchone():
                    allowed = True
        
        if not allowed:
             print(json.dumps({"error": "auth.forbidden"}))
             return

    # Check Expires
    if expires_at:
        try:
             exp_dt = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        except:
             print(json.dumps({"error": "announcement.invalid_date"}))
             return
    
    # Insert
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO announcements (
                    title, body, target_type, target_id, is_pinned, expires_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, body, target_type, target_id, 1 if is_pinned else 0, expires_at, actor_id))
            
            announcement_id = cursor.lastrowid
            conn.commit()
            
            log_audit_event(
                actor_id=actor_id,
                action_type='ANNOUNCEMENT_CREATE',
                resource_type='announcement',
                resource_id=announcement_id,
                metadata={'title': title, 'target': target_type}
            )
            
            print(json.dumps({
                "success": True, 
                "announcement_id": announcement_id,
                "message": "announcement.created_success"
            }))

    except Exception as e:
        print(json.dumps({"error": f"Internal Error: {str(e)}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body")
    parser.add_argument("--target-type", default='Global', choices=['Global', 'Role', 'Ministry'])
    parser.add_argument("--target-id")
    parser.add_argument("--expires-at", help="ISO format")
    parser.add_argument("--pinned", action='store_true')
    
    args = parser.parse_args()
    post_message(args.token, args.title, args.body, args.target_type, args.target_id, args.expires_at, args.pinned)
