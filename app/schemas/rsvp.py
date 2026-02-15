from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RSVPStatus(str, Enum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    DECLINED = "declined"
    MAYBE = "maybe"

class RSVPBase(BaseModel):
    event_id: int
    status: RSVPStatus
    guests_count: int = 1
    notes: Optional[str] = None

class RSVPCreate(RSVPBase):
    pass

class RSVPInDB(RSVPBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True