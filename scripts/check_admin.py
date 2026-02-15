import sqlite3
import os
import json

# locate DB relative to repo
db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'execution', 'church_app.db'))
print('DB_PATH:', db)
print('EXISTS:', os.path.exists(db))

if not os.path.exists(db):
    raise SystemExit(1)

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id,email,role,status,organization_id FROM users WHERE email=?", ('admin@dev.localhost.com',))
r = cur.fetchone()
if r:
    print(json.dumps(dict(r), ensure_ascii=False))
else:
    print('NOT FOUND')
conn.close()
