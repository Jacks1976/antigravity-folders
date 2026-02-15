import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'church_app.db')

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db_file():
    if not os.path.exists(DB_PATH):
        print(f"Creating database file at {DB_PATH}")
        with open(DB_PATH, 'w'): pass
