from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserProfile(str, Enum):
    ADMIN = "admin"
    CLIENTE = "cliente"
    OPERADOR = "operador"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    is_admin: bool = False

class UserBase(BaseModel):
    username: str
    email: EmailStr
    profile: UserProfile = UserProfile.CLIENTE
    is_active: bool = False
    is_admin: bool = False
    avatar_emoji: str = "👤"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile: Optional[UserProfile] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    avatar_emoji: Optional[str] = None

class User(UserBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
