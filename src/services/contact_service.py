from typing import Dict, List, Optional, Any
import pandas as pd
from ..utils.phone_utils import format_phone_number
from .message_service import MessageService
from datetime import datetime
from bson import ObjectId
from ..database.mongodb import MongoDB
import logging

logger = logging.getLogger(__name__)

class ContactService:
    def __init__(self, history_service=None):
        """
        Inicializa o serviço de contatos.
        
        Args:
            history_service: Serviço para registro de histórico (opcional)
        """
        self.history_service = history_service
        self.message_service = MessageService()

    def process_contacts(self, input_text: str, webhook_url: str, webhook_id: str, webhook_name: str, method: str = 'txt') -> Dict[str, Any]:
        """
        Processa uma lista de contatos a partir de um texto.
        
        Args:
            input_text (str): Texto com os números de telefone
            webhook_url (str): URL do webhook para envio
            webhook_id (str): ID do webhook para registro
            webhook_name (str): Nome do webhook selecionado
            method (str): Método de importação ('txt' ou 'csv')
            
        Returns:
            Dict[str, Any]: Resultado do processamento com números válidos e inválidos
        """
        # Divide o texto em linhas e remove espaços em branco
        numbers = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        # Processa cada número
        valid_numbers = []
        invalid_numbers = []
        
        for number in numbers:
            formatted = format_phone_number(number)
            if formatted:
                valid_numbers.append(formatted)
            else:
                invalid_numbers.append(number)
        
        result = {
            "valid_numbers": valid_numbers,
            "invalid_numbers": invalid_numbers,
            "total_processed": len(numbers),
            "total_valid": len(valid_numbers),
            "total_invalid": len(invalid_numbers),
            "timestamp": datetime.now().isoformat()
        }
        
        # Registra a operação no histórico
        if self.history_service:
            self.history_service.register_import(
                valid_numbers=valid_numbers,
                invalid_numbers=invalid_numbers,
                webhook_id=webhook_id,
                webhook_name=webhook_name,
                webhook_url=webhook_url,
                method=method
            )
        
        return result

    def process_csv(self, file_content: bytes, column_name: str, webhook_url: str, webhook_id: str, webhook_name: str, method: str = 'csv') -> Dict[str, Any]:
        """
        Processa contatos a partir de um arquivo CSV.
        
        Args:
            file_content (bytes): Conteúdo do arquivo CSV
            column_name (str): Nome da coluna que contém os números
            webhook_url (str): URL do webhook para envio
            webhook_id (str): ID do webhook para registro
            webhook_name (str): Nome do webhook selecionado
            method (str): Método de importação ('txt' ou 'csv')
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        try:
            # Lê o CSV
            df = pd.read_csv(pd.io.common.BytesIO(file_content))
            
            if column_name not in df.columns:
                return {"error": f"Coluna '{column_name}' não encontrada no arquivo"}
            
            # Extrai os números da coluna selecionada
            numbers = df[column_name].astype(str).tolist()
            numbers_text = '\n'.join(numbers)
            
            # Usa o método process_contacts para processar os números
            return self.process_contacts(
                numbers_text,
                webhook_url=webhook_url,
                webhook_id=webhook_id,
                webhook_name=webhook_name,
                method=method
            )
            
        except Exception as e:
            return {"error": f"Erro ao processar arquivo CSV: {str(e)}"}

    def send_messages(self, numbers: List[str], message: str, webhook_url: str, webhook_id: str) -> Dict[str, Any]:
        """
        Envia mensagens para uma lista de números.
        
        Args:
            numbers (List[str]): Lista de números formatados
            message (str): Mensagem a ser enviada
            webhook_url (str): URL do webhook para envio
            webhook_id (str): ID do webhook para registro
            
        Returns:
            Dict[str, Any]: Resultado do envio
        """
        try:
            # Envia mensagem para cada número
            for number in numbers:
                self.message_service.send_message(number, message, webhook_url)
            
            result = {
                "success": True,
                "message": f"Mensagens enviadas com sucesso para {len(numbers)} números"
            }
            
            # Registra o envio no histórico
            if self.history_service:
                self.history_service.register_send(
                    numbers=numbers,
                    message=message,
                    webhook_id=webhook_id
                )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao enviar mensagens: {str(e)}"
            }

    def get_history(self, client_id: str = None) -> List[Dict]:
        """
        Retorna o histórico de envios, opcionalmente filtrado por cliente.
        """
        try:
            # Busca o webhook relacionado ao cliente
            if client_id:
                webhook_ids = []
                webhooks = list(self.history_service.db['webhooks'].find({'client_id': ObjectId(client_id)}))
                for webhook in webhooks:
                    webhook_ids.append(webhook['_id'])
                
                query = {
                    'status': {'$exists': True},
                    'webhook_id': {'$in': webhook_ids}
                }
            else:
                query = {'status': {'$exists': True}}
            
            history = list(self.history_service.history_collection.find(query).sort('timestamp', -1))
            
            # Converte ObjectId para string para serialização
            for entry in history:
                entry['_id'] = str(entry['_id'])
                if 'client_id' in entry:
                    entry['client_id'] = str(entry['client_id'])
                if 'webhook_id' in entry:
                    entry['webhook_id'] = str(entry['webhook_id'])
                if 'timestamp' in entry:
                    entry['created_at'] = entry['timestamp']
                # Adiciona campos necessários se não existirem
                if 'method' not in entry:
                    entry['method'] = 'txt'
                if 'total_processed' not in entry:
                    entry['total_processed'] = len(entry.get('valid_numbers', []))
                if 'valid_numbers' not in entry:
                    entry['valid_numbers'] = entry.get('numbers', [])
                if 'invalid_numbers' not in entry:
                    entry['invalid_numbers'] = []
                
                # Busca o nome do cliente pelo webhook
                if 'webhook_id' in entry:
                    webhook = self.history_service.db['webhooks'].find_one({'_id': ObjectId(entry['webhook_id'])})
                    if webhook and 'client_id' in webhook:
                        client = self.history_service.db['clients'].find_one({'_id': webhook['client_id']})
                        if client:
                            entry['client_name'] = client['name']
                        else:
                            entry['client_name'] = 'Cliente'
                    else:
                        entry['client_name'] = 'Cliente'
                else:
                    entry['client_name'] = 'Cliente'
            
            return history
        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {str(e)}")
            raise Exception(f"Erro ao buscar histórico: {str(e)}")
