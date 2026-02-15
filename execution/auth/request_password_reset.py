import sys
import os
import argparse
import json
import uuid
import datetime

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import ERR_RESET_SENT, RESET_TOKEN_EXPIRE_MINUTES
from infra.audit_logger import log_audit_event

def request_password_reset(email):
    # Always return success message to prevent enumeration
    success_response = json.dumps({"message": ERR_RESET_SENT})
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Check User
        cursor.execute("SELECT id, status FROM users WHERE email = ? AND deleted_at IS NULL", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Log attempt for non-existent user? Maybe, but could be noisy. 
            # Optional: Log if needed for security monitoring.
            print(success_response)
            return True
            
        user_id, status = user
        
        if status == 'Banned':
            # Do NOT allow banned users to reset
            print(success_response) 
            return True

        # 2. Invalidate previous tokens
        cursor.execute("UPDATE password_resets SET is_used = 1 WHERE user_id = ? AND is_used = 0", (user_id,))
        
        # 3. Generate New Token
        token = str(uuid.uuid4())
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        
        cursor.execute("""
            INSERT INTO password_resets (token, user_id, expires_at)
            VALUES (?, ?, ?)
        """, (token, user_id, expires_at))
        
        conn.commit()
        
        # 4. Audit Log
        log_audit_event(user_id, 'AUTH_PASSWORD_RESET_REQUEST', 'user', user_id)
        
        # IN REAL APP: Send Email. 
        # FOR MVP/DEV: Print the link to STDOUT (or just the token)
        # We print a special debug message so the caller (test script) can grab it, 
        # but the JSON output remains standard.
        # Actually, let's include the debug link in a separate line or logging.
        # For simplicity in this text-based interaction, I'll print it to stderr or include in a debug field if this is dev mode.
        # User requirement: "Generic response".
        # But I need to see the token to test it. I will print "[DEBUG] Token: ..." to stderr.
        
        sys.stderr.write(f"[DEBUG] Password Reset Link: /reset-password?token={token}\n")
        print(success_response)
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Request password reset")
    parser.add_argument("--email", required=True, help="User email")
    
    args = parser.parse_args()
    request_password_reset(args.email)
