import sys
import os
import argparse
import json
import secrets
import string

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import hash_password, validate_password_strength, ERR_INVALID_EMAIL, ERR_PASSWORD_WEAK
from infra.audit_logger import log_audit_event

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def create_profile(admin_id, email, full_name, password=None, phone=None, address=None, dob=None, role='Pending', status='Pending'):
    # 1. Password
    if not password:
        password = generate_password()
        
    if not validate_password_strength(password):
        print(json.dumps({"error": ERR_PASSWORD_WEAK}))
        return False

    pwd_hash = hash_password(password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check Admin Permissions (if admin_id provided)
            # For now assuming script usage implies admin or system privilege if not using token
            # But let's check if admin_id is valid admin
            if admin_id:
                cursor.execute("SELECT role FROM users WHERE id = ?", (admin_id,))
                res = cursor.fetchone()
                if not res or res[0] not in ('Admin', 'Staff'):
                     print(json.dumps({"error": "auth.forbidden"}))
                     return False

            # Insert User
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, status)
                VALUES (?, ?, ?, ?)
            """, (email, pwd_hash, role, status))
            user_id = cursor.lastrowid
            
            # Insert Profile
            cursor.execute("""
                INSERT INTO member_profiles (user_id, full_name, phone, address, dob)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, full_name, phone, address, dob))
            
            conn.commit()
            
            # Audit Log
            log_audit_event(
                actor_id=admin_id if admin_id else user_id,
                action_type='MEMBER_PROFILE_CREATE',
                resource_type='user',
                resource_id=user_id,
                metadata={'email': email, 'created_by': admin_id}
            )
            
            print(json.dumps({
                "success": True, 
                "user_id": user_id,
                "email": email,
                "temp_password": password 
            }))
            return True

    except Exception as e:
        if "UNIQUE constraint failed: users.email" in str(e):
             print(json.dumps({"error": "auth.email_already_registered"}))
        else:
            print(json.dumps({"error": f"Internal Error: {str(e)}"}))
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Member Profile (Admin)")
    parser.add_argument("--admin-id", help="ID of admin creating the user (optional)")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", help="If not provided, one is generated")
    parser.add_argument("--phone")
    parser.add_argument("--address")
    parser.add_argument("--dob", help="YYYY-MM-DD")
    parser.add_argument("--role", default="Pending")
    parser.add_argument("--status", default="Pending")
    
    args = parser.parse_args()
    create_profile(args.admin_id, args.email, args.name, args.password, args.phone, args.address, args.dob, args.role, args.status)
