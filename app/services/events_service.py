"""
Events service - uses core business logic from execution/events/core.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'execution'))

from events.core import create_event_core, list_events_core, rsvp_event_core

# Re-export core functions
create_event = create_event_core
list_events = list_events_core
rsvp_event = rsvp_event_core
