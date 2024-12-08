from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None
    users_collection = None

    @classmethod
    async def connect(cls):
        """Conecta ao MongoDB"""
        try:
            if cls.client is None:
                print("Iniciando conexão com MongoDB...")
                mongodb_uri = os.getenv("MONGODB_URI")
                if not mongodb_uri:
                    raise ValueError("MONGODB_URI não está definido no arquivo .env")
                
                cls.client = AsyncIOMotorClient(
                    mongodb_uri,
                    serverSelectionTimeoutMS=5000
                )
                # Testa a conexão
                await cls.client.admin.command('ping')
                print("Conexão com MongoDB estabelecida com sucesso!")
                
                cls.db = cls.client[os.getenv("DATABASE_NAME", "sbsender_auth")]
                cls.users_collection = cls.db["users"]
                
                # Cria índices únicos
                await cls.users_collection.create_index("username", unique=True)
                await cls.users_collection.create_index("email", unique=True)
                
                print("Conectado ao MongoDB com sucesso!")
            return cls.client
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            cls.client = None
            cls.users_collection = None
            raise

    @classmethod
    async def disconnect(cls):
        """Desconecta do MongoDB"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.users_collection = None
            print("Desconectado do MongoDB!")

    @classmethod
    async def get_users_collection(cls):
        """Retorna a coleção de usuários"""
        if cls.users_collection is None:
            await cls.connect()
        return cls.users_collection

# Não vamos mais conectar automaticamente na inicialização
# A conexão será feita sob demanda quando necessário
