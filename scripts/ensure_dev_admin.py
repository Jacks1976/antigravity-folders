import sqlite3
import os
import sys

# Ensure repo root is in path
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from execution.db import get_db_connection

DB = os.path.normpath(os.path.join(ROOT, 'execution', 'church_app.db'))
print('DB path:', DB)
if not os.path.exists(DB):
    print('DB not found at expected path. Aborting.')
    sys.exit(1)

# Look for provided email
email = 'admin@dev.localhost.com'
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, status FROM users WHERE email = ?", (email,))
    r = cursor.fetchone()
    if r:
        print('FOUND', dict(r))
    else:
        print('NOT FOUND')
        # Create user and promote to admin via core function
        from execution.auth.core import register_user_core
        pw = 'DevAdmin123!'
        res = register_user_core(email, pw, 'Dev Admin')
        print('register result:', res)
        if res.get('ok'):
            uid = res['data']['user_id']
            cursor.execute("UPDATE users SET role = 'Admin', status = 'Active' WHERE id = ?", (uid,))
            conn.commit()
            print('Created and promoted admin', email)
        else:
            print('Failed to create admin:', res.get('error_key'))
