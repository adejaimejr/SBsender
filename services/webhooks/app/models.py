from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class WebhookStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

class WebhookBase(BaseModel):
    client_id: str
    event_type: str
    payload: Dict[str, Any]

class WebhookCreate(WebhookBase):
    pass

class Webhook(WebhookBase):
    id: str
    status: WebhookStatus
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
