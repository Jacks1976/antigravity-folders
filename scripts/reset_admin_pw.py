import os
import sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from execution.db import get_db_connection
from execution.auth.utils import hash_password

email = 'admin@dev.localhost.com'
password = 'DevAdmin123!'

DB = os.path.join(ROOT, 'execution', 'church_app.db')
print('DB:', DB, 'exists?', os.path.exists(DB))

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, role, status FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user:
        print('User exists:', dict(user))
        ph = hash_password(password)
        cursor.execute('UPDATE users SET password_hash = ?, role = ?, status = ? WHERE email = ?', (ph, 'Admin', 'Active', email))
        conn.commit()
        print('Password updated and promoted to Admin')
    else:
        print('User not found. Creating...')
        from execution.auth.core import register_user_core
        res = register_user_core(email, password, 'Dev Admin')
        print('register result:', res)
        if res.get('ok'):
            uid = res['data']['user_id']
            cursor.execute("UPDATE users SET role = 'Admin', status = 'Active' WHERE id = ?", (uid,))
            conn.commit()
            print('Created and promoted admin:', email)
        else:
            print('Failed to create admin:', res.get('error_key'))

    # Print current row
    cursor.execute('SELECT id, email, role, status FROM users WHERE email = ?', (email,))
    print('Final row:', cursor.fetchone())
