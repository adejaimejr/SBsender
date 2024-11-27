from datetime import datetime
from bson import ObjectId
from ..database.mongodb import MongoDB
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ClientService:
    def __init__(self, db=None):
        """
        Inicializa o serviço de clientes.
        """
        self.db = db if db is not None else MongoDB().get_database()
        self.collection = self.db['clients']
        logger.info("ClientService inicializado")

    def create_client(self, name: str, description: str = None) -> Dict:
        """
        Cria um novo cliente.
        """
        logger.info(f"Iniciando criação de cliente - Nome: {name}")
        
        # Verifica se já existe um cliente com o mesmo nome
        existing_client = self.collection.find_one({
            'name': {'$regex': f'^{name}$', '$options': 'i'},  # Case-insensitive
            'active': True
        })
        if existing_client:
            logger.warning(f"Cliente com nome '{name}' já existe")
            raise ValueError(f"Já existe um cliente com o nome '{name}'")
        
        client = {
            'name': name.strip(),  # Remove espaços em branco
            'description': description.strip() if description else None,  # Remove espaços em branco
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'active': True
        }
        
        logger.debug(f"Dados do cliente a ser criado: {client}")
        result = self.collection.insert_one(client)
        client['_id'] = str(result.inserted_id)
        logger.info(f"Cliente criado com sucesso. ID: {client['_id']}")
        return client

    def get_all_clients(self) -> List[Dict]:
        """
        Retorna todos os clientes ativos.
        """
        logger.info("Buscando todos os clientes ativos")
        clients = list(self.collection.find({'active': True}))
        for client in clients:
            client['_id'] = str(client['_id'])
        logger.info(f"Total de clientes encontrados: {len(clients)}")
        return clients

    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """
        Busca um cliente pelo ID.
        """
        logger.info(f"Buscando cliente pelo ID: {client_id}")
        client = self.collection.find_one({'_id': ObjectId(client_id), 'active': True})
        if client:
            client['_id'] = str(client['_id'])
            logger.info(f"Cliente encontrado: {client['_id']}")
        else:
            logger.info(f"Cliente não encontrado com ID: {client_id}")
        return client

    def update_client(self, client_id: str, name: str, description: str = None) -> Optional[Dict]:
        """
        Atualiza um cliente existente.
        """
        logger.info(f"Atualizando cliente com ID: {client_id}")
        
        # Verifica se já existe outro cliente com o mesmo nome
        existing_client = self.collection.find_one({
            '_id': {'$ne': ObjectId(client_id)},
            'name': name,
            'active': True
        })
        if existing_client:
            logger.warning(f"Outro cliente com nome '{name}' já existe")
            raise ValueError(f"Já existe outro cliente com o nome '{name}'")
        
        update_data = {
            'name': name,
            'description': description,
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(client_id), 'active': True},
            {'$set': update_data}
        )
        
        if result.modified_count:
            logger.info(f"Cliente atualizado com sucesso: {client_id}")
            client = self.get_client_by_id(client_id)
            return client
        logger.info(f"Cliente não encontrado ou não atualizado: {client_id}")
        return None

    def delete_client(self, client_id: str) -> bool:
        """
        Desativa um cliente (soft delete).
        """
        logger.info(f"Desativando cliente com ID: {client_id}")
        result = self.collection.update_one(
            {'_id': ObjectId(client_id), 'active': True},
            {
                '$set': {
                    'active': False,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        if result.modified_count:
            logger.info(f"Cliente desativado com sucesso: {client_id}")
        else:
            logger.info(f"Cliente não encontrado ou não desativado: {client_id}")
        return bool(result.modified_count)
