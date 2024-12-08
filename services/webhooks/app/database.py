import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI não está definido no arquivo .env")
            
            print("Iniciando conexão com MongoDB...")
            cls.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Testa a conexão
            cls.client.admin.command('ping')
            print("Conexão com MongoDB estabelecida com sucesso!")
            
            cls.db = cls.client[os.getenv("DATABASE_NAME", "sbsender_webhooks")]

    @classmethod
    def get_webhooks_collection(cls):
        if cls.db is None:
            cls.connect()
        return cls.db.webhooks

    @classmethod
    def close(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
