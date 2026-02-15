"""
Schema update for worship files/assets infrastructure.
Creates assets table for file storage tracking.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

def update_schema():
    """Add assets table for file storage."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL UNIQUE,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                checksum TEXT,
                uploaded_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        print("[OK] Assets table created")

if __name__ == "__main__":
    update_schema()
    print("Schema update complete: worship files")
