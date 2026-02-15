import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'church_app.db')

def update_schema_events():
    print(f"Updating schema at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. Create events table
    # We use IF NOT EXISTS, but we also want to ensure constraints/indexes.
    # Since sqlite ALTER TABLE is limited, if table exists we assume it's legacy or we might need to check columns.
    # Given this is "Phase 1.7", assume table doesn't exist yet or is empty dev table. 
    # But user said "do NOT recreate the DB if any data exists".
    
    print("Creating events table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_at TIMESTAMP NOT NULL,
            end_at TIMESTAMP NOT NULL,
            location TEXT,
            is_public BOOLEAN DEFAULT 0,
            rsvp_required BOOLEAN DEFAULT 0,
            target_ministry_ids TEXT DEFAULT '[]', -- JSON Array
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id),
            CONSTRAINT check_event_dates CHECK (end_at > start_at)
        )
    """)

    # Indexes for events
    print("Creating indexes for events...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_public_start ON events(is_public, start_at)")

    # 2. Create event_rsvps table
    print("Creating event_rsvps table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_rsvps (
            event_id INTEGER,
            user_id INTEGER,
            status TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT check_rsvp_status CHECK (status IN ('going', 'maybe', 'not_going'))
        )
    """)

    # Indexes for rsvps
    print("Creating indexes for event_rsvps...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rsvps_user ON event_rsvps(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rsvps_event ON event_rsvps(event_id)")

    conn.commit()
    conn.close()
    print("Schema update for events complete.")

if __name__ == "__main__":
    update_schema_events()
