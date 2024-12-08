import os
import json
import aiohttp
import asyncio
import jinja2
from datetime import datetime
from typing import Dict, Any, Optional
from .models import Message, MessageStatus, MessageType
from .database import Database

class MessageProcessor:
    _template_env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        autoescape=True
    )

    @classmethod
    def render_template(cls, template: str, data: Dict[str, Any]) -> str:
        """Renderiza um template usando Jinja2"""
        try:
            template = cls._template_env.from_string(template)
            return template.render(**data)
        except Exception as e:
            raise ValueError(f"Erro ao renderizar template: {str(e)}")

    @staticmethod
    async def send_webhook(client_id: str, content: str, metadata: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Envia um webhook para o cliente"""
        try:
            webhook_url = os.getenv("WEBHOOK_SERVICE_URL")
            if not webhook_url:
                raise ValueError("WEBHOOK_SERVICE_URL não configurada")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{webhook_url}/webhooks",
                    json={
                        "client_id": client_id,
                        "event_type": "message",
                        "payload": {
                            "content": content,
                            "metadata": metadata
                        }
                    }
                ) as response:
                    if response.status not in (200, 201, 202):
                        error_data = await response.text()
                        return False, f"Erro ao enviar webhook: {error_data}"
                    return True, None
        except Exception as e:
            return False, f"Erro ao enviar webhook: {str(e)}"

    @classmethod
    async def process_message(cls, message_id: str):
        """Processa uma mensagem"""
        messages_collection = Database.get_messages_collection()
        message_data = messages_collection.find_one({"_id": message_id})
        
        if not message_data:
            return
        
        message = Message(**message_data)
        
        # Atualiza status para processando
        messages_collection.update_one(
            {"_id": message_id},
            {
                "$set": {
                    "status": MessageStatus.PROCESSING,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        try:
            # Processa o conteúdo da mensagem
            content = message.content
            if message.type == MessageType.TEMPLATE and message.template_data:
                content = cls.render_template(content, message.template_data)

            # Envia para cada cliente
            sent_count = 0
            failed_count = 0
            error_messages = []

            for client_id in message.client_ids:
                success, error = await cls.send_webhook(
                    client_id, 
                    content, 
                    message.metadata or {}
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    error_messages.append(f"Cliente {client_id}: {error}")

            # Atualiza o status final
            status = MessageStatus.SENT if failed_count == 0 else MessageStatus.FAILED
            update_data = {
                "status": status,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "updated_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            }

            if error_messages:
                update_data["error_message"] = "\n".join(error_messages)

            messages_collection.update_one(
                {"_id": message_id},
                {"$set": update_data}
            )

        except Exception as e:
            # Em caso de erro, atualiza o status para falha
            messages_collection.update_one(
                {"_id": message_id},
                {
                    "$set": {
                        "status": MessageStatus.FAILED,
                        "error_message": str(e),
                        "updated_at": datetime.utcnow(),
                        "completed_at": datetime.utcnow()
                    }
                }
            )
