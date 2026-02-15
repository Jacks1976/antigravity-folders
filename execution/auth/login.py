import sys
import os
import argparse
import json

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import ERR_INVALID_CREDENTIALS, ERR_ACCOUNT_PENDING, ERR_ACCOUNT_BANNED, ERR_TOO_MANY_ATTEMPTS, check_rate_limit, verify_password, create_access_token
from infra.audit_logger import log_audit_event

def login_user(email, password, ip_address='127.0.0.1'):
    # 1. Rate Limiting
    if not check_rate_limit(ip_address, email):
        log_audit_event(None, 'AUTH_LOGIN_FAIL', 'user', email, metadata={'reason': 'rate_limit'}, ip_address=ip_address)
        print(json.dumps({"error": ERR_TOO_MANY_ATTEMPTS}))
        return False

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 2. Fetch User
        cursor.execute("SELECT id, password_hash, status, role FROM users WHERE email = ? AND deleted_at IS NULL", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Generic error to avoid enumeration, but log the attempt
            log_audit_event(None, 'AUTH_LOGIN_FAIL', 'user', email, metadata={'reason': 'user_not_found'}, ip_address=ip_address)
            print(json.dumps({"error": ERR_INVALID_CREDENTIALS}))
            return False
            
        user_id, password_hash, status, role = user
        
        # 3. Verify Password
        if not verify_password(password_hash, password):
            log_audit_event(user_id, 'AUTH_LOGIN_FAIL', 'user', user_id, metadata={'reason': 'invalid_password'}, ip_address=ip_address)
            print(json.dumps({"error": ERR_INVALID_CREDENTIALS}))
            return False
            
        # 4. Status Check
        if status == 'Banned':
            log_audit_event(user_id, 'AUTH_LOGIN_FAIL', 'user', user_id, metadata={'reason': 'banned'}, ip_address=ip_address)
            print(json.dumps({"error": ERR_ACCOUNT_BANNED}))
            return False
            
        if status == 'Pending':
            log_audit_event(user_id, 'AUTH_LOGIN_FAIL', 'user', user_id, metadata={'reason': 'pending'}, ip_address=ip_address)
            print(json.dumps({"error": ERR_ACCOUNT_PENDING}))
            return False
            
        # 5. Success - Generate Token
        access_token = create_access_token(data={"sub": str(user_id), "role": role})
        
        log_audit_event(user_id, 'AUTH_LOGIN_SUCCESS', 'user', user_id, metadata={}, ip_address=ip_address)
        
        print(json.dumps({
            "success": True,
            "token": access_token,
            "user": {
                "id": user_id,
                "email": email,
                "role": role,
                "status": status
            }
        }))
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Login a user")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", required=True, help="User password")
    
    args = parser.parse_args()
    login_user(args.email, args.password)
