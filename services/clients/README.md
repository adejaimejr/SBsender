# Client Service

Este é o serviço de gerenciamento de clientes do SBsender. Ele é responsável por gerenciar os clientes que receberão as notificações via webhook.

## Funcionalidades

- Criar novos clientes (requer admin)
- Listar todos os clientes (requer autenticação)
- Obter detalhes de um cliente específico (requer autenticação)
- Atualizar dados de um cliente (requer admin)
- Deletar um cliente (requer admin)

## Configuração

1. Crie um arquivo `.env` baseado no `.env.example`:
```bash
cp .env.example .env
```

2. Configure as variáveis de ambiente no arquivo `.env`:
- `MONGODB_URL`: URL de conexão com o MongoDB
- `DATABASE_NAME`: Nome do banco de dados
- `AUTH_SERVICE_URL`: URL do serviço de autenticação

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o serviço:
```bash
uvicorn app.main:app --reload
```

## Endpoints

### POST /clients
Cria um novo cliente. Requer autenticação de administrador.

### GET /clients
Lista todos os clientes. Requer autenticação.

### GET /clients/{client_id}
Obtém detalhes de um cliente específico. Requer autenticação.

### PUT /clients/{client_id}
Atualiza os dados de um cliente. Requer autenticação de administrador.

### DELETE /clients/{client_id}
Remove um cliente. Requer autenticação de administrador.

## Modelos de Dados

### Cliente
```json
{
    "name": "string",
    "email": "string",
    "webhook_url": "string",
    "active": true,
    "description": "string (opcional)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

## Autenticação

O serviço utiliza autenticação JWT em conjunto com o serviço de autenticação. Para acessar os endpoints protegidos, é necessário incluir o token JWT no header da requisição:

```
Authorization: Bearer <token>
```
