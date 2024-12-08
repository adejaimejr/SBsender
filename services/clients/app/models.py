from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    webhook_url: HttpUrl
    active: bool = True
    description: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    webhook_url: Optional[HttpUrl] = None
    active: Optional[bool] = None
    description: Optional[str] = None

class Client(ClientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
