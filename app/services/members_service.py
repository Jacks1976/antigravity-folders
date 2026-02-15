"""
Members service - uses core business logic from execution/members/core.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'execution'))

from members.core import get_directory_core, update_profile_core, assign_ministry_core

# Re-export core functions
get_directory = get_directory_core
update_profile = update_profile_core
assign_ministry = assign_ministry_core
