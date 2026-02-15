from db import get_db_connection

DEFAULT_MINISTRIES = [
    ("Worship Team", "Music and Arts ministry"),
    ("Kids Ministry", "Children's education"),
    ("Ushers", "Welcome and hospitality"),
    ("Media Team", "Audio, Video, and Tech")
]

def seed_data():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Seed Ministries
        print("Seeding Ministries...")
        for name, desc in DEFAULT_MINISTRIES:
            try:
                cursor.execute(
                    "INSERT INTO ministries (name, description) VALUES (?, ?)",
                    (name, desc)
                )
            except Exception as e:
                print(f"Skipping {name}: already exists")
        
        # Seed Admin User (Placeholder - normally created via Auth, but good for bootstrapping)
        # Note: In a real flow, we'd hash the password.
        # This is just ensuring the roles/ministries are ready.
        
        conn.commit()
        print("Seeding complete.")

if __name__ == '__main__':
    seed_data()
