import subprocess
import sys
import os
import json
import time

PYTHON_EXEC = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTH_DIR = os.path.join(BASE_DIR, 'execution', 'auth')

# Helper to run scripts
def run_script(script_name, args):
    cmd = [PYTHON_EXEC, os.path.join(AUTH_DIR, script_name)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    return result

def parse_output(output):
    # Try to find JSON object in the output (scan lines in reverse)
    lines = output.strip().split('\n')
    for line in reversed(lines):
        try:
             if line.strip().startswith('{'):
                return json.loads(line)
        except:
             continue
    return None

def test_auth_flow():
    print("=== STARTING AUTH SMOKE TEST ===")
    
    # Generate unique email
    timestamp = int(time.time())
    email = f"testuser_{timestamp}@example.com"
    password = "TestUser123!"
    new_password = "NewPassword123!"
    
    print(f"\n[1] Registering User: {email}")
    res = run_script("register.py", ["--email", email, "--password", password, "--name", "Test User"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        print("PASS: Registration successful")
    else:
        print(f"FAIL: Registration failed. Output: {res.stdout}")
        print(f"STDERR: {res.stderr}")
        return

    print(f"\n[2] Attempt Login (Pending Status)")
    res = run_script("login.py", ["--email", email, "--password", password])
    data = parse_output(res.stdout)
    if data and data.get("error") == "auth.account_pending":
        print("PASS: Pending user blocked correctly")
    else:
        print(f"FAIL: Expected pending error. Got: {res.stdout}")
        print(f"STDERR: {res.stderr}")

    print(f"\n[3] Approve User (Admin Action)")
    # Using hardcoded admin id 999 for audit log test
    res = run_script("approve_user.py", ["--email", email, "--admin-id", "999"])
    data = parse_output(res.stdout)
    if data and data.get("success"):
        print("PASS: User approved")
    else:
        print(f"FAIL: Approval failed. Output: {res.stdout}")
        print(f"STDERR: {res.stderr}")
        return

    print(f"\n[4] Attempt Login (Active Status)")
    res = run_script("login.py", ["--email", email, "--password", password])
    data = parse_output(res.stdout)
    if data and data.get("success") and "token" in data:
        print("PASS: Login successful. Token received.")
    else:
        print(f"FAIL: Login failed. Output: {res.stdout}")
        print(f"STDERR: {res.stderr}")

    print(f"\n[5] Password Reset Request")
    res = run_script("request_password_reset.py", ["--email", email])
    # Capture stderr for token
    stderr = res.stderr
    token = None
    if "token=" in stderr: 
        import re
        match = re.search(r"token=([a-f0-9\-]+)", stderr)
        if match:
            token = match.group(1)
            print(f"PASS: Reset token captured: {token}")
        else:
            print("FAIL: Could not extract token from stderr")
    else:
        print(f"FAIL: Token debug message not found in stderr. Stderr: {stderr}")
        # Note: In production we wouldn't print to stderr, but for this test script we need it. 
        # I wrote `sys.stderr.write(f"[DEBUG] Password Reset Link: /reset-password?token={token}\n")` in request_password_reset.py.
        
    if token:
        print(f"\n[6] Confirm Password Reset")
        res = run_script("confirm_password_reset.py", ["--token", token, "--password", new_password])
        data = parse_output(res.stdout)
        if data and data.get("success"):
            print("PASS: Password reset confirmed")
        else:
            print(f"FAIL: Reset confirm failed. Output: {res.stdout}")

        print(f"\n[7] Login with Old Password (Should Fail)")
        res = run_script("login.py", ["--email", email, "--password", password])
        data = parse_output(res.stdout)
        if data and data.get("error") == "auth.invalid_credentials":
            print("PASS: Old password rejected")
        else:
             print(f"FAIL: Old password should fail. Output: {res.stdout}")

        print(f"\n[8] Login with New Password (Should Succeed)")
        res = run_script("login.py", ["--email", email, "--password", new_password])
        data = parse_output(res.stdout)
        if data and data.get("success"):
            print("PASS: New password accepted")
        else:
             print(f"FAIL: New password failed. Output: {res.stdout}")

    print(f"\n[9] Rate Limit Test (5 failures)")
    # Reset limit? It tracks by IP/Email.
    # We'll use a new random email to test IP limiting? 
    # Or just spam failures for this user.
    # IP is always 127.0.0.1 in the script default.
    # There are already some failures above maybe? No, mostly successes.
    # Let's try 6 failures.
    for i in range(1, 7):
        print(f"  Attempt {i}...", end=" ")
        res = run_script("login.py", ["--email", email, "--password", "badpass"])
        data = parse_output(res.stdout)
        if data and data.get("error") == "auth.too_many_attempts":
            print("PASS: Rate limit hit.")
            break
        elif data and data.get("error") == "auth.invalid_credentials":
            print("Invalid Creds (OK)")
        else:
            print(f"Unexpected: {res.stdout}")
            
    print("\n=== SMOKE TEST COMPLETE ===")

if __name__ == "__main__":
    test_auth_flow()
