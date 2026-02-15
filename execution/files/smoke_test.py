"""
Smoke test for worship files/assets module.
Tests upload, download, and delete operations.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from files.core import upload_asset_core, delete_asset_core, get_asset_path_core
from db import get_db_connection

def test_files():
    """Test file operations."""
    print("=== Worship Files Smoke Test ===\n")
    
    # Get test user (admin)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE role = 'Admin' LIMIT 1")
        admin = cursor.fetchone()
        
        if not admin:
            print("[FAIL] No admin user found")
            return False
        
        admin_id = admin['id']
    
    # Test 1: Upload MP3
    print("Test 1: Upload MP3 file")
    test_content = b"fake mp3 content for testing"
    result = upload_asset_core(admin_id, "test_song.mp3", test_content, "audio/mpeg")
    
    if not result['ok']:
        print(f"[FAIL] Upload failed: {result['error_key']}")
        return False
    
    asset_id = result['data']['asset_id']
    print(f"[PASS] Uploaded asset ID: {asset_id}\n")
    
    # Test 2: Get asset path
    print("Test 2: Get asset path")
    result = get_asset_path_core(admin_id, asset_id)
    
    if not result['ok']:
        print(f"[FAIL] Get path failed: {result['error_key']}")
        return False
    
    print(f"[PASS] Got path: {result['data']['storage_path']}\n")
    
    # Test 3: Delete asset
    print("Test 3: Delete asset")
    result = delete_asset_core(admin_id, asset_id)
    
    if not result['ok']:
        print(f"[FAIL] Delete failed: {result['error_key']}")
        return False
    
    print(f"[PASS] Deleted asset\n")
    
    # Test 4: Try to get deleted asset (should fail)
    print("Test 4: Get deleted asset (should fail)")
    result = get_asset_path_core(admin_id, asset_id)
    
    if result['ok']:
        print("[FAIL] Should not be able to get deleted asset")
        return False
    
    print(f"[PASS] Correctly blocked: {result['error_key']}\n")
    
    print("=== All Tests PASSED ===")
    return True

if __name__ == "__main__":
    success = test_files()
    sys.exit(0 if success else 1)
