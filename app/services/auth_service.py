"""
Auth service - uses core business logic from execution/auth/core.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'execution'))

from auth.core import register_user_core, login_user_core, approve_user_core

# Re-export core functions
register_user = register_user_core
login_user = login_user_core
approve_user = approve_user_core
