import requests
import json
from typing import List, Dict, Any
from datetime import datetime

class MessageService:
    def __init__(self, webhook_url: str = None):
        """
        Inicializa o serviço de mensagens.
        
        Args:
            webhook_url (str, optional): URL do webhook para envio de mensagens.
        """
        self.webhook_url = webhook_url or "https://n8nwebhooks.i92tecnologia.com.br/webhook/fb45f8f6-7eb6-4736-9e99-7996b3c28281"

    def send_messages(self, phone_numbers: List[str], message: str, webhook_url: str = None) -> Dict[str, Any]:
        """
        Envia mensagens para uma lista de números através do webhook.
        
        Args:
            phone_numbers (List[str]): Lista de números de telefone formatados
            message (str): Mensagem a ser enviada
            webhook_url (str, optional): URL do webhook específico para este envio
            
        Returns:
            Dict[str, Any]: Resultado da operação com status e detalhes
        """
        url = webhook_url or self.webhook_url
        
        try:
            payload = {
                "phones": phone_numbers,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Mensagens enviadas com sucesso",
                    "details": {
                        "total_numbers": len(phone_numbers),
                        "webhook_response": response.json() if response.text else None,
                        "timestamp": payload["timestamp"]
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro ao enviar mensagens: Status {response.status_code}",
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text,
                        "timestamp": payload["timestamp"]
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao enviar mensagens: {str(e)}",
                "details": {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }

    def validate_webhook(self, webhook_url: str) -> bool:
        """
        Valida se um webhook está acessível e funcionando.
        
        Args:
            webhook_url (str): URL do webhook a ser validada
            
        Returns:
            bool: True se o webhook está válido, False caso contrário
        """
        try:
            # Faz uma requisição de teste com um payload mínimo
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=5  # Timeout de 5 segundos
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
