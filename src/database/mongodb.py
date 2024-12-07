import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging
import time

# Configura o logger
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance

    def __init__(self):
        """
        Inicializa a conexão com o MongoDB.
        """
        if self.client is None:
            self.connect()
            self.setup_database()

    def connect(self):
        """
        Estabelece conexão com o MongoDB usando as configurações do .env
        """
        try:
            mongo_uri = os.secrets('MONGODB_URI')
            db_name = os.secrets('MONGODB_DATABASE')
            
            if not mongo_uri or not db_name:
                raise Exception("MONGODB_URI ou MONGODB_DATABASE não configurados no arquivo .env")
            
            # Tenta conectar até 3 vezes
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    self.client = MongoClient(mongo_uri)
                    # Testa a conexão
                    self.client.admin.command('ping')
                    self.db = self.client[db_name]
                    logger.info("Conexão com MongoDB estabelecida com sucesso")
                    return
                except Exception as e:
                    last_error = e
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Tentativa {retry_count} falhou, tentando novamente em 2 segundos...")
                        time.sleep(2)
            
            # Se chegou aqui, todas as tentativas falharam
            raise Exception(f"Todas as tentativas de conexão falharam. Último erro: {str(last_error)}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            raise Exception(f"Erro ao conectar ao MongoDB: {str(e)}")

    def setup_database(self):
        """
        Configura as collections necessárias se não existirem.
        """
        try:
            if self.db is None:
                raise Exception("Conexão com o banco de dados não estabelecida")
                
            # Lista de collections necessárias
            required_collections = ['webhooks', 'clients', 'history']
            existing_collections = self.db.list_collection_names()

            # Cria as collections que não existem
            for collection in required_collections:
                if collection not in existing_collections:
                    logger.info(f"Criando collection {collection}")
                    self.db.create_collection(collection)
                    
                    # Adiciona índices necessários
                    if collection == 'webhooks':
                        self.db[collection].create_index([("title", 1)], unique=True)
                        self.db[collection].create_index([("client_id", 1)])
                    elif collection == 'clients':
                        self.db[collection].create_index([("name", 1)], unique=True)
                    elif collection == 'history':
                        self.db[collection].create_index([("created_at", -1)])
                        self.db[collection].create_index([("client_id", 1)])
                        self.db[collection].create_index([("webhook_id", 1)])
                        self.db[collection].create_index([("status", 1)])

            logger.info("Setup do banco de dados concluído com sucesso")
        except Exception as e:
            logger.error(f"Erro ao configurar banco de dados: {str(e)}")
            raise Exception(f"Erro ao configurar banco de dados: {str(e)}")

    def get_database(self):
        """
        Retorna a instância do banco de dados.
        """
        if self.db is None:
            self.connect()
            self.setup_database()
        return self.db

    def close(self):
        """
        Fecha a conexão com o MongoDB.
        """
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Conexão com MongoDB fechada")
