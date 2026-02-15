import sys
import os
import argparse
import json
import datetime

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token
from infra.audit_logger import log_audit_event

def rsvp_action(token, event_id, status):
    payload = decode_access_token(token)
    if not payload:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    user_id = payload['sub']
    
    # DB Check for Status='Active'
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row or row['status'] != 'Active':
             print(json.dumps({"error": "auth.account_pending"})) # Only Active can RSVP
             return

        # Check Event
        cursor.execute("SELECT id, start_at FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            print(json.dumps({"error": "event.not_found"}))
            return
            
        # Check Values
        if status not in ('going', 'maybe', 'not_going'):
            print(json.dumps({"error": "event.invalid_rsvp_status"}))
            return
            
        # Insert/Update (Upsert)
        # Sqlite UPSERT syntax: INSERT INTO ... ON CONFLICT(pk) DO UPDATE SET ...
        try:
            cursor.execute("""
                INSERT INTO event_rsvps (event_id, user_id, status)
                VALUES (?, ?, ?)
                ON CONFLICT(event_id, user_id) DO UPDATE SET
                    status = excluded.status,
                    updated_at = CURRENT_TIMESTAMP
            """, (event_id, user_id, status))
            
            conn.commit()
            
            # Audit
            log_audit_event(
                actor_id=user_id,
                action_type='RSVP_CHANGE',
                resource_type='event',
                resource_id=event_id,
                metadata={'status': status}
            )
            
            print(json.dumps({"success": True, "message": "event.rsvp_saved"}))
            
        except Exception as e:
            print(json.dumps({"error": f"Internal Error: {str(e)}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--status", required=True)
    
    args = parser.parse_args()
    rsvp_action(args.token, args.event_id, args.status)
