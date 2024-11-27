from datetime import datetime
from bson import ObjectId
from ..database.mongodb import MongoDB
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self, db=None):
        """
        Inicializa o serviço de webhooks.
        """
        self.db = db if db is not None else MongoDB().get_database()
        self.collection = self.db['webhooks']
        logger.info("WebhookService inicializado")

    def create_webhook(self, title: str, url: str, client_id: str, client_name: str) -> Dict:
        """
        Cria um novo webhook.
        """
        logger.info(f"Iniciando criação de webhook - Título: {title}, URL: {url}")
        
        # Verifica se já existe um webhook com o mesmo título
        existing_webhook = self.collection.find_one({'title': title, 'active': True})
        if existing_webhook:
            logger.warning(f"Webhook com título '{title}' já existe")
            raise ValueError(f"Já existe um webhook com o título '{title}'")
        
        webhook = {
            'title': title,
            'url': url,
            'client_id': ObjectId(client_id),
            'client_name': client_name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'active': True
        }
        
        logger.debug(f"Dados do webhook a ser criado: {webhook}")
        result = self.collection.insert_one(webhook)
        webhook['_id'] = str(result.inserted_id)
        webhook['client_id'] = str(webhook['client_id'])
        logger.info(f"Webhook criado com sucesso. ID: {webhook['_id']}")
        return webhook

    def get_all_webhooks(self) -> List[Dict]:
        """
        Retorna todos os webhooks ativos.
        """
        logger.info("Buscando todos os webhooks ativos")
        webhooks = list(self.collection.find({'active': True}))
        for webhook in webhooks:
            webhook['_id'] = str(webhook['_id'])
            webhook['client_id'] = str(webhook['client_id'])
        logger.info(f"Total de webhooks encontrados: {len(webhooks)}")
        return webhooks

    def get_webhook_by_id(self, webhook_id: str) -> Optional[Dict]:
        """
        Busca um webhook pelo ID.
        """
        logger.info(f"Buscando webhook pelo ID: {webhook_id}")
        webhook = self.collection.find_one({'_id': ObjectId(webhook_id), 'active': True})
        if webhook:
            webhook['_id'] = str(webhook['_id'])
            webhook['client_id'] = str(webhook['client_id'])
            logger.info(f"Webhook encontrado: {webhook['_id']}")
        else:
            logger.info(f"Webhook não encontrado com ID: {webhook_id}")
        return webhook

    def get_webhooks_by_client(self, client_id: str) -> List[Dict]:
        """
        Retorna todos os webhooks ativos de um cliente específico.
        """
        try:
            webhooks = list(self.collection.find({
                'client_id': ObjectId(client_id),
                'active': True
            }))
            for webhook in webhooks:
                webhook['_id'] = str(webhook['_id'])
                webhook['client_id'] = str(webhook['client_id'])
            return webhooks
        except Exception as e:
            logger.error(f"Erro ao buscar webhooks do cliente {client_id}: {str(e)}")
            raise Exception(f"Erro ao buscar webhooks: {str(e)}")

    def update_webhook(self, webhook_id: str, title: str, url: str, client_id: str, client_name: str) -> Optional[Dict]:
        """
        Atualiza um webhook existente.
        """
        logger.info(f"Atualizando webhook com ID: {webhook_id}")
        update_data = {
            'title': title,
            'url': url,
            'client_id': ObjectId(client_id),
            'client_name': client_name,
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(webhook_id), 'active': True},
            {'$set': update_data}
        )
        
        if result.modified_count:
            logger.info(f"Webhook atualizado com sucesso: {webhook_id}")
            webhook = self.get_webhook_by_id(webhook_id)
            return webhook
        else:
            logger.info(f"Webhook não encontrado ou não atualizado: {webhook_id}")
        return None

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Desativa um webhook (soft delete).
        """
        logger.info(f"Desativando webhook com ID: {webhook_id}")
        result = self.collection.update_one(
            {'_id': ObjectId(webhook_id), 'active': True},
            {
                '$set': {
                    'active': False,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        if result.modified_count:
            logger.info(f"Webhook desativado com sucesso: {webhook_id}")
        else:
            logger.info(f"Webhook não encontrado ou não desativado: {webhook_id}")
        return bool(result.modified_count)
