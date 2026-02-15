import os
import jwt
import datetime
import json
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db import get_db_connection

# Load Secret Key (In prod, use env var)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours for MVP
RESET_TOKEN_EXPIRE_MINUTES = 30

ph = PasswordHasher()

# Error Messages (i18n Keys)
ERR_INVALID_CREDENTIALS = "auth.invalid_credentials"
ERR_ACCOUNT_PENDING = "auth.account_pending"
ERR_ACCOUNT_BANNED = "auth.account_banned"
ERR_TOO_MANY_ATTEMPTS = "auth.too_many_attempts"
ERR_RESET_SENT = "auth.reset_sent"
ERR_RESET_INVALID = "auth.reset_invalid_or_expired"
ERR_INVALID_EMAIL = "auth.invalid_email_format"
ERR_PASSWORD_WEAK = "auth.password_too_weak" 

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hash: str, password: str) -> bool:
    try:
        return ph.verify(hash, password)
    except VerifyMismatchError:
        return False

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_password_strength(password: str) -> bool:
    """
    Min 12 chars, mixed case, number, symbol.
    """
    if len(password) < 12:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def check_rate_limit(ip_address: str, email: str = None) -> bool:
    """
    Check if IP or Account has exceeded login failures.
    Limit: 5 failures in 15 minutes.
    """
    limit_window = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check IP Limit
        cursor.execute("""
            SELECT count(*) FROM audit_logs 
            WHERE action_type = 'AUTH_LOGIN_FAIL' 
            AND ip_address = ? 
            AND timestamp > ?
        """, (ip_address, limit_window))
        ip_count = cursor.fetchone()[0]
        
        if ip_count >= 5:
            return False

        # Check Account Limit (if email provided)
        if email:
            cursor.execute("""
                SELECT count(*) FROM audit_logs 
                WHERE action_type = 'AUTH_LOGIN_FAIL' 
                AND metadata LIKE ? 
                AND timestamp > ?
            """, (f'%{email}%', limit_window))
            account_count = cursor.fetchone()[0]
            if account_count >= 5:
                return False
                
    return True
