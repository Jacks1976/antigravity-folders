#!/usr/bin/env python3
import sys
sys.path.insert(0, r"C:\Users\dieke\Documents\Antigravity folders")

try:
    import sqlite3
    import os
    from argon2 import PasswordHasher
    
    DB = r"C:\Users\dieke\Documents\Antigravity folders\execution\church_app.db"
    EMAIL = "admin@dev.localhost.com"
    PWD = "DevAdmin123!"
    
    if not os.path.exists(DB):
        print("FAIL: DB not found")
        sys.exit(1)
    
    ph = PasswordHasher()
    hash_val = ph.hash(PWD)
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # Check if exists
    cur.execute("SELECT id FROM users WHERE email=?", (EMAIL,))
    user = cur.fetchone()
    
    if user:
        uid = user[0]
        cur.execute("UPDATE users SET password_hash=?, role=?, status=?, organization_id=? WHERE id=?", 
                   (hash_val, 'Admin', 'Active', 1, uid))
    else:
        cur.execute("INSERT INTO users (email, password_hash, role, status, organization_id) VALUES (?, ?, ?, ?, ?)",
                   (EMAIL, hash_val, 'Admin', 'Active', 1))
        uid = cur.lastrowid
    
    conn.commit()
    
    # Verify
    cur.execute("SELECT id, email, role, status FROM users WHERE id=?", (uid,))
    result = cur.fetchone()
    conn.close()
    
    if result:
        print(f"SUCCESS: id={result[0]}, email={result[1]}, role={result[2]}, status={result[3]}")
    else:
        print("FAIL: Could not verify")
        sys.exit(1)
        
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
