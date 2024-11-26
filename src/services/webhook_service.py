from typing import List, Dict, Optional
from datetime import datetime
from src.database.mongodb import MongoDB

class WebhookService:
    def __init__(self):
        self.db = MongoDB().db
        self.collection = self.db.webhooks

    def create_webhook(self, title: str, url: str) -> Dict:
        """
        Cria um novo webhook.
        """
        webhook = {
            'title': title,
            'url': url,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'active': True
        }
        
        result = self.collection.insert_one(webhook)
        webhook['_id'] = str(result.inserted_id)
        return webhook

    def get_all_webhooks(self) -> List[Dict]:
        """
        Retorna todos os webhooks ativos.
        """
        webhooks = list(self.collection.find({'active': True}))
        for webhook in webhooks:
            webhook['_id'] = str(webhook['_id'])
        return webhooks

    def get_webhook_by_id(self, webhook_id: str) -> Optional[Dict]:
        """
        Busca um webhook pelo ID.
        """
        from bson import ObjectId
        webhook = self.collection.find_one({'_id': ObjectId(webhook_id), 'active': True})
        if webhook:
            webhook['_id'] = str(webhook['_id'])
        return webhook

    def update_webhook(self, webhook_id: str, title: str, url: str) -> Optional[Dict]:
        """
        Atualiza um webhook existente.
        """
        from bson import ObjectId
        update_data = {
            'title': title,
            'url': url,
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(webhook_id), 'active': True},
            {'$set': update_data}
        )
        
        if result.modified_count:
            webhook = self.get_webhook_by_id(webhook_id)
            return webhook
        return None

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Desativa um webhook (soft delete).
        """
        from bson import ObjectId
        result = self.collection.update_one(
            {'_id': ObjectId(webhook_id), 'active': True},
            {
                '$set': {
                    'active': False,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        return bool(result.modified_count)
