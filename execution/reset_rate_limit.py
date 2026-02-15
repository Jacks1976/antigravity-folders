import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'church_app.db')

def reset_limits():
    print(f"Clearing login failures from {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB Not Found")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM audit_logs WHERE action_type = 'AUTH_LOGIN_FAIL'")
        conn.commit()
        print(f"Deleted {cursor.rowcount} rows.")
    except Exception as e:
        print(e)
    conn.close()
    print("Rate limits reset.")

if __name__ == "__main__":
    reset_limits()
