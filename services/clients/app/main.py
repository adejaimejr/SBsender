from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
from bson import ObjectId
import logging
from pydantic import ValidationError

from .models import Client, ClientCreate, ClientUpdate
from .database import Database
from .auth import verify_token, verify_admin
from .config import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_title, version=settings.app_version)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicialização
@app.on_event("startup")
async def startup_event():
    """Conecta ao banco de dados na inicialização"""
    logger.info("Iniciando serviço de clientes...")
    try:
        await Database.connect()
        logger.info("Conexão com o banco de dados estabelecida com sucesso")
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Rota raiz para verificar se o serviço está rodando"""
    return {"message": "Client Service is running"}

@app.post("/clients", response_model=Client, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate, user = Depends(verify_token)):
    """Cria um novo cliente"""
    try:
        logger.info(f"Iniciando criação do cliente: {client.name}")
        logger.info(f"Número de contatos recebidos: {len(client.contacts)}")
        
        clients_collection = await Database.get_clients_collection()
        
        # Verifica se já existe cliente com mesmo nome
        existing_client = await clients_collection.find_one({"name": client.name})
        if existing_client:
            logger.warning(f"Cliente com nome '{client.name}' já existe")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este nome"
            )
        
        # Converte o modelo Pydantic para dict
        client_dict = client.dict(by_alias=True)
        
        # Processa os contatos
        contacts = client_dict.get('contacts', [])
        logger.info(f"Processando {len(contacts)} contatos")
        
        # Garante que os contatos estão no formato correto
        processed_contacts = []
        for contact in contacts:
            if isinstance(contact, dict):
                processed_contact = {
                    "name": str(contact['name']).strip(),
                    "phone": str(contact['phone']).strip(),
                }
                if 'group' in contact and contact['group']:
                    processed_contact['group'] = str(contact['group']).strip()
                processed_contacts.append(processed_contact)
        
        # Atualiza os contatos processados
        client_dict['contacts'] = processed_contacts
        logger.info(f"Número de contatos processados: {len(processed_contacts)}")
        
        # Adiciona timestamps e status
        now = datetime.utcnow()
        client_dict.update({
            "created_at": now,
            "updated_at": now,
            "active": True
        })
        
        # Log dos dados antes de inserir
        logger.info(f"Dados a serem inseridos: {client_dict}")
        
        # Insere no MongoDB
        result = await clients_collection.insert_one(client_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao inserir cliente no banco de dados"
            )
        
        logger.info(f"Cliente inserido com sucesso. ID: {result.inserted_id}")
        
        # Recupera o cliente criado
        created_client = await clients_collection.find_one({"_id": result.inserted_id})
        if not created_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao recuperar o cliente criado"
            )
        
        # Converte _id para string
        created_client["id"] = str(created_client.pop("_id"))
        
        logger.info(f"Cliente criado com sucesso: {created_client['name']} (ID: {created_client['id']})")
        logger.info(f"Número de contatos salvos: {len(created_client['contacts'])}")
        
        return created_client
        
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@app.get("/clients", response_model=List[Client])
async def read_clients(user = Depends(verify_token)):
    """Lista todos os clientes (requer autenticação)"""
    logger.info("Tentando listar clientes")
    try:
        clients_collection = await Database.get_clients_collection()
        logger.info("Collection de clientes obtida com sucesso")
        clients = []
        async for client in clients_collection.find():
            client["id"] = str(client["_id"])
            clients.append(client)
        logger.info(f"Clientes listados com sucesso. Total: {len(clients)}")
        return clients
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar clientes: {str(e)}"
        )

@app.get("/clients/{client_id}", response_model=Client)
async def read_client(client_id: str, user = Depends(verify_token)):
    """Obtém um cliente específico (requer autenticação)"""
    logger.info(f"Tentando obter cliente com ID: {client_id}")
    try:
        clients_collection = await Database.get_clients_collection()
        logger.info("Collection de clientes obtida com sucesso")
        client = await clients_collection.find_one({"_id": ObjectId(client_id)})
        
        if client is None:
            logger.warning(f"Cliente com ID '{client_id}' não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        client["id"] = str(client["_id"])
        logger.info(f"Cliente obtido com sucesso. ID: {client_id}")
        return client
    except Exception as e:
        logger.error(f"Erro ao obter cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter cliente: {str(e)}"
        )

@app.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client_update: ClientUpdate, user = Depends(verify_token)):
    """Atualiza um cliente existente"""
    try:
        logger.info(f"Atualizando cliente {client_id}")
        
        clients_collection = await Database.get_clients_collection()
        
        # Verifica se o cliente existe
        client = await clients_collection.find_one({"_id": ObjectId(client_id)})
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Prepara os dados para atualização
        update_data = client_update.dict(exclude_unset=True)
        
        # Se houver atualização de contatos, processa-os
        if 'contacts' in update_data:
            contacts = update_data['contacts']
            logger.info(f"Atualizando contatos. Total recebido: {len(contacts)}")
            
            # Processa os contatos
            processed_contacts = []
            for contact in contacts:
                if isinstance(contact, dict):
                    processed_contact = {
                        "name": str(contact['name']).strip(),
                        "phone": str(contact['phone']).strip(),
                    }
                    if 'group' in contact and contact['group']:
                        processed_contact['group'] = str(contact['group']).strip()
                    processed_contacts.append(processed_contact)
            
            update_data['contacts'] = processed_contacts
            logger.info(f"Contatos processados: {len(processed_contacts)}")
        
        # Adiciona timestamp de atualização
        update_data["updated_at"] = datetime.utcnow()
        
        # Atualiza no MongoDB
        result = await clients_collection.update_one(
            {"_id": ObjectId(client_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning("Nenhuma alteração realizada no banco de dados")
        
        # Retorna o cliente atualizado
        updated_client = await clients_collection.find_one({"_id": ObjectId(client_id)})
        if not updated_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Erro ao recuperar cliente atualizado"
            )
        
        # Converte _id para string
        updated_client["id"] = str(updated_client.pop("_id"))
        
        logger.info(f"Cliente {client_id} atualizado com sucesso")
        if 'contacts' in update_data:
            logger.info(f"Contatos atualizados: {len(updated_client['contacts'])}")
        
        return updated_client
        
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

@app.delete("/clients/{client_id}")
async def delete_client(client_id: str, user = Depends(verify_admin)):
    """Deleta um cliente (requer admin)"""
    logger.info(f"Tentando deletar cliente com ID: {client_id}")
    try:
        clients_collection = await Database.get_clients_collection()
        logger.info("Collection de clientes obtida com sucesso")
        result = await clients_collection.delete_one({"_id": ObjectId(client_id)})
        
        if result.deleted_count == 0:
            logger.warning(f"Cliente com ID '{client_id}' não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        logger.info(f"Cliente deletado com sucesso. ID: {client_id}")
        return {"message": "Cliente deletado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar cliente: {str(e)}"
        )
