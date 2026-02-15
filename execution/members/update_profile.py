import sys
import os
import argparse
import json
import jwt

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token, ERR_INVALID_EMAIL
from infra.audit_logger import log_audit_event

def get_current_user(token):
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload

def update_profile(token, target_user_id=None, **kwargs):
    user = get_current_user(token)
    if not user:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    actor_id = user['sub']
    actor_role = user['role']
    
    # If target not specified, update self
    if not target_user_id:
        target_user_id = actor_id
    else:
        target_user_id = int(target_user_id)

    # Permission Check
    # Admin can update anyone. Member can update self (but not everything).
    if target_user_id != actor_id:
        if actor_role not in ('Admin', 'Staff'):
            print(json.dumps({"error": "auth.forbidden"}))
            return

    # Allowed fields for update
    # Self: phone, address, dob, bio, share_phone, profile_pic_url
    # Admin: All above + full_name (?)
    
    allowed_fields = ['phone', 'address', 'dob', 'bio', 'share_phone', 'profile_pic_url']
    if actor_role in ('Admin', 'Staff'):
        allowed_fields.append('full_name')
        allowed_fields.append('baptism_date')

    updates = {}
    for k, v in kwargs.items():
        if k in allowed_fields and v is not None:
             # Convert share_phone to int/bool
             if k == 'share_phone':
                 v = 1 if str(v).lower() == 'true' else 0
             updates[k] = v

    if not updates:
        print(json.dumps({"message": "No changes"}))
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(target_user_id)
            
            sql = f"UPDATE member_profiles SET {set_clause} WHERE user_id = ?"
            cursor.execute(sql, values)
            
            if cursor.rowcount == 0:
                 # Create profile if not exists? Or error?
                 print(json.dumps({"error": "profile.not_found"}))
                 return

            conn.commit()
            
            # Audit
            log_audit_event(
                actor_id=actor_id,
                action_type='MEMBER_PROFILE_UPDATE',
                resource_type='user',
                resource_id=target_user_id,
                metadata={'fields': list(updates.keys())}
            )

            print(json.dumps({"success": True}))

    except Exception as e:
        print(json.dumps({"error": f"Internal Error: {str(e)}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--target-id", help="Target User ID (Admin only)")
    parser.add_argument("--phone")
    parser.add_argument("--address")
    parser.add_argument("--dob")
    parser.add_argument("--bio")
    parser.add_argument("--share-phone") # String 'true'/'false'
    parser.add_argument("--pic-url")
    parser.add_argument("--full-name") # Admin only
    parser.add_argument("--baptism-date") # Admin only
    
    args = parser.parse_args()
    
    update_profile(
        args.token, 
        args.target_id,
        phone=args.phone,
        address=args.address,
        dob=args.dob,
        bio=args.bio,
        share_phone=args.share_phone,
        profile_pic_url=args.pic_url,
        full_name=args.full_name,
        baptism_date=args.baptism_date
    )
