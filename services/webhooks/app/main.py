from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
from bson import ObjectId

from .models import Webhook, WebhookCreate, WebhookStatus
from .database import Database
from .sender import WebhookSender

app = FastAPI(title="Webhook Service", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webhooks", response_model=Webhook)
async def create_webhook(webhook: WebhookCreate):
    """Cria um novo webhook para envio"""
    webhooks_collection = Database.get_webhooks_collection()
    
    webhook_dict = webhook.dict()
    webhook_dict["status"] = WebhookStatus.PENDING
    webhook_dict["retry_count"] = 0
    webhook_dict["created_at"] = datetime.utcnow()
    webhook_dict["updated_at"] = datetime.utcnow()
    
    result = webhooks_collection.insert_one(webhook_dict)
    webhook_dict["id"] = str(result.inserted_id)
    
    # Inicia o processamento do webhook de forma assíncrona
    app.state.event_loop.create_task(
        WebhookSender.process_webhook(str(result.inserted_id))
    )
    
    return Webhook(**webhook_dict)

@app.get("/webhooks", response_model=List[Webhook])
async def list_webhooks(
    client_id: str = None,
    status: WebhookStatus = None,
    skip: int = 0,
    limit: int = 100
):
    """Lista webhooks com filtros opcionais"""
    webhooks_collection = Database.get_webhooks_collection()
    
    query = {}
    if client_id:
        query["client_id"] = client_id
    if status:
        query["status"] = status
    
    webhooks = list(webhooks_collection.find(query).skip(skip).limit(limit))
    for webhook in webhooks:
        webhook["id"] = str(webhook["_id"])
    
    return webhooks

@app.get("/webhooks/{webhook_id}", response_model=Webhook)
async def get_webhook(webhook_id: str):
    """Obtém detalhes de um webhook específico"""
    webhooks_collection = Database.get_webhooks_collection()
    webhook = webhooks_collection.find_one({"_id": ObjectId(webhook_id)})
    
    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook não encontrado"
        )
    
    webhook["id"] = str(webhook["_id"])
    return Webhook(**webhook)

@app.post("/webhooks/{webhook_id}/retry")
async def retry_webhook(webhook_id: str):
    """Força uma nova tentativa de envio do webhook"""
    webhooks_collection = Database.get_webhooks_collection()
    webhook = webhooks_collection.find_one({"_id": ObjectId(webhook_id)})
    
    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook não encontrado"
        )
    
    if webhook["status"] not in [WebhookStatus.FAILED, WebhookStatus.RETRYING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook não está em estado de falha ou retentativa"
        )
    
    # Atualiza o status e inicia nova tentativa
    webhooks_collection.update_one(
        {"_id": ObjectId(webhook_id)},
        {
            "$set": {
                "status": WebhookStatus.PENDING,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    app.state.event_loop.create_task(
        WebhookSender.process_webhook(webhook_id)
    )
    
    return {"message": "Webhook agendado para reenvio"}
