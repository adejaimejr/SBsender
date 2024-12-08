import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        if cls.client is None:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                logger.error("MONGODB_URI não está definido no arquivo .env")
                raise ValueError("MONGODB_URI não está definido no arquivo .env")
            
            database_name = os.getenv("DATABASE_NAME", "sbsender_clients")
            logger.info(f"Iniciando conexão com MongoDB... URI: {mongodb_uri}, Database: {database_name}")
            
            try:
                cls.client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                # Testa a conexão
                await cls.client.admin.command('ping')
                logger.info("Conexão com MongoDB estabelecida com sucesso!")
                
                # Configura o banco de dados
                cls.db = cls.client[database_name]
                
                # Cria a collection se não existir
                if "clients" not in await cls.db.list_collection_names():
                    logger.info("Collection 'clients' não encontrada. Criando...")
                    await cls.db.create_collection("clients")
                    # Cria índice único no campo name
                    await cls.db.clients.create_index("name", unique=True)
                    logger.info("Collection 'clients' criada com sucesso!")
                else:
                    logger.info("Collection 'clients' já existe")
                
                logger.info(f"Banco de dados '{database_name}' configurado com sucesso!")
            except Exception as e:
                logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
                raise e

    @classmethod
    async def get_clients_collection(cls):
        if cls.db is None:
            logger.info("Banco de dados não inicializado. Conectando...")
            await cls.connect()
        return cls.db.clients

    @classmethod
    async def close(cls):
        if cls.client is not None:
            logger.info("Fechando conexão com MongoDB...")
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Conexão fechada com sucesso!")

# Conecta ao banco de dados na inicialização
import asyncio
asyncio.create_task(Database.connect())
