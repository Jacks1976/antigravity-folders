"""
Smoke test for music repertoire module.
Tests song creation, updates, and asset management.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_repertoire.core import (
    create_song_core, update_song_core, list_songs_core,
    add_song_asset_core, remove_song_asset_core
)
from db import get_db_connection

def test_repertoire():
    """Test repertoire operations."""
    print("=== Music Repertoire Smoke Test ===\n")
    
    # Get test user
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE role = 'Admin' LIMIT 1")
        admin = cursor.fetchone()
        
        if not admin:
            print("[FAIL] No admin user found")
            return False
        
        admin_id = admin['id']
    
    # Test 1: Create song
    print("Test 1: Create song")
    result = create_song_core(admin_id, "Amazing Grace", "John Newton", 90, "G")
    
    if not result['ok']:
        print(f"[FAIL] Create failed: {result['error_key']}")
        return False
    
    song_id = result['data']['song_id']
    print(f"[PASS] Created song ID: {song_id}\n")
    
    # Test 2: Update song
    print("Test 2: Update song")
    result = update_song_core(admin_id, song_id, {"bpm": 95})
    
    if not result['ok']:
        print(f"[FAIL] Update failed: {result['error_key']}")
        return False
    
    print(f"[PASS] Updated song\n")
    
    # Test 3: List songs
    print("Test 3: List songs")
    result = list_songs_core(admin_id, search="Amazing")
    
    if not result['ok'] or len(result['data']['results']) == 0:
        print(f"[FAIL] List failed")
        return False
    
    print(f"[PASS] Found {len(result['data']['results'])} songs\n")
    
    # Test 4: Add link asset
    print("Test 4: Add link asset")
    result = add_song_asset_core(
        admin_id, song_id, "LINK",
        url="https://example.com/sheet.pdf",
        label="Sheet Music"
    )
    
    if not result['ok']:
        print(f"[FAIL] Add asset failed: {result['error_key']}")
        return False
    
    asset_id = result['data']['song_asset_id']
    print(f"[PASS] Added asset ID: {asset_id}\n")
    
    # Test 5: Remove asset
    print("Test 5: Remove asset")
    result = remove_song_asset_core(admin_id, asset_id)
    
    if not result['ok']:
        print(f"[FAIL] Remove asset failed: {result['error_key']}")
        return False
    
    print(f"[PASS] Removed asset\n")
    
    print("=== All Tests PASSED ===")
    return True

if __name__ == "__main__":
    success = test_repertoire()
    sys.exit(0 if success else 1)
