import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
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
            
            cls.db = cls.client[os.getenv("DATABASE_NAME", "sbsender_history")]
            
            # Cria índices
            await cls.get_history_collection().create_index([("created_at", DESCENDING)])
            await cls.get_history_collection().create_index("client_id")
            await cls.get_history_collection().create_index("message_id")
            await cls.get_history_collection().create_index("webhook_id")
            await cls.get_history_collection().create_index("event_type")

    @classmethod
    def get_history_collection(cls):
        if cls.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.db.history

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
