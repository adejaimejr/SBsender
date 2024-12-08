@echo off
echo Iniciando servicos do SBsender...

:: Inicia o Auth Service
start cmd /k "cd services/auth && python -m uvicorn app.main:app --port 8000"

:: Aguarda 2 segundos
timeout /t 2

:: Inicia o Client Service
start cmd /k "cd services/clients && python -m uvicorn app.main:app --port 8001"

:: Aguarda 2 segundos
timeout /t 2

:: Inicia o Webhook Service
start cmd /k "cd services/webhooks && python -m uvicorn app.main:app --port 8002"

:: Aguarda 2 segundos
timeout /t 2

:: Inicia o Message Service
start cmd /k "cd services/messages && python -m uvicorn app.main:app --port 8003"

:: Aguarda 2 segundos
timeout /t 2

:: Inicia o History Service
start cmd /k "cd services/history && python -m uvicorn app.main:app --port 8004"

:: Aguarda 2 segundos
timeout /t 2

:: Inicia o Gateway
start cmd /k "cd services/gateway && python -m uvicorn app.main:app --port 8080"

:: Aguarda 2 segundos
timeout /t 2

:: Inicia o Frontend com Streamlit
start cmd /k "cd frontend && python -m streamlit run app.py"

echo Todos os servicos foram iniciados!
pause
