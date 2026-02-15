import sys
import os
import argparse
import json

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token
from infra.audit_logger import log_audit_event

def get_current_user(token):
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload

def assign_ministry(token, user_id, ministry_id, role, is_lead=False):
    actor = get_current_user(token)
    if not actor:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    actor_id = actor['sub']
    actor_role = actor['role']
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check permissions
        # Staff/Admin: Can assign anyone
        # Ministry Lead: Can assign to OWN ministry only
        allowed = False
        if actor_role in ('Admin', 'Staff'):
            allowed = True
        else:
            # Check if actor is lead of ministry_id
            cursor.execute("""
                SELECT 1 FROM ministry_assignments 
                WHERE user_id = ? AND ministry_id = ? AND is_lead = 1 AND deleted_at IS NULL
            """, (actor_id, ministry_id))
            if cursor.fetchone():
                allowed = True
        
        if not allowed:
            print(json.dumps({"error": "auth.forbidden"}))
            return
            
        # Perform Assignment
        try:
            # Insert or Update (Reacting deleted?)
            # Simplified: just Insert.
            cursor.execute("""
                INSERT INTO ministry_assignments (user_id, ministry_id, role, is_lead, assigned_by)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, ministry_id, role, 1 if is_lead else 0, actor_id))
            
            conn.commit()
            
            # Audit
            log_audit_event(
                actor_id=actor_id,
                action_type='MINISTRY_ASSIGN',
                resource_type='ministry_assignment',
                resource_id=cursor.lastrowid,
                metadata={'user_id': user_id, 'ministry_id': ministry_id, 'role': role, 'is_lead': is_lead}
            )
            
            print(json.dumps({"success": True}))
            
        except Exception as e:
            print(json.dumps({"error": f"Internal Error: {str(e)}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--ministry-id", required=True)
    parser.add_argument("--role", required=True) # e.g. "Singer", "Guitarist"
    parser.add_argument("--is-lead", action='store_true')
    
    args = parser.parse_args()
    assign_ministry(args.token, args.user_id, args.ministry_id, args.role, args.is_lead)
