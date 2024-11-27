import streamlit as st
from src.services.contact_service import ContactService
from src.services.webhook_service import WebhookService
from src.services.history_service import HistoryService
from src.services.client_service import ClientService
from src.services.task_service import TaskService
from src.database.mongodb import MongoDB
from datetime import datetime, time
import time as time_module
from src.utils.logger import logger
import hashlib

def main():
    # Inicializa o estado da sessão se necessário
    if 'processed_forms' not in st.session_state:
        st.session_state.processed_forms = set()
    
    st.title("📱 SBsender")
    
    try:
        # Inicializa a conexão com o MongoDB
        mongodb = MongoDB()
        db = mongodb.get_database()
        
        # Inicializa os serviços com uma única conexão
        webhook_service = WebhookService(db)
        client_service = ClientService(db)
        history_service = HistoryService(db)
        contact_service = ContactService(history_service)
        
        # Inicializa e inicia o processamento em background
        if 'task_service' not in st.session_state:
            task_service = TaskService(db)
            task_service.start_processing()
            st.session_state.task_service = task_service
        
        # Menu lateral
        st.sidebar.title("Menu")
        menu = st.sidebar.radio(
            "",
            ["Mensagem via Webhook", "Webhooks", "Clientes", "Histórico de Envios"]
        )
        
        if menu == "Mensagem via Webhook":
            st.header("📨 Enviar Mensagem via Webhook")
            
            # Obtém lista de clientes e webhooks
            clients = client_service.get_all_clients()
            if not clients:
                st.warning("Você precisa cadastrar pelo menos um cliente antes de enviar mensagens.")
                return

            # Seleção do cliente
            client_id = st.selectbox(
                "Selecione o Cliente:",
                options=[c['_id'] for c in clients],
                format_func=lambda x: next((c['name'] for c in clients if c['_id'] == x), ''),
                key="webhook_msg_client"
            )

            # Filtra webhooks pelo cliente selecionado
            webhooks = webhook_service.get_webhooks_by_client(str(client_id)) if client_id else []
            if not webhooks:
                st.warning("Este cliente não possui webhooks cadastrados.")
                return

            webhook_id = st.selectbox(
                "Selecione o Webhook:",
                options=[w['_id'] for w in webhooks],
                format_func=lambda x: next((w['title'] for w in webhooks if w['_id'] == x), '')
            )

            # Seleção do método de importação
            import_method = st.radio(
                "Escolha o método:",
                ["Texto", "Arquivo CSV"]
            )
            
            if import_method == "Texto":
                text_input = st.text_area(
                    "Cole os números aqui (um por linha):",
                    height=200
                )
                
                if st.button("Processar Números"):
                    if text_input:
                        result = contact_service.process_contacts(
                            text_input,
                            webhook_url=next((w['url'] for w in webhooks if w['_id'] == webhook_id), ''),
                            webhook_id=webhook_id,
                            webhook_name=next((w['title'] for w in webhooks if w['_id'] == webhook_id), ''),
                            method='txt'  # Especifica o método como 'txt'
                        )
                        
                        st.write("### Resultado do Processamento")
                        st.write(f"Total processado: {result['total_processed']}")
                        st.write(f"Números válidos: {result['total_valid']}")
                        st.write(f"Números inválidos: {result['total_invalid']}")
                        
                        if result["valid_numbers"]:
                            st.success(f"✅ Números válidos ({len(result['valid_numbers'])}):")
                            st.json(result["valid_numbers"])
                        
                        if result["invalid_numbers"]:
                            st.error(f"❌ Números inválidos ({len(result['invalid_numbers'])}):")
                            st.json(result["invalid_numbers"])
            
            else:  # CSV
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(
                        """
                        <style>
                        .uploadedFile {
                            display: none;
                        }
                        .stFileUploader div:first-child {
                            padding: 20px;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                        }
                        .stFileUploader div:first-child::before {
                            content: "Arraste e solte o arquivo aqui";
                            display: block;
                            margin-bottom: 5px;
                        }
                        .stFileUploader div:first-child::after {
                            content: "ou clique para selecionar";
                            font-size: 0.8em;
                            color: #666;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    uploaded_file = st.file_uploader(
                        " ",  # Espaço em branco para não mostrar o label
                        type="csv",
                        label_visibility="collapsed",
                        help="Arraste ou clique para selecionar um arquivo CSV (máx. 200MB)"
                    )
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)  # Espaço para alinhar com o uploader
                    try:
                        with open("static/modelo_contatos.csv", "r", encoding='utf-8') as f:
                            csv_content = f.read()
                        st.download_button(
                            label="📥 Baixar Modelo CSV",
                            data=csv_content,
                            file_name="modelo_contatos.csv",
                            mime="text/csv",
                            help="Baixe este arquivo para ver como estruturar seus contatos"
                        )
                    except Exception as e:
                        st.error("Arquivo modelo não encontrado. Por favor, crie o arquivo modelo_contatos.csv")
                
                if uploaded_file:
                    # Lê o CSV para mostrar as colunas disponíveis
                    import pandas as pd
                    df = pd.read_csv(uploaded_file)
                    column = st.selectbox("Selecione a coluna com os números:", df.columns)
                    
                    if st.button("Processar CSV"):
                        # Volta o cursor do arquivo para o início
                        uploaded_file.seek(0)
                        result = contact_service.process_csv(
                            uploaded_file.read(),
                            column,
                            webhook_url=next((w['url'] for w in webhooks if w['_id'] == webhook_id), ''),
                            webhook_id=webhook_id,
                            webhook_name=next((w['title'] for w in webhooks if w['_id'] == webhook_id), ''),
                            method='csv'  # Especifica o método como 'csv'
                        )
                        
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.write("### Resultado do Processamento")
                            st.write(f"Total processado: {result['total_processed']}")
                            st.write(f"Números válidos: {result['total_valid']}")
                            st.write(f"Números inválidos: {result['total_invalid']}")
                            
                            if result["valid_numbers"]:
                                st.success(f"✅ Números válidos ({len(result['valid_numbers'])}):")
                                st.json(result["valid_numbers"])
                            
                            if result["invalid_numbers"]:
                                st.error(f"❌ Números inválidos ({len(result['invalid_numbers'])}):")
                                st.json(result["invalid_numbers"])
        
        elif menu == "Webhooks":
            st.header("🔗 Gerenciar Webhooks")
            
            # Obtém lista de clientes para o dropdown
            clients = client_service.get_all_clients()
            if not clients:
                st.warning("Você precisa cadastrar pelo menos um cliente antes de criar webhooks.")
                return

            # Formulário para novo webhook
            with st.form("new_webhook", clear_on_submit=True):
                st.write("### Adicionar Novo Webhook")
                title = st.text_input("Título:")
                url = st.text_input("URL:")
                client_id = st.selectbox(
                    "Cliente:",
                    options=[c['_id'] for c in clients],
                    format_func=lambda x: next((c['name'] for c in clients if c['_id'] == x), '')
                )
                submitted = st.form_submit_button("Adicionar")
                
                if submitted and title and url and client_id:
                    # Cria um hash único para esta submissão
                    form_hash = hashlib.md5(f"{title}{url}{client_id}".encode()).hexdigest()
                    
                    try:
                        if form_hash not in st.session_state.processed_forms:
                            client = next((c for c in clients if c['_id'] == client_id), None)
                            if client:
                                webhook_service.create_webhook(title, url, str(client_id), client['name'])
                                st.session_state.processed_forms.add(form_hash)
                                st.success("Webhook adicionado com sucesso!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao adicionar webhook: {str(e)}")

            # Lista webhooks existentes
            st.write("### Webhooks Cadastrados")
            webhooks = webhook_service.get_all_webhooks()
            
            for webhook in webhooks:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{webhook['title']}**")
                    
                    with col2:
                        st.write(f"Cliente: {webhook.get('client_name', 'N/A')}")
                    
                    with col3:
                        edit_key = f"edit_{webhook['_id']}"
                        if st.button("Editar", key=edit_key):
                            st.session_state.editing_webhook = str(webhook['_id'])
                            st.rerun()
                    
                    with col4:
                        delete_key = f"delete_{webhook['_id']}"
                        if st.button("Excluir", key=delete_key):
                            try:
                                webhook_service.delete_webhook(webhook['_id'])
                                st.success("Webhook excluído com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir webhook: {str(e)}")
                    
                    # Formulário de edição
                    if 'editing_webhook' in st.session_state and st.session_state.editing_webhook == str(webhook['_id']):
                        with st.form(f"edit_webhook_{webhook['_id']}", clear_on_submit=True):
                            new_title = st.text_input("Novo título:", webhook['title'])
                            new_url = st.text_input("Nova URL:", webhook['url'])
                            new_client = st.selectbox(
                                "Cliente:",
                                options=[c['_id'] for c in clients],
                                format_func=lambda x: next((c['name'] for c in clients if c['_id'] == x), ''),
                                index=[i for i, c in enumerate(clients) if c["_id"] == webhook.get('client_id')][0] if webhook.get('client_id') else 0
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Salvar"):
                                    try:
                                        webhook_service.update_webhook(
                                            webhook['_id'],
                                            new_title,
                                            new_url,
                                            new_client,
                                            next((c['name'] for c in clients if c['_id'] == new_client), '')
                                        )
                                        st.success("Webhook atualizado com sucesso!")
                                        del st.session_state.editing_webhook
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar webhook: {str(e)}")
                            
                            with col2:
                                if st.form_submit_button("Cancelar"):
                                    del st.session_state.editing_webhook
                                    st.rerun()
        
        elif menu == "Clientes":
            st.header("👥 Gerenciar Clientes")
            
            # Formulário para novo cliente
            with st.form("new_client", clear_on_submit=True):
                st.write("### Adicionar Novo Cliente")
                name = st.text_input("Nome:")
                description = st.text_area("Descrição (opcional):")
                submitted = st.form_submit_button("Adicionar")
                
                if submitted and name:
                    # Cria um hash único para esta submissão
                    form_hash = hashlib.md5(f"{name}".encode()).hexdigest()
                    
                    try:
                        if form_hash not in st.session_state.processed_forms:
                            logger.info(f"Tentando criar novo cliente - Nome: {name}")
                            client_service.create_client(name, description)
                            logger.info("Cliente criado com sucesso")
                            st.session_state.processed_forms.add(form_hash)
                            st.success("Cliente adicionado com sucesso!")
                            time_module.sleep(1)
                            st.rerun()
                    except Exception as e:
                        logger.error(f"Erro ao criar cliente: {str(e)}")
                        st.error(f"Erro ao adicionar cliente: {str(e)}")
            
            # Lista clientes existentes
            st.write("### Clientes Cadastrados")
            clients = client_service.get_all_clients()
            
            for client in clients:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{client['name']}**")
                        if client.get('description'):
                            st.write(client['description'])
                    
                    with col2:
                        edit_key = f"edit_client_{client['_id']}"
                        if st.button("Editar", key=edit_key):
                            st.session_state.editing_client = str(client['_id'])
                            st.rerun()
                    
                    with col3:
                        delete_key = f"delete_client_{client['_id']}"
                        if st.button("Excluir", key=delete_key):
                            try:
                                client_service.delete_client(client['_id'])
                                st.success("Cliente excluído com sucesso!")
                                time_module.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir cliente: {str(e)}")
                    
                    # Formulário de edição
                    if 'editing_client' in st.session_state and st.session_state.editing_client == str(client['_id']):
                        with st.form(f"edit_client_{client['_id']}", clear_on_submit=True):
                            new_name = st.text_input("Novo nome:", client['name'])
                            new_description = st.text_area("Nova descrição:", client.get('description', ''))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Salvar"):
                                    try:
                                        client_service.update_client(
                                            client['_id'],
                                            new_name,
                                            new_description
                                        )
                                        st.success("Cliente atualizado com sucesso!")
                                        del st.session_state.editing_client
                                        time_module.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar cliente: {str(e)}")
                            
                            with col2:
                                if st.form_submit_button("Cancelar"):
                                    del st.session_state.editing_client
                                    st.rerun()
        
        else:  # Histórico
            st.header("📋 Histórico de Envios")
            
            # Obtém lista de clientes para filtro
            clients = client_service.get_all_clients()
            
            # Filtro por cliente
            client_filter = st.selectbox(
                "Filtrar por Cliente:",
                options=[None] + [c['_id'] for c in clients],
                format_func=lambda x: "Todos os Clientes" if x is None else next((c['name'] for c in clients if c['_id'] == x), ''),
                key="history_client_filter"
            )

            # Busca histórico com filtro de cliente
            history_data = contact_service.get_history(client_id=str(client_filter) if client_filter else None)
            
            if history_data:
                for entry in history_data:
                    entry = history_service.format_history_entry(entry)
                    with st.expander(entry['display_title']):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total", entry['total_processed'])
                        with col2:
                            st.metric("Válidos", len(entry['valid_numbers']))
                        with col3:
                            st.metric("Inválidos", len(entry['invalid_numbers']))
                        with col4:
                            st.metric("Método", "CSV" if entry['method'] == 'csv' else "Texto")
                        
                        if entry["valid_numbers"]:
                            st.success(f"✅ Números válidos ({len(entry['valid_numbers'])}):")
                            st.json(entry["valid_numbers"])
                        
                        if entry["invalid_numbers"]:
                            st.error(f"❌ Números inválidos ({len(entry['invalid_numbers'])}):")
                            st.json(entry["invalid_numbers"])
            else:
                st.info("Nenhum envio registrado ainda.")
                return
            
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        st.info("Verifique se as configurações do MongoDB no arquivo .env estão corretas")

if __name__ == "__main__":
    main()
