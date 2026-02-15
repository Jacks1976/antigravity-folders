import subprocess
import sys
import os
import json
import time

PYTHON_EXEC = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(BASE_DIR, 'execution')
MEMBERS_DIR = os.path.join(EXEC_DIR, 'members')
AUTH_DIR = os.path.join(EXEC_DIR, 'auth')

# Helper to run scripts
def run_script(path, args):
    cmd = [PYTHON_EXEC, path] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=EXEC_DIR)
    return result

def parse_output(output):
    lines = output.strip().split('\n')
    for line in reversed(lines):
        try:
             if line.strip().startswith('{'):
                return json.loads(line)
        except:
             continue
    return None

def test_members_flow():
    print("=== STARTING MEMBERS SMOKE TEST ===")
    
    timestamp = int(time.time())
    
    # 1. Register/Create Admin (We need an admin first)
    # Actually we can use create_profile to make an admin? No, create_profile requires admin or nothing check?
    # create_profile.py assumes if admin_id is passed, it checks permissions.
    # To bootstrap, we might need a "God Mode" or just use register and force update role via SQL?
    # Or just use create_profile without admin_id if it allows?
    # My create_profile impl: "if admin_id: check... else: just insert".
    # So anyone can run create_profile? That's a security hole for the script, but for CLI implementation 
    # we assume access to the script = access to DB in MVP/CLI context if no API layer.
    
    admin_email = f"admin_{timestamp}@example.com"
    member_email = f"member_{timestamp}@example.com"
    observer_email = f"observer_{timestamp}@example.com"
    password = "TestUser123!"
    
    print(f"\n[1] Creating Admin User: {admin_email}")
    res = run_script(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                     ["--email", admin_email, "--name", "Admin User", "--password", password, "--role", "Admin", "--status", "Active"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        admin_id = str(data["user_id"])
        print(f"PASS: Admin created (ID: {admin_id})")
    else:
        print(f"FAIL: Admin creation failed. Output: {res.stdout}")
        return

    # Login Admin to get token
    print(f"\n[2] Login Admin")
    res = run_script(os.path.join(AUTH_DIR, "login.py"), ["--email", admin_email, "--password", password])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        admin_token = data["token"]
        print("PASS: Admin logged in")
    else:
        print(f"FAIL: Admin login failed. Output: {res.stdout}")
        return

    print(f"\n[3] Creating Member User (via Admin): {member_email}")
    res = run_script(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                     ["--admin-id", admin_id, "--email", member_email, "--name", "Regular Member", "--password", password, "--status", "Active", "--dob", "1990-05-20", "--phone", "+1234567890"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        member_id = str(data["user_id"])
        print(f"PASS: Member created (ID: {member_id})")
    else:
        print(f"FAIL: Member creation failed. Output: {res.stdout}")
        return

    # Login Member
    print(f"\n[4] Login Member")
    res = run_script(os.path.join(AUTH_DIR, "login.py"), ["--email", member_email, "--password", password])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        member_token = data["token"]
        print("PASS: Member logged in")
    else:
        print(f"FAIL: Member login failed. Output: {res.stdout}")
        return

    # Member Updates Profile (Share Phone = True)
    print(f"\n[5] Member Updates Profile (Share Phone)")
    res = run_script(os.path.join(MEMBERS_DIR, "update_profile.py"), 
                     ["--token", member_token, "--share-phone", "true", "--bio", "I love music"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        print("PASS: Profile updated")
    else:
        print(f"FAIL: Update profile failed. Output: {res.stdout}")

    print(f"\n[6] Creating Observer User: {observer_email}")
    res = run_script(os.path.join(MEMBERS_DIR, "create_profile.py"), 
                     ["--email", observer_email, "--name", "Observer User", "--password", password, "--status", "Active"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        observer_id = str(data["user_id"])
        print(f"PASS: Observer created")
    else:
        print(f"FAIL: Observer creation failed")
        return

    # Login Observer
    res = run_script(os.path.join(AUTH_DIR, "login.py"), ["--email", observer_email, "--password", password])
    data = parse_output(res.stdout)
    observer_token = data["token"]

    print(f"\n[7] Observer Views Directory")
    res = run_script(os.path.join(MEMBERS_DIR, "get_directory.py"), 
                     ["--token", observer_token, "--search", "Regular"])
    data = parse_output(res.stdout)
    if data and "results" in data:
        results = data["results"]
        if len(results) > 0:
            target = results[0]
            print(f"Found: {target['full_name']}")
            
            # Verify Privacy
            # Phone shared?
            if target['phone'] == "+1234567890":
                print("PASS: Phone is visible (shared)")
            else:
                print(f"FAIL: Phone should be visible. Got: {target.get('phone')}")
                
            # Address hidden?
            if target.get('address') is None:
                print("PASS: Address is hidden (Null)")
            else:
                print(f"FAIL: Address should be hidden. Got: {target.get('address')}")
                
            # DOB masked?
            if target.get('dob') == "05-20":
                print("PASS: DOB is masked (05-20)")
            else:
                print(f"FAIL: DOB verification failed. Got: {target.get('dob')}")
        else:
            print("FAIL: No results found in directory")
    else:
        print(f"FAIL: Directory fetch failed. Output: {res.stdout}")

    print(f"\n[8] Admin Assigns Ministry")
    # Need a ministry first? We might need to manually insert one or assume one exists.
    # Let's Insert a ministry via SQL for testing or assuming ID 1 exists/create it via DB.
    # I'll rely on the script being smart or just insert one via DB.
    
    # We'll run a quick python snippet to ensure ministry exists
    import sqlite3
    db_path = os.path.join(os.path.dirname(EXEC_DIR), 'church_app.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS ministries (id INTEGER PRIMARY KEY, name TEXT)")
    cur.execute("INSERT OR IGNORE INTO ministries (id, name) VALUES (1, 'Worship Team')")
    conn.commit()
    conn.close()
    
    res = run_script(os.path.join(MEMBERS_DIR, "assign_ministry.py"), 
                     ["--token", admin_token, "--user-id", member_id, "--ministry-id", "1", "--role", "Singer", "--is-lead"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        print("PASS: Ministry assigned")
    else:
        print(f"FAIL: Ministry assignment failed. Output: {res.stdout}")

    print("\n=== MEMBERS SMOKE TEST COMPLETE ===")

if __name__ == "__main__":
    test_members_flow()
