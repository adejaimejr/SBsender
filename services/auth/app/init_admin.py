import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import sys
from models import UserProfile

load_dotenv()

# Configurações do MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("Erro: MONGODB_URI não está definido no arquivo .env")
    sys.exit(1)

DATABASE_NAME = os.getenv("DATABASE_NAME", "sbsender_auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def init_admin():
    try:
        # Conectar ao MongoDB
        print(f"Conectando ao MongoDB em {MONGODB_URI}...")
        client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Testa a conexão
        await client.admin.command('ping')
        print("Conectado ao MongoDB com sucesso!")
        
        db = client[DATABASE_NAME]
        print(f"Usando banco de dados: {DATABASE_NAME}")
        
        # Verificar se a coleção de usuários existe
        collections = await db.list_collection_names()
        if "users" not in collections:
            await db.create_collection("users")
            print("Coleção de usuários criada com sucesso!")
        
        # Verificar se já existe um usuário admin
        admin = await db.users.find_one({"username": "admin"})
        
        if not admin:
            # Criar usuário admin
            admin_user = {
                "username": "admin",
                "email": "admin@sbsender.com",
                "password": get_password_hash("admin123"),
                "profile": UserProfile.ADMIN,
                "is_active": True,
                "is_admin": True,
                "avatar_emoji": "👑",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            print("Criando novo usuário admin...")
            result = await db.users.insert_one(admin_user)
            
            if result.inserted_id:
                print(f"Usuário admin criado com sucesso! ID: {result.inserted_id}")
                # Verifica se foi realmente criado
                created_user = await db.users.find_one({"_id": result.inserted_id})
                print(f"Dados do usuário criado: {created_user}")
                print("\nVocê pode fazer login com:")
                print("Username: admin")
                print("Password: admin123")
            else:
                print("Falha ao criar usuário admin!")
        else:
            print("Usuário admin já existe!")
            
        # Fechar conexão
        client.close()
        print("Conexão com MongoDB fechada!")
        
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_admin())
