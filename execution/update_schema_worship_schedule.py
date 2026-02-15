"""
Schema update for music scheduling.
Creates service_plans, service_setlist, and roster_entries tables.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

def update_schema():
    """Add music scheduling tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Service plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                event_id INTEGER,
                notes TEXT,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # Service setlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_setlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                order_index INTEGER NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES service_plans(id),
                FOREIGN KEY (song_id) REFERENCES songs(id)
            )
        """)
        
        # Roster entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roster_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                musician_id INTEGER NOT NULL,
                instrument TEXT NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'declined')),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES service_plans(id),
                FOREIGN KEY (musician_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        print("[OK] Service plans table created")
        print("[OK] Service setlist table created")
        print("[OK] Roster entries table created")

if __name__ == "__main__":
    update_schema()
    print("Schema update complete: music scheduling")
