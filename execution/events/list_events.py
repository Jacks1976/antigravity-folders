import sys
import os
import argparse
import json
import datetime

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token

def get_list_events(token=None, ministry_id=None):
    # Default Viewer Context
    viewer_status = 'Public'
    viewer_ministries = set()
    viewer_id = None
    
    if token:
        payload = decode_access_token(token)
        if payload:
            viewer_id = payload['sub']
            # We should verify status from DB to be compliant with "strict status gating"
            # But for list_events performance, maybe rely on token if we trust it?
            # Re-querying DB for status is safer.
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM users WHERE id = ?", (viewer_id,))
                row = cursor.fetchone()
                if row:
                    viewer_status = row['status'] # Pending, Active, Banned
                    
                if viewer_status == 'Active':
                    # Get Ministries
                    cursor.execute("""
                        SELECT ministry_id FROM ministry_assignments 
                        WHERE user_id = ? AND deleted_at IS NULL
                    """, (viewer_id,))
                    viewer_ministries = {r[0] for r in cursor.fetchall()}

    # Query Events
    # We'll fetch all future events (and recent past? let's fail to limit purely by date for now, just fetch all)
    # Optimization: Filter `is_public=1` in SQL if viewer is not Active.
    
    query = "SELECT * FROM events WHERE deleted_at IS NULL"
    params = []
    
    if viewer_status != 'Active':
        query += " AND is_public = 1"
    
    query += " ORDER BY start_at ASC"
    
    # Execution
    results = []
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        for row in rows:
            event = dict(row)
            is_public = bool(event['is_public'])
            
            # Visibility Check (Python side for Internal logic)
            if not is_public and viewer_status == 'Active':
                # Check targets
                try:
                    targets = json.loads(event['target_ministry_ids'])
                except:
                    targets = []
                
                # Rule: NULL or [] => All Active
                if not targets:
                    pass # Visible
                else:
                    # Check overlap
                    if not set(targets).intersection(viewer_ministries):
                        continue # Skip this event, not for you

            # Format Response
            # Add RSVP status if logged in?
            # For MVP just list the event details.
            # Client can fetch RSVP separately or we join it. 
            # Let's simple fetch.
            
            results.append({
                "id": event['id'],
                "title": event['title'],
                "description": event['description'],
                "start": event['start_at'],
                "end": event['end_at'],
                "location": event['location'],
                "public": is_public,
                "rsvp_required": bool(event['rsvp_required'])
            })

    print(json.dumps({"results": results, "count": len(results)}))

import sqlite3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token")
    parser.add_argument("--ministry-id", help="Filter by ministry (not implemented in MVP logic yet)")
    
    args = parser.parse_args()
    get_list_events(args.token, args.ministry_id)
