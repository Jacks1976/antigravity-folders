"""
Authentication dependency for FastAPI endpoints.
All exceptions return HTTP 200 with error envelope for MVP simplicity.
"""
from fastapi import Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import sys
import os

# Add execution directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'execution'))

from auth.utils import decode_access_token
from db import get_db_connection
from fastapi import Query

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), response: Response = None) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    Returns payload with 'sub' (user_id), 'role', etc.
    Returns error envelope on failure (HTTP 200).
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        # Return error envelope instead of raising exception
        if response:
            response.status_code = 200
        return {"_error": True, "ok": False, "data": None, "error_key": "auth.unauthorized"}
    
    return payload

def get_current_active_user(current_user: dict = Depends(get_current_user), response: Response = None) -> dict:
    """
    Dependency to ensure user has status='Active'.
    Returns error envelope if not active (HTTP 200).
    """
    # Check if previous dependency returned error
    if current_user.get("_error"):
        return current_user
    
    user_id = current_user['sub']
    
    # Verify status from DB
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row or row['status'] != 'Active':
            if response:
                response.status_code = 200
            return {"_error": True, "ok": False, "data": None, "error_key": "auth.account_pending"}
    
    return current_user

def get_current_admin_user(current_user: dict = Depends(get_current_active_user), response: Response = None) -> dict:
    """
    Dependency to ensure user is Admin/Staff.
    Returns error envelope if not admin (HTTP 200).
    """
    # Check if previous dependency returned error
    if current_user.get("_error"):
        return current_user
    
    if current_user['role'] not in ('Admin', 'Staff'):
        if response:
            response.status_code = 200
        return {"_error": True, "ok": False, "data": None, "error_key": "auth.forbidden"}
    
    return current_user

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """
    Optional authentication - returns None if no token provided.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload
# Backward-compatible alias for worship routers
require_active_user = get_current_active_user


def get_org_context(organization: str | None = Query(None, alias='organization'), current_user: Optional[dict] = Depends(get_optional_user)) -> int | None:
    """
    Resolve the current organization id from multiple sources in order of precedence:
    1. Authenticated user's token payload (`org` claim)
    2. Authenticated user's `organization_id` from DB
    3. Public `organization` query parameter (slug -> id)

    Returns organization id or None if not resolvable.
    """
    # 1/2: Try current user
    if current_user and not current_user.get('_error'):
        org_claim = current_user.get('org')
        if org_claim:
            return org_claim

        # fallback to DB lookup
        user_id = current_user.get('sub')
        if user_id:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT organization_id FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                if row and row.get('organization_id'):
                    return row['organization_id']

    # 3: Try query param slug
    if organization:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM organizations WHERE slug = ?", (organization,))
            r = cursor.fetchone()
            if r:
                return r['id']

    return None
