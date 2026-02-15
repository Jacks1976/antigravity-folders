import sys
import os
import argparse
import json
import datetime
from dateutil import parser as date_parser

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import hash_password, validate_password_strength, ERR_RESET_INVALID, ERR_PASSWORD_WEAK
from infra.audit_logger import log_audit_event

def confirm_password_reset(token, new_password):
    # 1. Validate Password Strength
    if not validate_password_strength(new_password):
        print(json.dumps({"error": ERR_PASSWORD_WEAK}))
        return False

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 2. Validate Token
        cursor.execute("""
            SELECT user_id, expires_at, is_used 
            FROM password_resets 
            WHERE token = ?
        """, (token,))
        row = cursor.fetchone()
        
        if not row:
            print(json.dumps({"error": ERR_RESET_INVALID}))
            return False
            
        user_id, expires_at_str, is_used = row
        
        if is_used:
            print(json.dumps({"error": ERR_RESET_INVALID}))
            return False
            
        # Parse timestamp. SQLite stores/returns string.
        # Ensure UTC comparison
        # expires_at_str example: "2023-10-27 10:00:00..."
        try:
             # handle simple string format or iso format
             expires_at = date_parser.parse(str(expires_at_str))
             # If naive, assume UTC because we saved as UTC
             if expires_at.tzinfo is None:
                 expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
        except:
             print(json.dumps({"error": "Internal Error: Date parsing"}))
             return False

        if datetime.datetime.now(datetime.timezone.utc) > expires_at:
            print(json.dumps({"error": ERR_RESET_INVALID}))
            return False
            
        # 3. Update Password
        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_hash, user_id))
        
        # 4. Mark Token Used
        cursor.execute("UPDATE password_resets SET is_used = 1 WHERE token = ?", (token,))
        
        conn.commit()
        
        # 5. Audit Log
        log_audit_event(user_id, 'AUTH_PASSWORD_RESET_CONFIRM', 'user', user_id)
        
        print(json.dumps({"success": True, "message": "Password updated successfully."}))
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confirm password reset")
    parser.add_argument("--token", required=True, help="Reset token")
    parser.add_argument("--password", required=True, help="New password")
    
    args = parser.parse_args()
    confirm_password_reset(args.token, args.password)
