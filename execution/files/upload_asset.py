"""
Upload a file asset (MP3 or PDF).
Usage: python upload_asset.py <filename> <file_path>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from files.core import upload_asset_core
from auth.utils import get_user_by_email
from db import get_db_connection

def main():
    if len(sys.argv) != 3:
        print("Usage: python upload_asset.py <filename> <file_path>")
        sys.exit(1)
    
    filename = sys.argv[1]
    file_path = sys.argv[2]
    
    # Get uploader (for CLI, use admin)
    email = input("Your email: ")
    password = input("Password: ")
    
    user = get_user_by_email(email)
    if not user:
        print("Error: User not found")
        sys.exit(1)
    
    # Read file
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Determine MIME type from extension
    ext = os.path.splitext(filename)[1].lower()
    mime_map = {
        '.mp3': 'audio/mpeg',
        '.pdf': 'application/pdf'
    }
    mime_type = mime_map.get(ext)
    
    if not mime_type:
        print(f"Error: Unsupported file type {ext}")
        sys.exit(1)
    
    # Upload
    result = upload_asset_core(user['id'], filename, file_content, mime_type)
    
    if result['ok']:
        print(f"Success: Asset uploaded with ID {result['data']['asset_id']}")
    else:
        print(f"Error: {result['error_key']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
