from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List
from bson import ObjectId

from .models import User, UserCreate, UserUpdate, Token
from .database import Database
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Auth Service", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Obtém o usuário atual baseado no token JWT"""
    try:
        token_data = decode_token(token)
        users_collection = await Database.get_users_collection()
        user = await users_collection.find_one({"username": token_data.username})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return User(**user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login do usuário"""
    try:
        users_collection = await Database.get_users_collection()
        print(f"Tentando login para usuário: {form_data.username}")
        user = await users_collection.find_one({"username": form_data.username})
        
        if not user:
            print(f"Usuário não encontrado: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        print(f"Usuário encontrado, verificando senha...")
        if verify_password(form_data.password, user["password"]):
            if not user.get("is_active", False):
                print(f"Usuário inativo: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário aguardando aprovação do administrador",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            print(f"Senha correta, gerando token...")
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user["username"], "is_admin": user.get("is_admin", False)},
                expires_delta=access_token_expires
            )
            print(f"Login bem sucedido para: {form_data.username}")
            return {"access_token": access_token, "token_type": "bearer"}
        
        print(f"Senha incorreta para usuário: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro interno no login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}",
        )

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Cria um novo usuário"""
    users_collection = await Database.get_users_collection()
    
    # Verifica se já existe usuário com mesmo username ou email
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe"
        )
    
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já existe"
        )
    
    # Cria o usuário
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    result = await users_collection.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    
    return User(**user_dict)

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Retorna o usuário atual"""
    return current_user

@app.get("/users", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user)):
    """Lista todos os usuários (requer admin)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado"
        )
    
    users_collection = await Database.get_users_collection()
    users = await users_collection.find()
    users_list = []
    async for user in users:
        user["id"] = str(user["_id"])
        users_list.append(user)
    
    return users_list

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Atualiza um usuário"""
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado"
        )
    
    users_collection = await Database.get_users_collection()
    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user["_id"])
    
    return User(**updated_user)

@app.put("/users/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Atualiza as configurações do usuário atual"""
    try:
        users_collection = await Database.get_users_collection()
        update_data = user_update.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum dado para atualizar"
            )
        
        result = await users_collection.update_one(
            {"username": current_user.username},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Retorna o usuário atualizado
        updated_user = await users_collection.find_one({"username": current_user.username})
        return User(**updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Deleta um usuário (requer admin)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado"
        )
    
    users_collection = await Database.get_users_collection()
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return {"message": "Usuário deletado com sucesso"}

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste para verificar o serviço"""
    try:
        # Testa a conexão com o MongoDB
        users_collection = await Database.get_users_collection()
        user = await users_collection.find_one({"username": "admin"})
        
        return {
            "status": "ok",
            "message": "Serviço funcionando",
            "mongodb_connection": "ok",
            "user_found": user is not None,
            "user_data": {
                "username": user["username"] if user else None,
                "is_admin": user.get("is_admin") if user else None
            } if user else None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": str(type(e))
        }
