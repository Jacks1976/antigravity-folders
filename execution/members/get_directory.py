import sys
import os
import argparse
import json
import math

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token

def get_current_user(token):
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload

def get_directory(token, page=1, limit=20, search=None):
    user = get_current_user(token)
    if not user:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    viewer_id = user['sub']
    viewer_role = user['role'] # Admin, Staff, MinistryLead, Member
    
    # Check Status (must be Active, unless Admin/Staff viewing)
    # Actually, we need to check the viewer's status from DB to be safe, but token should reflect it?
    # Ideally token has status. If not, query DB.
    # For MVP assume token is valid and we check status from DB if critical.
    # The requirement: "Only status='Active' can access directory". 
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verify Viewer Status
        cursor.execute("SELECT status FROM users WHERE id = ?", (viewer_id,))
        res = cursor.fetchone()
        if not res:
            print(json.dumps({"error": "auth.user_not_found"}))
            return
        
        viewer_status = res[0]
        if viewer_status != 'Active' and viewer_role not in ('Admin', 'Staff'):
            print(json.dumps({"error": "auth.forbidden_pending"}))
            return

        # Query Members
        offset = (page - 1) * limit
        
        query = """
            SELECT 
                u.id, u.email, u.role, u.status,
                p.full_name, p.phone, p.address, p.dob, p.baptism_date, p.bio, p.share_phone, p.profile_pic_url,
                p.ministry_history
            FROM users u
            LEFT JOIN member_profiles p ON u.id = p.user_id
            WHERE u.deleted_at IS NULL
        """
        params = []
        
        if search:
            query += " AND (p.full_name LIKE ? OR u.email LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
            
        query += " ORDER BY p.full_name ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Apply Field Level Permissions
        results = []
        for row in rows:
            uid = row['id']
            is_self = (uid == viewer_id)
            is_admin = (viewer_role in ('Admin', 'Staff'))
            
            # Base object
            member = {
                "id": uid,
                "full_name": row['full_name'],
                "profile_pic_url": row['profile_pic_url'],
                "bio": row['bio'],
                "status": row['status'],
                "roles": row['role']
            }
            
            # Email: Edit by Admin, View by All (Requirement said View by All)
            member['email'] = row['email']
            
            # Phone: Edit by Self/Admin. View if share_phone=True
            share_phone = bool(row['share_phone'])
            if is_admin or is_self or share_phone:
                member['phone'] = row['phone']
            else:
                member['phone'] = None # Hidden
                
            # Address: Hidden (PII) unless Admin or Self
            if is_admin or is_self:
                member['address'] = row['address']
            else:
                member['address'] = None # Hidden
                
            # DOB: Day/Month only to others (no year)
            dob = row['dob'] # YYYY-MM-DD
            if dob:
                 if is_admin or is_self:
                     member['dob'] = dob
                 else:
                     # Mask year: MM-DD
                     parts = dob.split('-')
                     if len(parts) == 3:
                         member['dob'] = f"{parts[1]}-{parts[2]}" # MM-DD
                     else:
                         member['dob'] = None
            else:
                member['dob'] = None
                
            # Ministry History?
            member['ministry_history'] = row['ministry_history']
            
            results.append(member)
            
        print(json.dumps({
            "page": page,
            "limit": limit,
            "results": results
        }))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--search")
    
    args = parser.parse_args()
    get_directory(args.token, args.page, args.limit, args.search)
