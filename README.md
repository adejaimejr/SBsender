# SBsender

Sistema para envio de mensagens via WhatsApp para números brasileiros utilizando Streamlit.

## Funcionalidades

- Importação de contatos via texto ou CSV
- Correção automática de números para formato WhatsApp BR
- Painel administrativo com histórico de envios
- Cadastro e gestão de webhooks
- Integração com webhook para disparo de mensagens

## Requisitos

- Python 3.8+
- MongoDB
- Dependências listadas em requirements.txt

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
   - Copie o arquivo `.env.example` para `.env`
   - Ajuste as configurações conforme necessário

5. Execute o aplicativo:
```bash
streamlit run app.py
```

## Estrutura do Projeto

```
SBsender/
├── app.py                 # Aplicação principal Streamlit
├── src/
│   ├── database/         # Configuração e operações do MongoDB
│   ├── services/         # Lógica de negócios
│   └── utils/            # Funções auxiliares
├── tests/                # Testes unitários
├── .env                  # Variáveis de ambiente
└── requirements.txt      # Dependências do projeto
```

## Executando os Testes

Para executar os testes unitários:

```bash
python -m unittest discover tests
```

## Uso

1. **Importação de Contatos:**
   - Acesse a página "Importar Contatos"
   - Escolha entre colar números ou importar CSV
   - Selecione um webhook para envio (opcional)
   - Os números serão validados e formatados automaticamente

2. **Gestão de Webhooks:**
   - Acesse a página "Webhooks"
   - Cadastre novos webhooks com título e URL
   - Edite ou exclua webhooks existentes

3. **Histórico:**
   - Acesse a página "Histórico"
   - Filtre por período
   - Visualize detalhes de cada importação/envio

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature
3. Faça commit das alterações
4. Faça push para a branch
5. Abra um Pull Request

## Segurança

- Nunca compartilhe seu arquivo `.env` ou credenciais
- Mantenha o MongoDB protegido por senha
- Valide e sanitize todas as URLs de webhook antes de usar
