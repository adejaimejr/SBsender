# 📱 SBsender

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.6.0-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## 🚀 Sobre o Projeto

O SBsender é uma aplicação web desenvolvida para facilitar o envio de mensagens via WhatsApp para números brasileiros. Com uma interface intuitiva e recursos poderosos, o sistema permite importar contatos, gerenciar webhooks e acompanhar o histórico de operações.

## ✨ Funcionalidades

- 📋 **Importação de Contatos**
  - Suporte para importação via texto ou arquivo CSV
  - Validação automática de números brasileiros
  - Feedback sobre números válidos e inválidos

- 🔗 **Gerenciamento de Webhooks**
  - Sistema completo de CRUD para webhooks
  - Integração com MongoDB para persistência
  - Interface intuitiva para gerenciamento

- 📊 **Histórico de Operações**
  - Registro detalhado de importações e envios
  - Filtros por data
  - Visualização clara dos detalhes de cada operação

## 🛠️ Tecnologias Utilizadas

- 🐍 **Python** - Linguagem principal
- 🌐 **Streamlit** - Interface do usuário
- 🗄️ **MongoDB** - Banco de dados
- 📊 **Pandas** - Manipulação de dados
- 🧪 **Unittest** - Testes unitários

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/adejaimejr/SBsender.git
cd SBsender
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv_sbsender
venv_sbsender\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## 🚀 Como Usar

1. Ative o ambiente virtual:
```bash
venv_sbsender\Scripts\activate
```

2. Execute a aplicação:
```bash
streamlit run app.py
```

3. Acesse a interface web em: http://localhost:8501

## 🧪 Testes

Para executar os testes unitários:
```bash
python -m unittest discover tests
```

## 🔒 Segurança

- ⚠️ Nunca compartilhe seu arquivo `.env`
- 🔐 Mantenha suas credenciais seguras
- 📝 Siga as boas práticas de segurança ao configurar webhooks

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Adejaime Junior**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Adejaime%20Junior-blue?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adejaime-junior/)
[![GitHub](https://img.shields.io/badge/GitHub-adejaimejr-181717?style=flat&logo=github&logoColor=white)](https://github.com/adejaimejr)

---

⭐️ Se este projeto te ajudou, considere dar uma estrela!
