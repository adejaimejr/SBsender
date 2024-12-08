# SBsender - Sistema de Envio de Webhooks

## Descrição
O SBsender é um sistema de microserviços para gerenciamento e envio de webhooks, permitindo o envio de mensagens para múltiplos endpoints de forma confiável e escalável.

## Arquitetura
O sistema é composto por vários microserviços:

1. **API Gateway** (Porta 8080)
   - Ponto central de acesso aos serviços
   - Roteamento de requisições
   - Monitoramento de saúde dos serviços

2. **Webhook Service** (Porta 8002)
   - Gerenciamento de webhooks
   - Configuração de endpoints
   - Sistema de retry para falhas

3. **Message Service** (Porta 8003)
   - Processamento de mensagens
   - Envio para webhooks
   - Gerenciamento de status

4. **History Service** (Porta 8001)
   - Registro de eventos
   - Histórico de mensagens
   - Métricas e análises

5. **Frontend** (Porta 8501)
   - Interface web em Streamlit
   - Dashboard de métricas
   - Gerenciamento de webhooks e mensagens

## Requisitos
- Python 3.8+
- MongoDB
- Dependências específicas de cada serviço (ver requirements.txt em cada pasta)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd SBsender
```

2. Configure o MongoDB e crie um banco de dados para o projeto

3. Em cada serviço (gateway, webhooks, messages, history, frontend):
   ```bash
   cd services/[SERVICE_NAME]
   pip install -r requirements.txt
   cp .env.example .env
   # Configure as variáveis em .env
   ```

## Execução

1. Inicie o MongoDB

2. Execute o script de inicialização:
```bash
start_services.bat
```

Ou inicie cada serviço manualmente:
```bash
# History Service
cd services/history
python -m uvicorn app.main:app --port 8001

# Webhook Service
cd services/webhooks
python -m uvicorn app.main:app --port 8002

# Message Service
cd services/messages
python -m uvicorn app.main:app --port 8003

# API Gateway
cd services/gateway
python -m uvicorn app.main:app --port 8080

# Frontend
cd frontend
streamlit run app.py
```

## Acessando os Serviços

- Frontend: http://localhost:8501
- API Gateway: http://localhost:8080
- Documentação da API: http://localhost:8080/docs

## Estrutura do Projeto
```
SBsender/
├── services/
│   ├── gateway/
│   ├── webhooks/
│   ├── messages/
│   └── history/
├── frontend/
├── tests/
└── start_services.bat
```

## Desenvolvimento

Para contribuir com o projeto:

1. Crie um branch para sua feature
2. Faça suas alterações
3. Execute os testes
4. Envie um pull request

## Testes

Execute os testes em cada serviço:
```bash
cd services/[SERVICE_NAME]
pytest
```

## Monitoramento

- Logs são gerados em cada serviço
- Métricas disponíveis no dashboard
- Healthcheck via API Gateway

## Licença
[Tipo de Licença]
