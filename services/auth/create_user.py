import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8080")

def create_user(username, email, password):
    """Cria um novo usuário"""
    try:
        response = requests.post(
            f"{API_GATEWAY_URL}/auth/users",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        
        if response.status_code == 200:
            print(f"Usuário {username} criado com sucesso!")
            return True
        else:
            print(f"Erro ao criar usuário: {response.json()['detail']}")
            return False
    except Exception as e:
        print(f"Erro ao criar usuário: {str(e)}")
        return False

def main():
    print("=== Criação de Usuário ===")
    
    while True:
        username = input("Digite o username (ou 'sair' para terminar): ")
        if username.lower() == 'sair':
            break
            
        email = input("Digite o email: ")
        password = input("Digite a senha: ")
        
        if create_user(username, email, password):
            print("\nUsuário criado com sucesso!")
        else:
            print("\nFalha ao criar usuário. Tente novamente.")
        
        print("\n---")

if __name__ == "__main__":
    main()
