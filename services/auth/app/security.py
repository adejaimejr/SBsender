from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .models import TokenData
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# Configurações
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    if not plain_password or not hashed_password:
        print("Senha ou hash vazios")
        return False
        
    try:
        print(f"Tentando verificar senha com passlib...")
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"Resultado passlib: {result}")
        return result
    except Exception as e:
        print(f"Erro na verificação da senha com passlib: {str(e)}")
        # Fallback para bcrypt direto se passlib falhar
        try:
            print(f"Tentando verificar senha com bcrypt...")
            result = bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
            print(f"Resultado bcrypt: {result}")
            return result
        except Exception as e:
            print(f"Erro no fallback bcrypt: {str(e)}")
            print(f"Senha fornecida: {len(plain_password)} caracteres")
            print(f"Hash armazenado: {len(hashed_password)} caracteres")
            return False

def get_password_hash(password: str) -> str:
    """Gera o hash da senha"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Erro ao gerar hash com passlib: {str(e)}")
        # Fallback para bcrypt direto se passlib falhar
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            print(f"Erro no fallback bcrypt: {str(e)}")
            raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decodifica e valida um token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if username is None:
            raise JWTError("Token inválido")
        return TokenData(username=username, is_admin=is_admin)
    except JWTError:
        raise JWTError("Token inválido")
