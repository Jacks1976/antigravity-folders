import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'church_app.db')

def update_schema():
    print(f"Updating schema at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(member_profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'profile_pic_url' not in columns:
        print("Adding profile_pic_url column...")
        cursor.execute("ALTER TABLE member_profiles ADD COLUMN profile_pic_url TEXT")
    else:
        print("profile_pic_url already exists.")
        
    if 'share_phone' not in columns:
        print("Adding share_phone column...")
        cursor.execute("ALTER TABLE member_profiles ADD COLUMN share_phone BOOLEAN DEFAULT 0")
    else:
        print("share_phone already exists.")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
