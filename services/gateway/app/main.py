from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import httpx

from .proxy import (
    auth_proxy,
    client_proxy,
    webhook_proxy,
    message_proxy,
    history_proxy
)

app = FastAPI(title="API Gateway", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_route(request: Request, path: str):
    """Rotas do serviço de autenticação"""
    try:
        response = await auth_proxy.handle_request(request, f"/auth/{path}")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.api_route("/clients/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def client_route(request: Request, path: str):
    """Rotas do serviço de clientes"""
    try:
        response = await client_proxy.handle_request(request, f"/clients/{path}")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.api_route("/webhooks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def webhook_route(request: Request, path: str):
    """Rotas do serviço de webhooks"""
    try:
        response = await webhook_proxy.handle_request(request, f"/webhooks/{path}")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.api_route("/messages/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def message_route(request: Request, path: str):
    """Rotas do serviço de mensagens"""
    try:
        response = await message_proxy.handle_request(request, f"/messages/{path}")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.api_route("/history/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def history_route(request: Request, path: str):
    """Rotas do serviço de histórico"""
    try:
        response = await history_proxy.handle_request(request, f"/history/{path}")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/health")
async def health_check():
    """Verifica a saúde do gateway e dos serviços"""
    health = {
        "gateway": "healthy",
        "services": {}
    }
    
    services = {
        "auth": auth_proxy,
        "client": client_proxy,
        "webhook": webhook_proxy,
        "message": message_proxy,
        "history": history_proxy
    }
    
    async with httpx.AsyncClient() as client:
        for name, proxy in services.items():
            try:
                response = await client.get(f"{proxy.service_url}/health")
                health["services"][name] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
            except:
                health["services"][name] = "unreachable"
    
    return health
