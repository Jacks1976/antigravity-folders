import sys
import os
import argparse
import json
import datetime

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token

def get_feed(token):
    payload = decode_access_token(token)
    if not payload:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    viewer_id = payload['sub']
    
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Check Status
        cursor.execute("SELECT role, status FROM users WHERE id = ?", (viewer_id,))
        user_row = cursor.fetchone()
        if not user_row or user_row['status'] != 'Active':
             print(json.dumps({"error": "auth.account_pending"})) # Only Active can see
             return
             
        user_role = user_row['role']
        
        # 2. Get Assigned Ministries
        cursor.execute("SELECT ministry_id FROM ministry_assignments WHERE user_id = ? AND deleted_at IS NULL", (viewer_id,))
        ministry_ids = [str(r[0]) for r in cursor.fetchall()]
        
        # 3. Query Active Announcements
        # Conditions:
        # - Expired < Now (Hide)
        # - Target = Global
        # - Target = Role AND target_id = user_role
        # - Target = Ministry AND target_id IN ministry_ids
        
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Build ministry placeholder string
        if ministry_ids:
             min_placeholders = ",".join(["?"] * len(ministry_ids))
             ministry_clause = f"(target_type = 'Ministry' AND target_id IN ({min_placeholders}))"
             params = ministry_ids
        else:
             ministry_clause = "0" # False
             params = []
             
        # Add static params for other clauses if query constructed properly
        # To avoid index juggling, let's construct query carefully.
        
        query = f"""
            SELECT * FROM announcements
            WHERE deleted_at IS NULL
            AND (expires_at IS NULL OR expires_at > ?)
            AND (
                (target_type = 'Global')
                OR (target_type = 'Role' AND target_id = ?)
                OR {ministry_clause}
            )
            ORDER BY is_pinned DESC, created_at DESC
        """
        
        # Query Params: [now_str, user_role, ...ministry_ids]
        final_params = [now_str, user_role] + params
        
        cursor.execute(query, final_params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row['id'],
                "title": row['title'],
                "body": row['body'],
                "target_type": row['target_type'],
                "is_pinned": bool(row['is_pinned']),
                "created_at": row['created_at']
            })
            
        print(json.dumps({"results": results, "count": len(results)}))

import sqlite3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    
    args = parser.parse_args()
    get_feed(args.token)
