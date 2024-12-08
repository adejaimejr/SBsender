from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from bson import ObjectId
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from .models import History, HistoryCreate, EventType
from .database import Database
from .auth import verify_token, verify_admin

app = FastAPI(title="History Service", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await Database.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await Database.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "history"}

@app.post("/events", response_model=History)
async def create_event(event: HistoryCreate, user=Depends(verify_token)):
    """Registra um novo evento no histórico"""
    history_collection = Database.get_history_collection()
    
    event_dict = event.dict()
    event_dict["created_at"] = datetime.utcnow()
    event_dict["user_id"] = user["id"]
    
    result = await history_collection.insert_one(event_dict)
    event_dict["id"] = str(result.inserted_id)
    
    return History(**event_dict)

@app.get("/events", response_model=List[History])
async def list_events(
    client_id: Optional[str] = None,
    message_id: Optional[str] = None,
    webhook_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    user=Depends(verify_token)
):
    """Lista eventos do histórico com filtros opcionais"""
    history_collection = Database.get_history_collection()
    
    query = {}
    if client_id:
        query["client_id"] = client_id
    if message_id:
        query["message_id"] = message_id
    if webhook_id:
        query["webhook_id"] = webhook_id
    if event_type:
        query["event_type"] = event_type
    
    # Filtro de data
    date_query = {}
    if start_date:
        date_query["$gte"] = start_date
    if end_date:
        date_query["$lte"] = end_date
    if date_query:
        query["created_at"] = date_query
    
    # Se não for admin, filtra apenas eventos do usuário
    if not user.get("is_admin"):
        query["user_id"] = user["id"]
    
    cursor = history_collection.find(query)
    cursor.sort("created_at", -1).skip(skip).limit(limit)
    
    events = []
    async for event in cursor:
        event["id"] = str(event["_id"])
        events.append(History(**event))
    
    return events

@app.get("/events/{event_id}", response_model=History)
async def get_event(event_id: str, user=Depends(verify_token)):
    """Obtém detalhes de um evento específico"""
    history_collection = Database.get_history_collection()
    event = await history_collection.find_one({"_id": ObjectId(event_id)})
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verifica se o usuário tem acesso ao evento
    if not user.get("is_admin") and event.get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    event["id"] = str(event["_id"])
    return History(**event)

@app.get("/clients/{client_id}/summary")
async def get_client_summary(client_id: str, user=Depends(verify_token)):
    """Obtém um resumo dos eventos de um cliente"""
    history_collection = Database.get_history_collection()
    
    # Verifica se o usuário tem acesso ao cliente
    if not user.get("is_admin"):
        # TODO: Verificar permissão no serviço de clientes
        pass
    
    # Últimas 24 horas
    start_date = datetime.utcnow() - timedelta(days=1)
    
    pipeline = [
        {"$match": {
            "client_id": client_id,
            "created_at": {"$gte": start_date}
        }},
        {"$group": {
            "_id": "$event_type",
            "count": {"$sum": 1},
            "last_occurrence": {"$max": "$created_at"}
        }}
    ]
    
    result = await history_collection.aggregate(pipeline).to_list(None)
    
    return {
        "client_id": client_id,
        "period": "last_24h",
        "events": {
            item["_id"]: {
                "count": item["count"],
                "last_occurrence": item["last_occurrence"]
            }
            for item in result
        }
    }

@app.get("/events/export/csv")
async def export_events_csv(
    client_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user=Depends(verify_admin)
):
    """Exporta eventos para CSV"""
    history_collection = Database.get_history_collection()
    
    query = {}
    if client_id:
        query["client_id"] = client_id
    if event_type:
        query["event_type"] = event_type
    
    # Filtro de data
    date_query = {}
    if start_date:
        date_query["$gte"] = start_date
    if end_date:
        date_query["$lte"] = end_date
    if date_query:
        query["created_at"] = date_query
    
    cursor = history_collection.find(query).sort("created_at", -1)
    
    # Cria o CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Tipo de Evento", "Cliente", "Mensagem", "Webhook",
        "Detalhes", "Data de Criação"
    ])
    
    async for event in cursor:
        writer.writerow([
            str(event["_id"]),
            event["event_type"],
            event.get("client_id", ""),
            event.get("message_id", ""),
            event.get("webhook_id", ""),
            str(event.get("details", {})),
            event["created_at"].isoformat()
        ])
    
    # Prepara a resposta
    output.seek(0)
    headers = {
        "Content-Disposition": f'attachment; filename="events_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    }
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers
    )
