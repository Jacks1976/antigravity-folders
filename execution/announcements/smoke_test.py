import subprocess
import sys
import os
import json
import time

PYTHON_EXEC = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(BASE_DIR, 'execution')
ANNOUNCE_DIR = os.path.join(EXEC_DIR, 'announcements')
MEMBERS_DIR = os.path.join(EXEC_DIR, 'members')
AUTH_DIR = os.path.join(EXEC_DIR, 'auth')

# Helper to capture run result
def run_cmd(script, args):
    cmd = [PYTHON_EXEC, script] + args
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=EXEC_DIR)
    return res

def parse_res(res):
    try:
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

def test_announcements_flow():
    print("=== STARTING ANNOUNCEMENTS SMOKE TEST ===")
    ts = int(time.time())

    # 1. Setup Users
    admin_email = f"admin_an_{ts}@test.com"
    musician_email = f"music_an_{ts}@test.com"
    normie_email = f"normie_an_{ts}@test.com"
    password = "TestUser123!"

    # Create Admin
    print(f"\n[1] Creating Admin: {admin_email}")
    res = run_cmd(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                  ["--email", admin_email, "--name", "Admin User", "--password", password, "--role", "Admin", "--status", "Active"])
    data = parse_res(res)
    if not data or not data.get("success"):
        print(f"FAIL: Admin create. Output: {res.stdout}")
        return
    admin_token = parse_res(run_cmd(os.path.join(AUTH_DIR, "login.py"), ["--email", admin_email, "--password", password]))["token"]
    admin_id = str(data["user_id"])

    # Create Musician (Role=Musician)
    # create_profile.py sets role=Pending by default. We need to set Role=Musician.
    # We can pass --role "Musician" to create_profile!
    print(f"[2] Creating Musician User: {musician_email}")
    res = run_cmd(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                  ["--admin-id", admin_id, "--email", musician_email, "--name", "Music User", "--password", password, "--role", "Musician", "--status", "Active"])
    data = parse_res(res)
    musician_token = parse_res(run_cmd(os.path.join(AUTH_DIR, "login.py"), ["--email", musician_email, "--password", password]))["token"]
    musician_id = str(data["user_id"])

    # Create Normie (Role=Member)
    print(f"[3] Creating Normie User: {normie_email}")
    res = run_cmd(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                  ["--admin-id", admin_id, "--email", normie_email, "--name", "Normie User", "--password", password, "--role", "Member", "--status", "Active"])
    data = parse_res(res)
    normie_token = parse_res(run_cmd(os.path.join(AUTH_DIR, "login.py"), ["--email", normie_email, "--password", password]))["token"]

    # 2. Post Messages
    print(f"\n[4] Posting Announcements")
    
    # Global
    res = run_cmd(os.path.join(ANNOUNCE_DIR, "post_message.py"), [
        "--token", admin_token, "--title", "Global News", "--body", "Hello World"
    ])
    global_id = parse_res(res)["announcement_id"]
    print(f"  Created Global ID: {global_id}")

    # Role Specific (Musician)
    res = run_cmd(os.path.join(ANNOUNCE_DIR, "post_message.py"), [
        "--token", admin_token, "--title", "Band Practice", "--target-type", "Role", "--target-id", "Musician"
    ])
    role_id = parse_res(res)["announcement_id"]
    print(f"  Created Role ID: {role_id}")
    
    # Expired Global
    res = run_cmd(os.path.join(ANNOUNCE_DIR, "post_message.py"), [
        "--token", admin_token, "--title", "Old News", "--expires-at", "2020-01-01T10:00:00"
    ])
    expired_id = parse_res(res)["announcement_id"]
    print(f"  Created Expired ID: {expired_id}")

    # Pinned Global
    res = run_cmd(os.path.join(ANNOUNCE_DIR, "post_message.py"), [
        "--token", admin_token, "--title", "Important!", "--pinned"
    ])
    pinned_id = parse_res(res)["announcement_id"]
    print(f"  Created Pinned ID: {pinned_id}")

    # 3. Check Feeds
    print(f"\n[5] Checking Feeds")

    # Musician Feed
    print("  Checking Musician Feed...")
    res = run_cmd(os.path.join(ANNOUNCE_DIR, "get_feed.py"), ["--token", musician_token])
    data = parse_res(res)
    ids = [a['id'] for a in data['results']]
    
    # Needs: Global, Role, Pinned
    # Hidden: Expired
    if global_id in ids and role_id in ids and pinned_id in ids:
        print("    PASS: Sees Global, Role, Pinned")
    else:
        print(f"    FAIL: Missing expected IDs. Got: {ids}")
        
    if expired_id in ids:
        print(f"    FAIL: Saw Expired ID {expired_id}")
    else:
        print("    PASS: Expired hidden")

    # Order Check: Pinned should be first
    if ids[0] == pinned_id:
        print("    PASS: Pinned is first")
    else:
        print(f"    FAIL: Pinned not first. First is {ids[0]}")

    # Normie Feed
    print("  Checking Normie Feed...")
    res = run_cmd(os.path.join(ANNOUNCE_DIR, "get_feed.py"), ["--token", normie_token])
    data = parse_res(res)
    ids = [a['id'] for a in data['results']]
    
    if role_id in ids:
        print(f"    FAIL: SAW Role ID {role_id} (Should be hidden)")
    else:
        print("    PASS: Role-specific hidden")
        
    if global_id in ids and pinned_id in ids:
         print("    PASS: Sees Global")
         
    print("\n=== ANNOUNCEMENTS SMOKE TEST COMPLETE ===")

if __name__ == "__main__":
    test_announcements_flow()
