import sys
import os
import argparse
import json
import datetime
from datetime import timezone

# Add execution directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.utils import decode_access_token
from infra.audit_logger import log_audit_event

def get_current_user(token):
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload

def create_event(token, title, start_at, end_at, description=None, location=None, is_public=False, rsvp_required=False, target_ministry_ids=None):
    user = get_current_user(token)
    if not user:
        print(json.dumps({"error": "auth.unauthorized"}))
        return

    actor_id = user['sub']
    actor_role = user['role']
    
    # Permission: Staff/Admin only
    if actor_role not in ('Admin', 'Staff'):
        print(json.dumps({"error": "auth.forbidden"}))
        return

    # Validation
    try:
        # Parse ISO strings to check validity (DB expects ISO strings, but let's validate logic)
        # Using python's fromisoformat
        start_dt = datetime.datetime.fromisoformat(start_at.replace('Z', '+00:00'))
        end_dt = datetime.datetime.fromisoformat(end_at.replace('Z', '+00:00'))
        
        if end_dt <= start_dt:
            print(json.dumps({"error": "event.invalid_dates"}))
            return
            
    except ValueError:
        print(json.dumps({"error": "event.invalid_date_format"}))
        return

    # Check target_ministries is valid JSON
    if target_ministry_ids:
        try:
             json.loads(target_ministry_ids)
        except:
             # If passed as "1,2", convert to JSON array
             if ',' in target_ministry_ids or target_ministry_ids.isdigit():
                 ids = [int(x.strip()) for x in target_ministry_ids.split(',') if x.strip().isdigit()]
                 target_ministry_ids = json.dumps(ids)
             else:
                 target_ministry_ids = '[]'
    else:
        target_ministry_ids = '[]'

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO events (
                    title, description, start_at, end_at, location, 
                    is_public, rsvp_required, target_ministry_ids, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title, description, start_at, end_at, location, 
                1 if is_public else 0, 
                1 if rsvp_required else 0, 
                target_ministry_ids, 
                actor_id
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            
            # Audit
            log_audit_event(
                actor_id=actor_id,
                action_type='EVENT_CREATE',
                resource_type='event',
                resource_id=event_id,
                metadata={'title': title}
            )
            
            print(json.dumps({
                "success": True, 
                "event_id": event_id,
                "message": "event.created_success"
            }))

    except Exception as e:
        print(json.dumps({"error": f"Internal Error: {str(e)}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--start", required=True, help="ISO format UTC")
    parser.add_argument("--end", required=True, help="ISO format UTC")
    parser.add_argument("--description")
    parser.add_argument("--location")
    parser.add_argument("--public", action='store_true')
    parser.add_argument("--rsvp-required", action='store_true')
    parser.add_argument("--targets", help="JSON array of ministry IDs or comma separated")
    
    args = parser.parse_args()
    create_event(args.token, args.title, args.start, args.end, args.description, args.location, args.public, args.rsvp_required, args.targets)
