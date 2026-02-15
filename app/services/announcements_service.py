"""
Announcements service - uses core business logic from execution/announcements/core.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'execution'))

from announcements.core import post_announcement_core, get_feed_core

# Re-export core functions
post_announcement = post_announcement_core
get_feed = get_feed_core
