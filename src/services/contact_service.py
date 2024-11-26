from typing import List, Dict, Any
import pandas as pd
from ..utils.phone_utils import format_phone_number
from .message_service import MessageService
from datetime import datetime

class ContactService:
    def __init__(self, history_service=None):
        """
        Inicializa o serviço de contatos.
        
        Args:
            history_service: Serviço para registro de histórico (opcional)
        """
        self.history_service = history_service
        self.message_service = MessageService()

    def process_contacts(self, input_text: str, webhook_url: str = None) -> Dict[str, Any]:
        """
        Processa uma lista de contatos a partir de um texto.
        
        Args:
            input_text (str): Texto com os números de telefone
            webhook_url (str, optional): URL do webhook para envio
            
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
        
        # Registra no histórico se disponível
        if self.history_service:
            self.history_service.add_record(
                "import",
                "text",
                result
            )
        
        return result

    def process_csv(self, file_content: bytes, column_name: str, webhook_url: str = None) -> Dict[str, Any]:
        """
        Processa contatos a partir de um arquivo CSV.
        
        Args:
            file_content (bytes): Conteúdo do arquivo CSV
            column_name (str): Nome da coluna que contém os números
            webhook_url (str, optional): URL do webhook para envio
            
        Returns:
            Dict[str, Any]: Resultado do processamento com números válidos e inválidos
        """
        try:
            # Lê o CSV
            df = pd.read_csv(pd.io.common.BytesIO(file_content))
            
            if column_name not in df.columns:
                return {
                    "error": f"Coluna '{column_name}' não encontrada no arquivo CSV",
                    "available_columns": df.columns.tolist()
                }
            
            # Processa cada número
            numbers = df[column_name].astype(str).tolist()
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
            
            # Registra no histórico se disponível
            if self.history_service:
                self.history_service.add_record(
                    "import",
                    "csv",
                    result
                )
            
            return result
            
        except Exception as e:
            return {
                "error": f"Erro ao processar arquivo CSV: {str(e)}"
            }

    def send_messages(self, numbers: List[str], message: str, webhook_url: str = None) -> Dict[str, Any]:
        """
        Envia mensagens para uma lista de números.
        
        Args:
            numbers (List[str]): Lista de números formatados
            message (str): Mensagem a ser enviada
            webhook_url (str, optional): URL do webhook específico
            
        Returns:
            Dict[str, Any]: Resultado da operação
        """
        result = self.message_service.send_messages(numbers, message, webhook_url)
        
        # Registra no histórico se disponível
        if self.history_service:
            self.history_service.add_record(
                "send",
                "webhook",
                {
                    "total_numbers": len(numbers),
                    "success": result["success"],
                    "message": result["message"],
                    "webhook_url": webhook_url or self.message_service.webhook_url,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return result
