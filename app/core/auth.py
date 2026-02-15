from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return {"_error": "No token provided", "sub": None}
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return {"_error": "Invalid token", "sub": None}
        return {"sub": user_id, **payload}
    except JWTError:
        return {"_error": "Could not validate credentials", "sub": None}

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("_error"):
        return current_user
    # Aqui você pode adicionar verificação se usuário está ativo
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("_error"):
        return current_user
    # Verificar se é admin (você pode ajustar conforme sua lógica)
    is_admin = current_user.get("is_admin", False)
    if not is_admin:
        return {"_error": "Not enough permissions", "sub": current_user.get("sub")}
    return current_user

def get_optional_user(token: str = Depends(oauth2_scheme)):
    """Get user if token exists, otherwise return None"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"sub": payload.get("sub"), **payload}
    except JWTError:
        return None