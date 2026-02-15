"""
Schema update for music repertoire.
Creates songs, instrument_tags, and song_assets tables.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

def update_schema():
    """Add music repertoire tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Songs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                bpm INTEGER,
                default_key TEXT,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # Instrument tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instrument_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Song assets table (links or file references)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS song_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('LINK', 'FILE')),
                url TEXT,
                asset_id INTEGER,
                label TEXT,
                instrument_tag_ids TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (song_id) REFERENCES songs(id),
                FOREIGN KEY (asset_id) REFERENCES assets(id)
            )
        """)
        
        conn.commit()
        print("[OK] Songs table created")
        print("[OK] Instrument tags table created")
        print("[OK] Song assets table created")

if __name__ == "__main__":
    update_schema()
    print("Schema update complete: music repertoire")
