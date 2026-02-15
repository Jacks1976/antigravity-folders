"""
Dev-only admin seeding utility.
Creates a default admin user if DEV_MODE=true and admin doesn't exist.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from auth.core import register_user_core

def seed_dev_admin():
    """Seed a dev admin user if DEV_MODE is enabled."""
    dev_mode = os.environ.get('DEV_MODE', 'false').lower() == 'true'
    
    if not dev_mode:
        return
    
    dev_admin_email = os.environ.get('DEV_ADMIN_EMAIL', 'admin@dev.local')
    dev_admin_password = os.environ.get('DEV_ADMIN_PASSWORD', 'DevAdmin123!')
    
    # Check if admin already exists
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (dev_admin_email,))
        if cursor.fetchone():
            print(f"[DEV] Admin {dev_admin_email} already exists")
            return
    
    # Create admin
    result = register_user_core(dev_admin_email, dev_admin_password, "Dev Admin")
    
    if result['ok']:
        user_id = result['data']['user_id']
        
        # Promote to Admin/Active
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = 'Admin', status = 'Active' WHERE id = ?", (user_id,))
            conn.commit()
        
        print(f"[DEV] Created admin user: {dev_admin_email}")
    else:
        print(f"[DEV] Failed to create admin: {result.get('error_key')}")

if __name__ == "__main__":
    seed_dev_admin()
