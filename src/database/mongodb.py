from pymongo import MongoClient
import os
from typing import Optional

class MongoDB:
    _instance = None
    _client: Optional[MongoClient] = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        """Conecta ao MongoDB usando as variáveis de ambiente."""
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        database_name = os.getenv('MONGODB_DATABASE', 'sbsender')
        
        try:
            self._client = MongoClient(mongodb_uri)
            self._db = self._client[database_name]
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            raise

    @property
    def db(self):
        """Retorna a instância do banco de dados."""
        return self._db

    def close(self):
        """Fecha a conexão com o MongoDB."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    def __del__(self):
        """Garante que a conexão seja fechada quando o objeto for destruído."""
        self.close()
