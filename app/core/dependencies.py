from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user, get_current_active_user
from typing import Optional, Dict

# Funções existentes
async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """Dependency for admin-only routes"""
    if current_user.get("_error"):
        return current_user
    # Verificar se é admin (ajuste conforme sua lógica)
    is_admin = current_user.get("is_admin", False)
    if not is_admin:
        return {"_error": "Not enough permissions", "sub": current_user.get("sub")}
    return current_user

async def get_optional_user(current_user: dict = Depends(get_current_user)):
    """Dependency that returns user if authenticated, None otherwise"""
    if current_user and not current_user.get("_error"):
        return current_user
    return None

def get_org_context(org_id: Optional[int] = None):
    """Get organization context from request"""
    # Implementar lógica de organização multi-tenancy
    return org_id

# NOVAS FUNÇÕES NECESSÁRIAS
async def require_active_user(current_user: dict = Depends(get_current_user)):
    """Require an active authenticated user"""
    if current_user.get("_error"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=current_user.get("_error"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

async def require_admin_user(current_user: dict = Depends(require_active_user)):
    """Require an admin user"""
    is_admin = current_user.get("is_admin", False)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def require_organization_access(org_id: Optional[int] = None):
    """Require access to specific organization"""
    def dependency(current_user: dict = Depends(require_active_user)):
        # Implementar lógica de verificação de acesso à organização
        if org_id and current_user.get("organization_id") != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this organization denied"
            )
        return current_user
    return dependency