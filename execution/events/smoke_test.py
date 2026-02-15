import subprocess
import sys
import os
import json
import time

PYTHON_EXEC = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(BASE_DIR, 'execution')
EVENTS_DIR = os.path.join(EXEC_DIR, 'events')
MEMBERS_DIR = os.path.join(EXEC_DIR, 'members')
AUTH_DIR = os.path.join(EXEC_DIR, 'auth')

def run_cmd(script, args):
    cmd = [PYTHON_EXEC, script] + args
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=EXEC_DIR)
    return res

def parse_res(res):
    try:
        # scan for json
        lines = res.stdout.strip().split('\n')
        for line in reversed(lines):
            try:
                if line.strip().startswith('{'):
                    return json.loads(line)
            except:
                continue
    except:
        pass
    return None

def test_events_flow():
    print("=== STARTING EVENTS SMOKE TEST ===")
    ts = int(time.time())
    
    # 1. Setup Users
    admin_email = f"admin_ev_{ts}@test.com"
    member_email = f"member_ev_{ts}@test.com"
    pending_email = f"pending_ev_{ts}@test.com"
    password = "TestUser123!"
    
    # Create Admin
    print(f"\n[1] Creating Admin: {admin_email}")
    res = run_cmd(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                  ["--email", admin_email, "--name", "Admin User", "--password", password, "--role", "Admin", "--status", "Active"])
    data = parse_res(res)
    if not data or not data.get("success"):
        print(f"FAIL: Admin create. Output: {res.stdout}")
        return
    admin_id = str(data["user_id"])
    
    # Login Admin
    res = run_cmd(os.path.join(AUTH_DIR, "login.py"), ["--email", admin_email, "--password", password])
    admin_token_data = parse_res(res)
    if not admin_token_data or not admin_token_data.get("token"):
         print(f"FAIL: Admin Login. Output: {res.stdout}")
         return
    admin_token = admin_token_data["token"]

    # Create Member (Active)
    print(f"[2] Creating Active Member: {member_email}")
    res = run_cmd(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                  ["--admin-id", admin_id, "--email", member_email, "--name", "Active Member", "--password", password, "--status", "Active"])
    # NOTE: create_profile uses admin_id for logging/check
    data = parse_res(res)
    if not data or "user_id" not in data:
         print(f"FAIL: Member Create. Output: {res.stdout}")
         return
    member_id = str(data["user_id"])
    
    # Login Member
    res = run_cmd(os.path.join(AUTH_DIR, "login.py"), ["--email", member_email, "--password", password])
    member_token = parse_res(res)["token"]

    # Create Pending User
    print(f"[3] Creating Pending User: {pending_email}")
    res = run_cmd(os.path.join(AUTH_DIR, "register.py"), 
                  ["--email", pending_email, "--name", "Pending User", "--password", password])
    # Login Pending (Login allows pending but returns error? No, wait. Login checks status. 
    # Actually my login script returns error if pending usually. 
    # But wait, list_events might work with NO token? 
    # Or needs a token but handles pending status? 
    # My "login.py" blocks pending. So Pending user cannot get a token usually.
    # If they can't login, they can't have a token.
    # So "Pending User" viewing events implies unauthenticated or partially authenticated?
    # Requirement: "Public: public events only". "Pending: must not view internal".
    # If Pending cannot login, they are effectively Public.
    # Unless we have a mechanism where they are logged in but pending?
    # My login.py blocks pending. So assume Pending = Public for this test (No Token).
    # But I will also test "Invalid Token" or just No Token.
    
    # Let's create events.
    print(f"\n[4] Creating Events")
    # Public Event
    res = run_cmd(os.path.join(EVENTS_DIR, "create_event.py"), [
        "--token", admin_token, 
        "--title", "Public Worship", 
        "--start", "2026-12-25T10:00:00", 
        "--end", "2026-12-25T12:00:00", 
        "--public"
    ])
    public_evt_id = parse_res(res)["event_id"]
    print(f"  Created Public Event ID: {public_evt_id}")

    # Internal Event (All Active)
    res = run_cmd(os.path.join(EVENTS_DIR, "create_event.py"), [
        "--token", admin_token, 
        "--title", "Members Meeting", 
        "--start", "2026-12-26T18:00:00", 
        "--end", "2026-12-26T20:00:00"
    ])
    internal_evt_id = parse_res(res)["event_id"]
    print(f"  Created Internal Event ID: {internal_evt_id}")
    
    # Internal Targeted Event (Ministry 999 - unlikely to exist/be assigned)
    res = run_cmd(os.path.join(EVENTS_DIR, "create_event.py"), [
        "--token", admin_token, 
        "--title", "Secret Leadership", 
        "--start", "2026-12-27T10:00:00", 
        "--end", "2026-12-27T12:00:00",
        "--targets", "[999]"
    ])
    targeted_evt_id = parse_res(res)["event_id"]
    print(f"  Created Targeted Event ID: {targeted_evt_id}")

    # 5. Visibility Tests
    print(f"\n[5] Testing Visibility")
    
    # Case A: Public (No Token)
    print("  Testing Public Access (No Token)...")
    res = run_cmd(os.path.join(EVENTS_DIR, "list_events.py"), [])
    data = parse_res(res)
    ids = [e['id'] for e in data['results']]
    if public_evt_id in ids and internal_evt_id not in ids:
        print("    PASS: Sees Public Only")
    else:
        print(f"    FAIL: IDs={ids}")
        
    # Case B: Active Member (No Ministry)
    print("  Testing Active Member Access...")
    res = run_cmd(os.path.join(EVENTS_DIR, "list_events.py"), ["--token", member_token])
    data = parse_res(res)
    ids = [e['id'] for e in data['results']]
    if public_evt_id in ids and internal_evt_id in ids and targeted_evt_id not in ids:
        print("    PASS: Sees Public + Internal(Global). Targeted hidden.")
    else:
        print(f"    FAIL: IDs={ids}")

    # 6. RSVP Tests
    print(f"\n[6] Testing RSVP")
    
    # Active requests specific event (Internal)
    res = run_cmd(os.path.join(EVENTS_DIR, "rsvp_action.py"), [
        "--token", member_token,
        "--event-id", str(internal_evt_id),
        "--status", "going"
    ])
    data = parse_res(res)
    if data and data.get("success"):
        print("    PASS: RSVP Saved")
    else:
        print(f"    FAIL: RSVP Error: {res.stdout}")

    # Verify duplicate update
    res = run_cmd(os.path.join(EVENTS_DIR, "rsvp_action.py"), [
        "--token", member_token,
        "--event-id", str(internal_evt_id),
        "--status", "maybe"
    ])
    data = parse_res(res)
    if data and data.get("success"):
        print("    PASS: RSVP Updated")
    else:
        print(f"    FAIL: RSVP Update Error: {res.stdout}")
        
    print("\n=== SMOKE TEST COMPLETE ===")

if __name__ == "__main__":
    test_events_flow()
