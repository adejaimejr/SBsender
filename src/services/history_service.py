from typing import List, Dict, Optional
from datetime import datetime
from src.database.mongodb import MongoDB

class HistoryService:
    def __init__(self):
        self.db = MongoDB().db
        self.collection = self.db.history

    def register_import(self, valid_numbers: List[str], invalid_numbers: List[str], webhook_id: Optional[str] = None) -> Dict:
        """
        Registra uma importação de números no histórico.
        """
        history_entry = {
            'type': 'import',
            'valid_count': len(valid_numbers),
            'invalid_count': len(invalid_numbers),
            'valid_numbers': valid_numbers,
            'invalid_numbers': invalid_numbers,
            'webhook_id': webhook_id,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(history_entry)
        history_entry['_id'] = str(result.inserted_id)
        return history_entry

    def register_send(self, history_id: str, success_numbers: List[str], failed_numbers: List[str]) -> Optional[Dict]:
        """
        Atualiza o registro de histórico com o resultado do envio.
        """
        from bson import ObjectId
        
        update_data = {
            'status': 'completed',
            'success_count': len(success_numbers),
            'failed_count': len(failed_numbers),
            'success_numbers': success_numbers,
            'failed_numbers': failed_numbers,
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(history_id)},
            {'$set': update_data}
        )
        
        if result.modified_count:
            history = self.collection.find_one({'_id': ObjectId(history_id)})
            history['_id'] = str(history['_id'])
            return history
        return None

    def get_history(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Busca o histórico de importações e envios.
        """
        query = {}
        if start_date:
            query['created_at'] = {'$gte': start_date}
        if end_date:
            if 'created_at' in query:
                query['created_at']['$lte'] = end_date
            else:
                query['created_at'] = {'$lte': end_date}
        
        history = list(self.collection.find(query).sort('created_at', -1))
        for entry in history:
            entry['_id'] = str(entry['_id'])
        return history

    def get_history_by_id(self, history_id: str) -> Optional[Dict]:
        """
        Busca um registro específico do histórico.
        """
        from bson import ObjectId
        history = self.collection.find_one({'_id': ObjectId(history_id)})
        if history:
            history['_id'] = str(history['_id'])
        return history
