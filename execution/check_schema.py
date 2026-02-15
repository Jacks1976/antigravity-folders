import sqlite3
import os

# DB is in the parent directory of this script (execution folder)
DB_PATH = os.path.join(os.path.dirname(os.getcwd()), 'church_app.db')
# actually let's just use relative path ..
DB_PATH = '../church_app.db'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"DB does not exist at {os.path.abspath(DB_PATH)}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['users', 'member_profiles', 'ministry_assignments', 'audit_logs']
    
    for table in tables:
        print(f"--- {table} ---")
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        res = cursor.fetchone()
        if res:
            print(res[0])
        else:
            print("Not Found")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
