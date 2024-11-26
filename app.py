import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime, time
from src.services.contact_service import process_text_input, process_csv_file
from src.services.webhook_service import WebhookService
from src.services.history_service import HistoryService

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="SBsender",
    page_icon="📱",
    layout="wide"
)

# Inicializa os serviços
webhook_service = WebhookService()
history_service = HistoryService()

# Título principal
st.title("📱 SBsender")
st.subheader("Sistema de Envio de Mensagens WhatsApp")

# Sidebar para navegação
menu = st.sidebar.selectbox(
    "Menu",
    ["Importar Contatos", "Webhooks", "Histórico"]
)

if menu == "Importar Contatos":
    st.header("Importar Contatos")
    
    # Lista de webhooks disponíveis
    webhooks = webhook_service.get_all_webhooks()
    webhook_options = {w['title']: w['_id'] for w in webhooks}
    selected_webhook = st.selectbox(
        "Selecione o webhook para envio",
        options=[""] + list(webhook_options.keys()),
        format_func=lambda x: "Selecione um webhook" if x == "" else x
    )
    
    # Opções de importação
    import_option = st.radio(
        "Escolha como deseja importar os contatos:",
        ["Colar números", "Importar CSV"]
    )
    
    if import_option == "Colar números":
        numbers = st.text_area(
            "Cole os números (um por linha ou separados por vírgula)",
            height=200
        )
        if st.button("Processar Números") and numbers:
            valid_numbers, invalid_numbers = process_text_input(numbers)
            
            # Registra no histórico
            webhook_id = webhook_options.get(selected_webhook) if selected_webhook else None
            history_service.register_import(valid_numbers, invalid_numbers, webhook_id)
            
            st.success(f"✅ {len(valid_numbers)} números válidos encontrados")
            if valid_numbers:
                st.write("Números válidos:")
                st.json(valid_numbers)
            
            if invalid_numbers:
                st.error(f"❌ {len(invalid_numbers)} números inválidos encontrados")
                st.write("Números inválidos:")
                st.json(invalid_numbers)
    
    else:
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
        if uploaded_file is not None:
            valid_numbers, invalid_numbers = process_csv_file(uploaded_file)
            
            # Registra no histórico
            webhook_id = webhook_options.get(selected_webhook) if selected_webhook else None
            history_service.register_import(valid_numbers, invalid_numbers, webhook_id)
            
            st.success(f"✅ {len(valid_numbers)} números válidos encontrados")
            if valid_numbers:
                st.write("Números válidos:")
                st.json(valid_numbers)
            
            if invalid_numbers:
                st.error(f"❌ {len(invalid_numbers)} números inválidos encontrados")
                st.write("Números inválidos:")
                st.json(invalid_numbers)

elif menu == "Webhooks":
    st.header("Gerenciar Webhooks")
    
    # Lista de webhooks existentes
    webhooks = webhook_service.get_all_webhooks()
    if webhooks:
        st.subheader("Webhooks Cadastrados")
        for webhook in webhooks:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(f"📌 {webhook['title']}: {webhook['url']}")
            with col2:
                if st.button("Editar", key=f"edit_{webhook['_id']}"):
                    st.session_state.editing_webhook = webhook['_id']
            with col3:
                if st.button("Excluir", key=f"delete_{webhook['_id']}"):
                    if webhook_service.delete_webhook(webhook['_id']):
                        st.success("Webhook excluído com sucesso!")
                        st.rerun()
    
    # Formulário para novo webhook ou edição
    st.subheader("Adicionar/Editar Webhook")
    with st.form("webhook_form"):
        webhook_id = st.session_state.get('editing_webhook', None)
        current_webhook = webhook_service.get_webhook_by_id(webhook_id) if webhook_id else None
        
        webhook_titulo = st.text_input("Título", value=current_webhook['title'] if current_webhook else "")
        webhook_url = st.text_input("URL", value=current_webhook['url'] if current_webhook else "")
        
        submitted = st.form_submit_button("Salvar")
        if submitted and webhook_titulo and webhook_url:
            if webhook_id:
                if webhook_service.update_webhook(webhook_id, webhook_titulo, webhook_url):
                    st.success("Webhook atualizado com sucesso!")
                    del st.session_state.editing_webhook
            else:
                webhook_service.create_webhook(webhook_titulo, webhook_url)
                st.success("Webhook criado com sucesso!")
            st.rerun()

else:  # Histórico
    st.header("Histórico de Envios")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial")
    with col2:
        data_fim = st.date_input("Data Final")
    
    # Converte as datas para datetime
    start_datetime = datetime.combine(data_inicio, time.min)
    end_datetime = datetime.combine(data_fim, time.max)
    
    # Busca o histórico
    historico = history_service.get_history(start_datetime, end_datetime)
    
    if historico:
        for entry in historico:
            with st.expander(f"📝 Importação {entry['created_at'].strftime('%d/%m/%Y %H:%M')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Números Válidos:**", entry['valid_count'])
                    if entry.get('success_count'):
                        st.write("**Enviados com Sucesso:**", entry['success_count'])
                with col2:
                    st.write("**Números Inválidos:**", entry['invalid_count'])
                    if entry.get('failed_count'):
                        st.write("**Falhas no Envio:**", entry['failed_count'])
                
                st.write("**Status:**", "✅ Concluído" if entry['status'] == 'completed' else "⏳ Pendente")
                
                if entry.get('webhook_id'):
                    webhook = webhook_service.get_webhook_by_id(entry['webhook_id'])
                    if webhook:
                        st.write("**Webhook:**", webhook['title'])
    else:
        st.info("Nenhum registro encontrado para o período selecionado.")
