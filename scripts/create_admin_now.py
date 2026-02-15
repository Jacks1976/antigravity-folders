import os
import sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from execution.db import get_db_connection
from execution.auth.core import register_user_core

email = 'admin@dev.localhost.com'
password = 'DevAdmin123!'

DB_PATH = os.path.join(ROOT, 'execution', 'church_app.db')
print('DB:', DB_PATH, 'exists?', os.path.exists(DB_PATH))

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, role, status FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    if row:
        print('FOUND:', dict(row))
    else:
        print('Creating user...')
        res = register_user_core(email, password, 'Dev Admin', organization_slug=None)
        print('register result:', res)
        if res.get('ok'):
            uid = res['data']['user_id']
            cursor.execute("UPDATE users SET role = 'Admin', status = 'Active' WHERE id = ?", (uid,))
            conn.commit()
            print('Created and promoted admin:', email)
        else:
            print('Failed to create admin:', res.get('error_key'))
