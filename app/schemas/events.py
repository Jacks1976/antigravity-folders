from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class EventBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    reminder_times: List[int] = [60, 1440]  # minutos antes: 1h e 24h
    send_push: bool = True
    send_email: bool = False
    send_sms: bool = False
    recurring: Optional[str] = None  # 'daily', 'weekly', 'monthly'
    max_capacity: Optional[int] = None
    image_url: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventInDB(EventBase):
    id: int
    created_by: int
    created_at: datetime
    rsvp_count: int = 0
    confirmed_count: int = 0