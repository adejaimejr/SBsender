@echo off
echo Instalando dependencias do servico de autenticacao...
pip install -r requirements.txt

echo Criando usuario admin inicial...
python app/init_admin.py

echo Configuracao concluida!
pause
