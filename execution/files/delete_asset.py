"""
Delete a file asset.
Usage: python delete_asset.py <asset_id>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from files.core import delete_asset_core
from auth.utils import get_user_by_email

def main():
    if len(sys.argv) != 2:
        print("Usage: python delete_asset.py <asset_id>")
        sys.exit(1)
    
    asset_id = int(sys.argv[1])
    
    # Get deleter
    email = input("Your email: ")
    password = input("Password: ")
    
    user = get_user_by_email(email)
    if not user:
        print("Error: User not found")
        sys.exit(1)
    
    # Delete
    result = delete_asset_core(user['id'], asset_id)
    
    if result['ok']:
        print(f"Success: {result['data']['message']}")
    else:
        print(f"Error: {result['error_key']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
