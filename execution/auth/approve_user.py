import sys
import os
import argparse
import json

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from infra.audit_logger import log_audit_event

def approve_user(target_email, admin_id=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Get User
        cursor.execute("SELECT id, status FROM users WHERE email = ? AND deleted_at IS NULL", (target_email,))
        user = cursor.fetchone()
        
        if not user:
            print(json.dumps({"error": "User not found"}))
            return False
            
        user_id, current_status = user
        
        if current_status == 'Active':
            print(json.dumps({"message": "User is already active."}))
            return True
            
        # 2. Update Status
        cursor.execute("UPDATE users SET status = 'Active', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        
        # 3. Audit Log
        log_audit_event(
            actor_id=admin_id, # The admin performing the action
            action_type='AUTH_STATUS_CHANGE',
            resource_type='user',
            resource_id=user_id,
            metadata={'previous_status': current_status, 'new_status': 'Active'}
        )
        
        print(json.dumps({"success": True, "message": f"User {target_email} approved successfully."}))
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Approve a pending user")
    parser.add_argument("--email", required=True, help="Email of the user to approve")
    parser.add_argument("--admin-id", type=int, help="ID of the admin performing the action (for audit logs)")
    
    args = parser.parse_args()
    approve_user(args.email, args.admin_id)
