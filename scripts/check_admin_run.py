import sqlite3, os, json, sys

# absolute DB path
DB = r"C:\Users\dieke\Documents\Antigravity folders\execution\church_app.db"
OUT = r"C:\Users\dieke\Documents\Antigravity folders\scripts\check_admin.out"

report = {"db_path": DB, "exists": os.path.exists(DB)}

if not os.path.exists(DB):
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print('DB MISSING')
    sys.exit(1)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id,email,role,status,organization_id FROM users WHERE email=?", ('admin@dev.localhost.com',))
r = cur.fetchone()
report['admin'] = dict(r) if r else None
conn.close()

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print('WROTE', OUT)
