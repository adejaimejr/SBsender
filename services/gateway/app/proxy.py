import httpx
from fastapi import Request
from typing import Optional
from .config import settings

async def proxy_request(
    request: Request,
    target_url: str,
    path: str,
    exclude_headers: Optional[list] = None
) -> httpx.Response:
    """
    Encaminha uma requisição para o serviço de destino
    """
    if exclude_headers is None:
        exclude_headers = []
    
    # Prepara os headers
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in exclude_headers
    }
    
    # Prepara a URL de destino
    url = f"{target_url.rstrip('/')}/{path.lstrip('/')}"
    
    # Obtém o corpo da requisição
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            follow_redirects=True
        )
        
        return response

class ServiceProxy:
    def __init__(self, service_url: str, prefix: str):
        self.service_url = service_url
        self.prefix = prefix
    
    async def handle_request(self, request: Request, path: str):
        """
        Manipula uma requisição para um serviço específico
        """
        # Remove o prefixo do path
        service_path = path.replace(self.prefix, "", 1)
        
        # Encaminha a requisição
        response = await proxy_request(
            request,
            self.service_url,
            service_path,
            exclude_headers=["host"]
        )
        
        return response

# Cria os proxies para cada serviço
auth_proxy = ServiceProxy(settings.AUTH_SERVICE_URL, "/auth")
client_proxy = ServiceProxy(settings.CLIENT_SERVICE_URL, "/clients")
webhook_proxy = ServiceProxy(settings.WEBHOOK_SERVICE_URL, "/webhooks")
message_proxy = ServiceProxy(settings.MESSAGE_SERVICE_URL, "/messages")
history_proxy = ServiceProxy(settings.HISTORY_SERVICE_URL, "/history")
