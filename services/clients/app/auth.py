import os
import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{os.getenv('AUTH_SERVICE_URL')}/token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Verifica o token JWT com o serviço de autenticação"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('AUTH_SERVICE_URL')}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao verificar token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verify_admin(token: str = Depends(oauth2_scheme)):
    """Verifica se o usuário é admin"""
    user = await verify_token(token)
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado"
        )
    return user
