import sys
import os
import argparse
import json

# Add execution directory to path to import db and auth.utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import hash_password, validate_password_strength, ERR_INVALID_EMAIL, ERR_PASSWORD_WEAK
from infra.audit_logger import log_audit_event

def register_user(email, password, full_name):
    # 1. Validation
    if not validate_password_strength(password):
        print(json.dumps({"error": ERR_PASSWORD_WEAK}))
        return False
    
    # 2. Hash Password
    pwd_hash = hash_password(password)
    
    # 3. Insert User
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert User
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, status)
                VALUES (?, ?, 'Pending', 'Pending')
            """, (email, pwd_hash))
            user_id = cursor.lastrowid
            
            # Create Profile (Basic)
            cursor.execute("""
                INSERT INTO member_profiles (user_id, full_name)
                VALUES (?, ?)
            """, (user_id, full_name))
            
            conn.commit()
            
            # 4. Audit Log
            log_audit_event(
                actor_id=user_id, # Self-registration
                action_type='AUTH_REGISTER',
                resource_type='user',
                resource_id=user_id,
                metadata={'email': email}
            )
            
            print(json.dumps({
                "success": True, 
                "message": "User registered successfully. Status is Pending.",
                "user_id": user_id
            }))
            return True
            
    except Exception as e:
        if "UNIQUE constraint failed: users.email" in str(e):
             print(json.dumps({"error": "auth.email_already_registered"}))
        else:
            print(json.dumps({"error": f"Internal Error: {str(e)}"}))
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register a new user")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", required=True, help="User password")
    parser.add_argument("--name", required=True, help="User full name")
    
    args = parser.parse_args()
    register_user(args.email, args.password, args.name)
