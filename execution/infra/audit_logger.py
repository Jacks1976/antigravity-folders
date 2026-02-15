from db import get_db_connection
import json
from datetime import datetime

def log_audit_event(actor_id, action_type, resource_type=None, resource_id=None, metadata=None, ip_address='0.0.0.0'):
    """
    Logs a system event to the audit_logs table.
    """
    if isinstance(metadata, dict):
        metadata = json.dumps(metadata)
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (actor_id, action_type, resource_type, resource_id, metadata, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (actor_id, action_type, resource_type, str(resource_id) if resource_id else None, metadata, ip_address))
        conn.commit()
    
    print(f"[AUDIT] {action_type} by User {actor_id}")

if __name__ == '__main__':
    # Test logger
    log_audit_event(1, "TEST_EVENT", "resource_123", {"foo": "bar"})
