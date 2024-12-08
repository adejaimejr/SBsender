from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    MESSAGE_SENT = "message_sent"
    MESSAGE_FAILED = "message_failed"
    WEBHOOK_SENT = "webhook_sent"
    WEBHOOK_FAILED = "webhook_failed"
    CLIENT_CREATED = "client_created"
    CLIENT_UPDATED = "client_updated"
    CLIENT_DELETED = "client_deleted"

class HistoryBase(BaseModel):
    event_type: EventType
    client_id: Optional[str] = None
    message_id: Optional[str] = None
    webhook_id: Optional[str] = None
    details: Dict[str, Any]

class HistoryCreate(HistoryBase):
    pass

class History(HistoryBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
