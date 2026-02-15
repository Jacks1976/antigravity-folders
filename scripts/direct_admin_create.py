#!/usr/bin/env python3
"""Direct script to create/reset dev admin without complex imports."""
import sqlite3
import os
from argon2 import PasswordHasher

DB_PATH = r"C:\Users\dieke\Documents\Antigravity folders\execution\church_app.db"
EMAIL = "admin@dev.localhost.com"
PASSWORD = "DevAdmin123!"
ORG_ID = 1  # Default org

# Verify DB exists
if not os.path.exists(DB_PATH):
    print(f"ERROR: DB not found at {DB_PATH}")
    exit(1)

print(f"OK_DB_FOUND: {DB_PATH}")

# Hash password
ph = PasswordHasher()
pw_hash = ph.hash(PASSWORD)
print(f"OK_PASSWORD_HASHED")

# Connect to DB
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check if user exists
cur.execute("SELECT id, email, role FROM users WHERE email = ?", (EMAIL,))
existing = cur.fetchone()

if existing:
    # Update existing user
    uid = existing['id']
    print(f"OK_USER_EXISTS id={uid}")
    cur.execute(
        "UPDATE users SET password_hash = ?, role = ?, status = ?, organization_id = ? WHERE id = ?",
        (pw_hash, "Admin", "Active", ORG_ID, uid)
    )
    conn.commit()
    print(f"OK_USER_UPDATED")
else:
    # Create new user
    print(f"OK_USER_CREATE_START")
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash, role, status, organization_id) VALUES (?, ?, ?, ?, ?)",
            (EMAIL, pw_hash, "Admin", "Active", ORG_ID)
        )
        conn.commit()
        uid = cur.lastrowid
        print(f"OK_USER_CREATED id={uid}")
    except Exception as e:
        print(f"ERROR_INSERT: {e}")
        conn.close()
        exit(1)

# Create or update member_profile
cur.execute("SELECT id FROM member_profiles WHERE user_id = ?", (uid,))
profile = cur.fetchone()

if not profile:
    print(f"OK_PROFILE_CREATE_START")
    try:
        cur.execute(
            "INSERT INTO member_profiles (user_id, organization_id) VALUES (?, ?)",
            (uid, ORG_ID)
        )
        conn.commit()
        print(f"OK_PROFILE_CREATED")
    except Exception as e:
        # member_profiles might not have organization_id column, try without it
        try:
            cur.execute("INSERT INTO member_profiles (user_id) VALUES (?)", (uid,))
            conn.commit()
            print(f"OK_PROFILE_CREATED_NO_ORG")
        except Exception as e2:
            print(f"ERROR_PROFILE: {e2}")
else:
    print(f"OK_PROFILE_EXISTS")

# Verify final state
cur.execute("SELECT id, email, role, status, organization_id FROM users WHERE email = ?", (EMAIL,))
final = cur.fetchone()
if final:
    print(f"OK_FINAL_ID={final['id']}")
    print(f"OK_FINAL_EMAIL={final['email']}")
    print(f"OK_FINAL_ROLE={final['role']}")
    print(f"OK_FINAL_STATUS={final['status']}")
    print(f"OK_FINAL_ORG={final['organization_id']}")
else:
    print(f"ERROR_NOT_FOUND")
    
conn.close()
print(f"OK_DONE")
