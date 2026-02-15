import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'church_app.db')

def update_schema_announcements():
    print(f"Updating schema at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create announcements table
    print("Creating announcements table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT,
            target_type TEXT CHECK(target_type IN ('Global', 'Role', 'Ministry')),
            target_id TEXT, -- Null if Global, Role Name, or Ministry ID
            is_pinned BOOLEAN DEFAULT 0,
            expires_at TIMESTAMP,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Indexes
    print("Creating indexes for announcements...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_expiry ON announcements(expires_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_target ON announcements(target_type, target_id)")

    conn.commit()
    conn.close()
    print("Schema update for announcements complete.")

if __name__ == "__main__":
    update_schema_announcements()
