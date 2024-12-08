import os
import aiohttp
import asyncio
from datetime import datetime
from .models import Webhook, WebhookStatus
from .database import Database

class WebhookSender:
    @staticmethod
    async def send_webhook(webhook: Webhook, client_url: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    client_url,
                    json={
                        "event_type": webhook.event_type,
                        "payload": webhook.payload,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ) as response:
                    return response.status in (200, 201, 202)
        except Exception as e:
            return False

    @staticmethod
    async def process_webhook(webhook_id: str):
        webhooks_collection = Database.get_webhooks_collection()
        webhook_data = webhooks_collection.find_one({"_id": webhook_id})
        
        if not webhook_data:
            return
        
        webhook = Webhook(**webhook_data)
        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        retry_delay = int(os.getenv("RETRY_DELAY_SECONDS", "60"))
        
        # Obter URL do cliente do serviço de clientes
        # TODO: Implementar chamada real ao serviço de clientes
        client_url = "http://example.com/webhook"  # Placeholder
        
        success = await WebhookSender.send_webhook(webhook, client_url)
        
        if success:
            webhooks_collection.update_one(
                {"_id": webhook_id},
                {
                    "$set": {
                        "status": WebhookStatus.SUCCESS,
                        "last_attempt": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            retry_count = webhook.retry_count + 1
            if retry_count >= max_retries:
                status = WebhookStatus.FAILED
            else:
                status = WebhookStatus.RETRYING
                # Agendar nova tentativa
                asyncio.create_task(
                    WebhookSender.retry_webhook(webhook_id, retry_delay)
                )
            
            webhooks_collection.update_one(
                {"_id": webhook_id},
                {
                    "$set": {
                        "status": status,
                        "retry_count": retry_count,
                        "last_attempt": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )

    @staticmethod
    async def retry_webhook(webhook_id: str, delay: int):
        await asyncio.sleep(delay)
        await WebhookSender.process_webhook(webhook_id)
