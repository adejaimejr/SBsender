from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
from bson import ObjectId

from .models import Client, ClientCreate, ClientUpdate
from .database import Database
from .auth import verify_token, verify_admin

app = FastAPI(title="Client Service", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/clients", response_model=Client)
async def create_client(client: ClientCreate, user = Depends(verify_admin)):
    """Cria um novo cliente (requer admin)"""
    clients_collection = await Database.get_clients_collection()
    
    # Verifica se já existe cliente com mesmo email
    existing_client = await clients_collection.find_one({"email": client.email})
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Prepara o documento para inserção
    client_dict = client.dict()
    client_dict["created_at"] = datetime.utcnow()
    client_dict["updated_at"] = datetime.utcnow()
    
    # Insere o cliente
    result = await clients_collection.insert_one(client_dict)
    client_dict["id"] = str(result.inserted_id)
    
    return Client(**client_dict)

@app.get("/clients", response_model=List[Client])
async def read_clients(user = Depends(verify_token)):
    """Lista todos os clientes (requer autenticação)"""
    clients_collection = await Database.get_clients_collection()
    clients = []
    async for client in clients_collection.find():
        client["id"] = str(client["_id"])
        clients.append(client)
    return clients

@app.get("/clients/{client_id}", response_model=Client)
async def read_client(client_id: str, user = Depends(verify_token)):
    """Obtém um cliente específico (requer autenticação)"""
    clients_collection = await Database.get_clients_collection()
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    client["id"] = str(client["_id"])
    return Client(**client)

@app.put("/clients/{client_id}", response_model=Client)
async def update_client(
    client_id: str,
    client_update: ClientUpdate,
    user = Depends(verify_admin)
):
    """Atualiza um cliente (requer admin)"""
    clients_collection = await Database.get_clients_collection()
    
    # Prepara os dados para atualização
    update_data = client_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Verifica se o email já existe (se estiver sendo atualizado)
    if "email" in update_data:
        existing_client = await clients_collection.find_one({
            "email": update_data["email"],
            "_id": {"$ne": ObjectId(client_id)}
        })
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    # Atualiza o cliente
    result = await clients_collection.update_one(
        {"_id": ObjectId(client_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Retorna o cliente atualizado
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    client["id"] = str(client["_id"])
    return Client(**client)

@app.delete("/clients/{client_id}")
async def delete_client(client_id: str, user = Depends(verify_admin)):
    """Deleta um cliente (requer admin)"""
    clients_collection = await Database.get_clients_collection()
    result = await clients_collection.delete_one({"_id": ObjectId(client_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return {"message": "Cliente deletado com sucesso"}
