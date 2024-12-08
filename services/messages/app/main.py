from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
from bson import ObjectId

from .models import Message, MessageCreate, MessageStatus
from .database import Database
from .processor import MessageProcessor
from .auth import verify_token, verify_admin, oauth2_scheme

app = FastAPI(title="Message Service", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "message"}

@app.post("/messages", response_model=Message)
async def create_message(message: MessageCreate, user=Depends(verify_token)):
    """Cria uma nova mensagem para envio"""
    messages_collection = Database.get_messages_collection()
    
    message_dict = message.dict()
    message_dict["status"] = MessageStatus.PENDING
    message_dict["created_at"] = datetime.utcnow()
    message_dict["updated_at"] = datetime.utcnow()
    message_dict["user_id"] = user["id"]
    
    result = messages_collection.insert_one(message_dict)
    message_dict["id"] = str(result.inserted_id)
    
    # Inicia o processamento da mensagem de forma assíncrona
    app.state.event_loop.create_task(
        MessageProcessor.process_message(str(result.inserted_id))
    )
    
    return Message(**message_dict)

@app.get("/messages", response_model=List[Message])
async def list_messages(
    status: MessageStatus = None,
    skip: int = 0,
    limit: int = 100,
    user=Depends(verify_token)
):
    """Lista mensagens com filtros opcionais"""
    messages_collection = Database.get_messages_collection()
    
    query = {}
    if status:
        query["status"] = status
    
    # Se não for admin, filtra apenas mensagens do usuário
    if not user.get("is_admin"):
        query["user_id"] = user["id"]
    
    messages = messages_collection.find(query).skip(skip).limit(limit)
    result = []
    
    for msg in messages:
        msg["id"] = str(msg["_id"])
        result.append(Message(**msg))
    
    return result

@app.get("/messages/{message_id}", response_model=Message)
async def get_message(message_id: str, user=Depends(verify_token)):
    """Obtém detalhes de uma mensagem específica"""
    messages_collection = Database.get_messages_collection()
    message = messages_collection.find_one({"_id": ObjectId(message_id)})
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    # Verifica se o usuário tem acesso à mensagem
    if not user.get("is_admin") and message.get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    message["id"] = str(message["_id"])
    return Message(**message)

@app.post("/messages/{message_id}/retry", response_model=Message)
async def retry_message(message_id: str, user=Depends(verify_admin)):
    """Força uma nova tentativa de envio da mensagem"""
    messages_collection = Database.get_messages_collection()
    message = messages_collection.find_one({"_id": ObjectId(message_id)})
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    if message["status"] not in [MessageStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail="Apenas mensagens com falha podem ser reenviadas"
        )
    
    # Atualiza status para pending
    messages_collection.update_one(
        {"_id": ObjectId(message_id)},
        {
            "$set": {
                "status": MessageStatus.PENDING,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Inicia o processamento da mensagem de forma assíncrona
    app.state.event_loop.create_task(
        MessageProcessor.process_message(message_id)
    )
    
    message["status"] = MessageStatus.PENDING
    message["id"] = str(message["_id"])
    return Message(**message)

@app.get("/count")
async def count_messages(token: str = Depends(oauth2_scheme)):
    """Retorna o número total de mensagens"""
    try:
        messages_collection = await Database.get_messages_collection()
        count = await messages_collection.count_documents({})
        return {"count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
