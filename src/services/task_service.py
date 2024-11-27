import time
import threading
import requests
import os
from datetime import datetime
from typing import Dict, List
import logging
from ..database.mongodb import MongoDB
from bson import ObjectId
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db=None):
        """
        Inicializa o serviço de tarefas.
        """
        self.db = db if db is not None else MongoDB().get_database()
        self.history_collection = self.db['history']
        self.provider_webhook = os.getenv('PROVIDER_WEBHOOK_URL')
        if not self.provider_webhook:
            raise Exception("PROVIDER_WEBHOOK_URL não configurado no arquivo .env")
        
        # Valida a URL do provedor
        parsed_url = urlparse(self.provider_webhook)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise Exception(f"URL do provedor inválida: {self.provider_webhook}")
            
        self.stop_flag = False
        self.thread = None
        logger.info(f"TaskService inicializado com webhook: {self.provider_webhook}")

    def start_processing(self):
        """
        Inicia o processamento em background.
        """
        if self.thread is None or not self.thread.is_alive():
            self.stop_flag = False
            self.thread = threading.Thread(target=self._process_pending_messages)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Processamento em background iniciado")

    def stop_processing(self):
        """
        Para o processamento em background.
        """
        self.stop_flag = True
        if self.thread:
            self.thread.join()
            logger.info("Processamento em background parado")

    def _process_pending_messages(self):
        """
        Processa mensagens pendentes em um loop.
        """
        while not self.stop_flag:
            try:
                # Busca mensagens pendentes
                pending_messages = self.history_collection.find({
                    'status': 'pending'
                })

                for message in pending_messages:
                    if self.stop_flag:
                        break

                    try:
                        # Valida os dados necessários
                        if not message.get('valid_numbers'):
                            raise Exception("Nenhum número válido para enviar")
                        
                        webhook_url = message.get('webhook_url')
                        if not webhook_url:
                            raise Exception("URL do webhook não encontrada")
                            
                        # Valida a URL do webhook
                        parsed_url = urlparse(webhook_url)
                        if not all([parsed_url.scheme, parsed_url.netloc]):
                            raise Exception(f"URL do webhook inválida: {webhook_url}")

                        # Atualiza status para processando
                        self.history_collection.update_one(
                            {'_id': message['_id']},
                            {'$set': {
                                'status': 'processing',
                                'processing_started_at': datetime.utcnow()
                            }}
                        )

                        logger.info(f"Enviando mensagem para o provedor - ID: {message['_id']}")
                        logger.info(f"Números: {len(message.get('valid_numbers', []))} - Webhook: {webhook_url}")

                        # Envia a mensagem para o webhook do provedor
                        # Remove campos específicos do MongoDB que não devem ser enviados
                        webhook_data = message.copy()
                        webhook_data.pop('_id', None)  # Remove o _id do MongoDB
                        webhook_data.pop('status', None)  # Remove status interno
                        webhook_data.pop('processing_started_at', None)
                        webhook_data.pop('processed_at', None)
                        webhook_data.pop('response_status', None)
                        webhook_data.pop('response_text', None)
                        webhook_data.pop('error', None)

                        # Função recursiva para converter ObjectIds e datetimes em strings
                        def convert_for_json(obj):
                            if isinstance(obj, dict):
                                return {key: convert_for_json(value) for key, value in obj.items()}
                            elif isinstance(obj, list):
                                return [convert_for_json(item) for item in obj]
                            elif isinstance(obj, ObjectId):
                                return str(obj)
                            elif isinstance(obj, datetime):
                                return obj.isoformat()
                            return obj

                        # Converte todos os ObjectIds e datetimes no payload
                        webhook_data = convert_for_json(webhook_data)

                        logger.info(f"Enviando mensagem para o provedor - ID: {message['_id']}")
                        logger.info(f"Payload: {webhook_data}")

                        response = requests.post(
                            self.provider_webhook,
                            json=webhook_data,
                            timeout=30
                        )

                        # Atualiza o status baseado na resposta
                        new_status = 'completed' if response.status_code == 200 else 'failed'
                        update_data = {
                            'status': new_status,
                            'processed_at': datetime.utcnow(),
                            'response_status': response.status_code,
                            'response_text': response.text
                        }

                        if new_status == 'failed':
                            update_data['error'] = f"Erro do provedor: Status {response.status_code} - {response.text}"

                        self.history_collection.update_one(
                            {'_id': message['_id']},
                            {'$set': update_data}
                        )

                        logger.info(f"Mensagem {message['_id']} processada com status {new_status}")

                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Erro ao processar mensagem {message['_id']}: {error_msg}")
                        
                        # Em caso de erro, marca como falha
                        self.history_collection.update_one(
                            {'_id': message['_id']},
                            {'$set': {
                                'status': 'failed',
                                'processed_at': datetime.utcnow(),
                                'error': error_msg
                            }}
                        )

            except Exception as e:
                logger.error(f"Erro no loop de processamento: {str(e)}")

            # Aguarda 1 minuto antes da próxima verificação
            time.sleep(60)
