#!/usr/bin/env python3
"""
Standalone admin setup - writes result to file only.
"""
import sys
import os

RESULT_FILE = r"C:\Users\dieke\Documents\Antigravity folders\ADMIN_SETUP_RESULT.txt"

def setup():
    try:
        import sqlite3
        from argon2 import PasswordHasher
        
        DB = r"C:\Users\dieke\Documents\Antigravity folders\church_app.db"
        EMAIL = "admin@dev.localhost.com"
        PASSWORD = "DevAdmin123!"
        
        # Write progress
        with open(RESULT_FILE, 'w') as f:
            f.write("Starting admin setup...\n")
        
        # Check DB
        if not os.path.exists(DB):
            with open(RESULT_FILE, 'a') as f:
                f.write(f"ERROR: DB not found at {DB}\n")
            return False
        
        # Hash password
        ph = PasswordHasher()
        pw_hash = ph.hash(PASSWORD)
        
        # Connect and setup
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        
        # Check if exists
        cur.execute("SELECT id FROM users WHERE email=?", (EMAIL,))
        user = cur.fetchone()
        
        if user:
            uid = user[0]
            cur.execute(
                "UPDATE users SET password_hash=?, role=?, status=?, organization_id=? WHERE id=?",
                (pw_hash, 'Admin', 'Active', 1, uid)
            )
            with open(RESULT_FILE, 'a') as f:
                f.write(f"Updated user id={uid}\n")
        else:
            cur.execute(
                "INSERT INTO users (email, password_hash, role, status, organization_id) VALUES (?, ?, ?, ?, ?)",
                (EMAIL, pw_hash, 'Admin', 'Active', 1)
            )
            uid = cur.lastrowid
            with open(RESULT_FILE, 'a') as f:
                f.write(f"Created user id={uid}\n")
        
        conn.commit()
        
        # Verify
        cur.execute("SELECT id, email, role, status FROM users WHERE id=?", (uid,))
        result = cur.fetchone()
        conn.close()
        
        if result:
            with open(RESULT_FILE, 'a') as f:
                f.write(f"VERIFIED: id={result[0]}, email={result[1]}, role={result[2]}, status={result[3]}\n")
                f.write(f"SUCCESS: Admin is ready!\n")
                f.write(f"Login with: {EMAIL} / {PASSWORD}\n")
            return True
        else:
            with open(RESULT_FILE, 'a') as f:
                f.write("ERROR: Verification failed\n")
            return False
            
    except Exception as e:
        with open(RESULT_FILE, 'a') as f:
            f.write(f"EXCEPTION: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = setup()
    sys.exit(0 if success else 1)
