import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        if cls.client is None:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI não está definido no arquivo .env")
            
            print("Iniciando conexão com MongoDB...")
            cls.client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Testa a conexão
            await cls.client.admin.command('ping')
            print("Conexão com MongoDB estabelecida com sucesso!")
            
            cls.db = cls.client[os.getenv("DATABASE_NAME", "sbsender_clients")]

    @classmethod
    async def get_clients_collection(cls):
        if cls.db is None:
            await cls.connect()
        return cls.db.clients

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None

# Conecta ao banco de dados na inicialização
import asyncio
asyncio.create_task(Database.connect())
