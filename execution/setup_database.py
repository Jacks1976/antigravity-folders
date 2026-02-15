import sqlite3
from db import get_db_connection, init_db_file

def create_tables():
    init_db_file()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Enable Foreign Keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Users Table (Core Auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'Pending',
                status TEXT DEFAULT 'Pending',
                language_pref TEXT DEFAULT 'pt-BR',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                CHECK (status IN ('Pending', 'Active', 'Banned'))
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);")
        
        # 2. Member Profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                phone TEXT,
                address TEXT,
                dob DATE,
                baptism_date DATE,
                bio TEXT,
                ministry_history TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        # 3. Ministries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ministries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP
            );
        """)
        
        # 4. Ministry Assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ministry_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ministry_id INTEGER NOT NULL,
                role TEXT,
                is_lead BOOLEAN DEFAULT 0,
                assigned_by INTEGER,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (ministry_id) REFERENCES ministries(id)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_user ON ministry_assignments(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_ministry ON ministry_assignments(ministry_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_lead ON ministry_assignments(is_lead);")
        
        # 5. Audit Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actor_id INTEGER,
                action_type TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                metadata TEXT, -- JSON blob
                ip_address TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_actor_time ON audit_logs(actor_id, timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);")
        
        # 6. Notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);")

        # 8. Password Resets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_password_resets_user ON password_resets(user_id);")

        # 7. Domain Events (Simple Bus)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS domain_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL, -- UUID
                event_type TEXT NOT NULL,
                payload TEXT,
                status TEXT DEFAULT 'PENDING',
                processed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON domain_events(status);")

        conn.commit()
        print("Database initialized successfully.")

if __name__ == '__main__':
    create_tables()
