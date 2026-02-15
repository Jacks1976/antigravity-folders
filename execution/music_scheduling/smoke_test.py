"""
Smoke test for music scheduling module.
Tests service plans, setlists, and roster management.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_scheduling.core import (
    create_service_plan_core, add_setlist_song_core,
    assign_roster_entry_core, update_roster_status_core, list_plans_core
)
from music_repertoire.core import create_song_core
from db import get_db_connection

def test_scheduling():
    """Test scheduling operations."""
    print("=== Music Scheduling Smoke Test ===\n")
    
    # Get test users
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE role = 'Admin' LIMIT 1")
        admin = cursor.fetchone()
        
        cursor.execute("SELECT id FROM users WHERE role = 'Member' LIMIT 1")
        member = cursor.fetchone()
        
        if not admin:
            print("[FAIL] No admin user found")
            return False
        
        admin_id = admin['id']
        member_id = member['id'] if member else admin_id
    
    # Create a test song first
    song_result = create_song_core(admin_id, "Test Worship Song", "Test Artist")
    if not song_result['ok']:
        print("[FAIL] Could not create test song")
        return False
    song_id = song_result['data']['song_id']
    
    # Test 1: Create service plan
    print("Test 1: Create service plan")
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    result = create_service_plan_core(admin_id, future_date, notes="Sunday service")
    
    if not result['ok']:
        print(f"[FAIL] Create plan failed: {result['error_key']}")
        return False
    
    plan_id = result['data']['plan_id']
    print(f"[PASS] Created plan ID: {plan_id}\n")
    
    # Test 2: Add song to setlist
    print("Test 2: Add song to setlist")
    result = add_setlist_song_core(admin_id, plan_id, song_id, 1)
    
    if not result['ok']:
        print(f"[FAIL] Add setlist song failed: {result['error_key']}")
        return False
    
    print(f"[PASS] Added song to setlist\n")
    
    # Test 3: Assign roster entry
    print("Test 3: Assign roster entry")
    result = assign_roster_entry_core(admin_id, plan_id, member_id, "Guitar")
    
    if not result['ok']:
        print(f"[FAIL] Assign roster failed: {result['error_key']}")
        return False
    
    roster_id = result['data']['roster_id']
    print(f"[PASS] Assigned roster ID: {roster_id}\n")
    
    # Test 4: Update roster status
    print("Test 4: Update roster status")
    result = update_roster_status_core(member_id, roster_id, "confirmed")
    
    if not result['ok']:
        print(f"[FAIL] Update status failed: {result['error_key']}")
        return False
    
    print(f"[PASS] Updated roster status\n")
    
    # Test 5: List plans
    print("Test 5: List plans")
    result = list_plans_core(admin_id)
    
    if not result['ok'] or len(result['data']['results']) == 0:
        print(f"[FAIL] List plans failed")
        return False
    
    print(f"[PASS] Found {len(result['data']['results'])} plans\n")
    
    print("=== All Tests PASSED ===")
    return True

if __name__ == "__main__":
    success = test_scheduling()
    sys.exit(0 if success else 1)
