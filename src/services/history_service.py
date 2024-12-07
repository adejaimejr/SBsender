from datetime import datetime
from bson import ObjectId
from ..database.mongodb import MongoDB
from typing import Dict, List, Optional
import logging
import pytz

logger = logging.getLogger(__name__)

class HistoryService:
    def __init__(self, db=None):
        """
        Inicializa o serviço de histórico.
        """
        self.db = db if db is not None else MongoDB().get_database()
        self.history_collection = self.db['history']

    def register_import(self, valid_numbers: List[str], invalid_numbers: List[str], webhook_id: str, webhook_name: str, webhook_url: str, method: str = 'txt') -> Dict:
        """
        Registra uma importação de números no histórico.
        
        Args:
            valid_numbers (List[str]): Lista de números válidos
            invalid_numbers (List[str]): Lista de números inválidos
            webhook_id (str): ID do webhook usado para envio
            webhook_name (str): Nome do webhook selecionado
            webhook_url (str): URL do webhook
            method (str): Método de importação ('txt' ou 'csv')
            
        Returns:
            Dict: Registro criado no histórico
        """
        # Converte o webhook_id para ObjectId
        webhook_obj_id = ObjectId(webhook_id)
        
        # Busca o cliente através do webhook
        webhook = self.db['webhooks'].find_one({'_id': webhook_obj_id})
        client_name = 'Cliente'
        if webhook and 'client_id' in webhook:
            client = self.db['clients'].find_one({'_id': webhook['client_id']})
            if client:
                client_name = client['name']
        
        history_entry = {
            'operation': method.lower(),  # 'txt' ou 'csv'
            'method': method.lower(),  # Campo adicional para compatibilidade
            'total_processed': len(valid_numbers) + len(invalid_numbers),
            'valid_count': len(valid_numbers),
            'invalid_count': len(invalid_numbers),
            'valid_numbers': valid_numbers,
            'invalid_numbers': invalid_numbers,
            'webhook_id': webhook_obj_id,
            'webhook_name': webhook_name,
            'webhook_url': webhook_url,
            'client_name': client_name,
            'status': 'pending',
            'timestamp': datetime.utcnow(),
            'details': {
                'valid_numbers': valid_numbers,
                'invalid_numbers': invalid_numbers,
                'webhook_id': str(webhook_obj_id),
                'webhook_name': webhook_name,
                'webhook_url': webhook_url,
                'method': method.lower(),
                'client_name': client_name
            }
        }
        
        result = self.history_collection.insert_one(history_entry)
        history_entry['_id'] = str(result.inserted_id)
        history_entry['webhook_id'] = str(webhook_obj_id)  # Converte de volta para string na resposta
        return history_entry

    def register_send(self, numbers: List[str], webhook_id: str, webhook_name: str, webhook_url: str) -> Dict:
        """
        Registra uma operação de envio no histórico.
        
        Args:
            numbers (List[str]): Lista de números para envio
            webhook_id (str): ID do webhook usado para envio
            webhook_name (str): Nome do webhook selecionado
            webhook_url (str): URL do webhook
            
        Returns:
            Dict: Registro criado no histórico
        """
        # Converte o webhook_id para ObjectId
        webhook_obj_id = ObjectId(webhook_id)
        
        history_entry = {
            'operation': 'send',
            'numbers_count': len(numbers),
            'numbers': numbers,
            'webhook_id': webhook_obj_id,
            'webhook_name': webhook_name,
            'webhook_url': webhook_url,
            'status': 'completed',
            'timestamp': datetime.utcnow(),
            'details': {
                'numbers': numbers,
                'webhook_id': str(webhook_obj_id),
                'webhook_name': webhook_name,
                'webhook_url': webhook_url
            }
        }
        
        result = self.history_collection.insert_one(history_entry)
        history_entry['_id'] = str(result.inserted_id)
        history_entry['webhook_id'] = str(webhook_obj_id)  # Converte de volta para string na resposta
        return history_entry

    def get_history(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Recupera o histórico de operações.
        
        Args:
            start_date (datetime, optional): Data inicial para filtro
            end_date (datetime, optional): Data final para filtro
            
        Returns:
            List[Dict]: Lista de registros do histórico
        """
        query = {}
        
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date
        
        cursor = self.history_collection.find(query).sort('timestamp', -1)
        
        # Converte ObjectId para string no resultado
        history = []
        for record in cursor:
            record['_id'] = str(record['_id'])
            if record.get('webhook_id'):
                record['webhook_id'] = str(record['webhook_id'])
            # Converte o timestamp para string ISO
            if 'timestamp' in record:
                record['timestamp'] = record['timestamp'].isoformat()
            history.append(record)
        
        return history

    def get_history_by_id(self, history_id: str) -> Optional[Dict]:
        """
        Busca um registro específico do histórico.
        """
        history = self.history_collection.find_one({'_id': ObjectId(history_id)})
        if history:
            history['_id'] = str(history['_id'])
            if history.get('webhook_id'):
                history['webhook_id'] = str(history['webhook_id'])
            # Converte o timestamp para string ISO
            if 'timestamp' in history:
                history['timestamp'] = history['timestamp'].isoformat()
        return history

    def format_history_entry(self, entry: Dict) -> Dict:
        """
        Formata um registro do histórico para exibição.
        
        Args:
            entry (Dict): Registro do histórico
            
        Returns:
            Dict: Registro formatado
        """
        timestamp = entry.get('timestamp', datetime.utcnow())
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.utcnow()
                
        # Converte UTC para horário local (Brasil)
        local_tz = pytz.timezone('America/Sao_Paulo')
        local_timestamp = pytz.utc.localize(timestamp).astimezone(local_tz)
        
        formatted_date = local_timestamp.strftime('%d/%m/%Y %H:%M')
        client_name = entry.get('client_name', 'Cliente')
        webhook_name = entry.get('webhook_name', 'Webhook')
        
        entry['display_title'] = f"{formatted_date} - {webhook_name} ({client_name})"
        return entry
