from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Contact(BaseModel):
    """Modelo para contatos"""
    name: str = Field(..., min_length=1, description="Nome do contato")
    phone: str = Field(..., min_length=1, description="Número de telefone do contato")
    group: Optional[str] = Field(None, description="Grupo do contato")

    @validator('phone')
    def validate_phone(cls, v):
        """Valida o número de telefone"""
        if not v:
            raise ValueError("O número de telefone é obrigatório")
        # Remove caracteres não numéricos
        v = ''.join(filter(str.isdigit, v))
        if not v:
            raise ValueError("O número de telefone deve conter pelo menos um dígito")
        return v

    @validator('name')
    def validate_name(cls, v):
        """Valida o nome do contato"""
        if not v or not v.strip():
            raise ValueError("O nome do contato é obrigatório")
        return v.strip()

class ClientBase(BaseModel):
    """Modelo base para clientes"""
    name: str = Field(..., min_length=1, description="Nome do cliente")
    description: Optional[str] = Field(None, description="Descrição do cliente")
    daily_limit: int = Field(..., gt=0, description="Limite diário de mensagens")
    active: bool = Field(default=True, description="Status do cliente")
    contacts: List[Contact] = Field(default_factory=list, description="Lista de contatos do cliente")

    @validator('name')
    def validate_name(cls, v):
        """Valida o nome do cliente"""
        if not v or not v.strip():
            raise ValueError("O nome do cliente é obrigatório")
        return v.strip()

class ClientCreate(ClientBase):
    """Modelo para criação de clientes"""
    pass

class ClientUpdate(BaseModel):
    """Modelo para atualização de clientes"""
    name: Optional[str] = None
    description: Optional[str] = None
    daily_limit: Optional[int] = None
    active: Optional[bool] = None
    contacts: Optional[List[Contact]] = None

class Client(ClientBase):
    """Modelo para retorno de clientes"""
    id: str = Field(..., description="ID do cliente")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
