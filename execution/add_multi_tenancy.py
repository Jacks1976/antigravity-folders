#!/usr/bin/env python3
"""
Add multi-tenancy support to existing database
Adds organization_id to all relevant tables
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'church_app.db')

def add_multi_tenancy_support():
    print(f"Adding multi-tenancy support to {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    try:
        # 1. Create organizations table
        print("Creating organizations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                country TEXT DEFAULT 'Brazil',
                website TEXT,
                logo_url TEXT,
                description TEXT,
                founded_year INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_slug ON organizations(slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_active ON organizations(is_active)")
        
        # 2. Add organization_id to existing tables (if column doesn't exist)
        print("Adding organization_id to users table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN organization_id INTEGER")
            cursor.execute("ALTER TABLE users ADD FOREIGN KEY (organization_id) REFERENCES organizations(id)")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                print(f"  Note: {e}")
        
        print("Adding organization_id to events table...")
        try:
            cursor.execute("ALTER TABLE events ADD COLUMN organization_id INTEGER")
            cursor.execute("ALTER TABLE events ADD FOREIGN KEY (organization_id) REFERENCES organizations(id)")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                print(f"  Note: {e}")
        
        print("Adding organization_id to announcements table...")
        try:
            cursor.execute("ALTER TABLE announcements ADD COLUMN organization_id INTEGER")
            cursor.execute("ALTER TABLE announcements ADD FOREIGN KEY (organization_id) REFERENCES organizations(id)")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                print(f"  Note: {e}")
        
        print("Adding organization_id to songs table...")
        try:
            cursor.execute("ALTER TABLE songs ADD COLUMN organization_id INTEGER")
            cursor.execute("ALTER TABLE songs ADD FOREIGN KEY (organization_id) REFERENCES organizations(id)")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                print(f"  Note: {e}")
        
        print("Adding organization_id to member_profiles table...")
        try:
            cursor.execute("ALTER TABLE member_profiles ADD COLUMN organization_id INTEGER")
            cursor.execute("ALTER TABLE member_profiles ADD FOREIGN KEY (organization_id) REFERENCES organizations(id)")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                print(f"  Note: {e}")
        
        # 3. Create default organization (PIBG)
        print("Creating default organization (PIBG Greenville)...")
        cursor.execute("""
            INSERT OR IGNORE INTO organizations 
            (id, name, slug, email, phone, city, country, description, is_active)
            VALUES (1, 'PIBG - Primeira Igreja Brasileira de Greenville', 'pibg-greenville', 
                   'contato@pibg.church', '+1-864-555-0123', 'Greenville', 'USA',
                   'Primeira Igreja Brasileira de Greenville', 1)
        """)
        
        # 4. Update all existing users/events/announcements to belong to organization 1
        print("Updating existing records to organization 1...")
        cursor.execute("UPDATE users SET organization_id = 1 WHERE organization_id IS NULL")
        cursor.execute("UPDATE events SET organization_id = 1 WHERE organization_id IS NULL")
        cursor.execute("UPDATE announcements SET organization_id = 1 WHERE organization_id IS NULL")
        cursor.execute("UPDATE songs SET organization_id = 1 WHERE organization_id IS NULL")
        cursor.execute("UPDATE member_profiles SET organization_id = 1 WHERE organization_id IS NULL")
        
        # 5. Create indexes for performance
        print("Creating performance indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_org ON users(organization_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_org ON events(organization_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcements_org ON announcements(organization_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_org ON songs(organization_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_org ON member_profiles(organization_id)")
        
        conn.commit()
        print("✓ Multi-tenancy support added successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_multi_tenancy_support()
