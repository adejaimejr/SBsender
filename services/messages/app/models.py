from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"

class MessageType(str, Enum):
    TEXT = "text"
    HTML = "html"
    TEMPLATE = "template"

class MessageBase(BaseModel):
    type: MessageType
    content: str
    client_ids: List[str]
    template_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    user_id: str
    status: MessageStatus
    error_message: Optional[str] = None
    sent_count: int = 0
    failed_count: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
