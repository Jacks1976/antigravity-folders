"""
Core configuration and utilities for the API.
"""
import os
import sys

# Add execution directory to Python path for importing existing modules
EXECUTION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'execution')
sys.path.insert(0, EXECUTION_DIR)

# JWT Configuration (reuse from execution/auth/utils.py)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
ALGORITHM = 'HS256'
