import streamlit as st
from src.services.contact_service import ContactService
from src.services.webhook_service import WebhookService
from src.services.history_service import HistoryService
from src.database.mongodb import get_database

def main():
    st.set_page_config(
        page_title="SBsender",
        page_icon="📱",
        layout="wide"
    )
    
    st.title("📱 SBsender")
    
    # Inicializa os serviços
    db = get_database()
    history_service = HistoryService(db)
    contact_service = ContactService(history_service)
    webhook_service = WebhookService(db)
    
    # Menu lateral
    menu = st.sidebar.selectbox(
        "Menu",
        ["Importar Contatos", "Webhooks", "Histórico"]
    )
    
    if menu == "Importar Contatos":
        st.header("📥 Importar Contatos")
        
        # Seleção do método de importação
        import_method = st.radio(
            "Escolha o método de importação:",
            ["Texto", "Arquivo CSV"]
        )
        
        # Campo para mensagem
        message = st.text_area(
            "Mensagem a ser enviada:",
            help="Digite a mensagem que será enviada para os contatos"
        )
        
        # Seleção do webhook
        webhooks = webhook_service.list_webhooks()
        webhook_options = {w["title"]: w["url"] for w in webhooks}
        webhook_options["Padrão"] = None
        
        selected_webhook = st.selectbox(
            "Webhook para envio:",
            options=list(webhook_options.keys()),
            help="Selecione o webhook que será usado para enviar as mensagens"
        )
        
        webhook_url = webhook_options[selected_webhook]
        
        if import_method == "Texto":
            text_input = st.text_area(
                "Cole os números aqui (um por linha):",
                height=200
            )
            
            if st.button("Processar Números"):
                if text_input:
                    result = contact_service.process_contacts(text_input, webhook_url)
                    
                    st.write("### Resultado do Processamento")
                    st.write(f"Total processado: {result['total_processed']}")
                    st.write(f"Números válidos: {result['total_valid']}")
                    st.write(f"Números inválidos: {result['total_invalid']}")
                    
                    if result["valid_numbers"]:
                        st.success(f"✅ Números válidos ({len(result['valid_numbers'])}):")
                        st.json(result["valid_numbers"])
                        
                        if message and st.button("Enviar Mensagem"):
                            send_result = contact_service.send_messages(
                                result["valid_numbers"],
                                message,
                                webhook_url
                            )
                            
                            if send_result["success"]:
                                st.success(send_result["message"])
                            else:
                                st.error(send_result["message"])
                    
                    if result["invalid_numbers"]:
                        st.error(f"❌ Números inválidos ({len(result['invalid_numbers'])}):")
                        st.json(result["invalid_numbers"])
                        
        else:  # CSV
            uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
            
            if uploaded_file:
                # Lê o CSV para mostrar as colunas disponíveis
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                column = st.selectbox("Selecione a coluna com os números:", df.columns)
                
                if st.button("Processar CSV"):
                    # Volta o cursor do arquivo para o início
                    uploaded_file.seek(0)
                    result = contact_service.process_csv(uploaded_file.read(), column, webhook_url)
                    
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
                            
                            if message and st.button("Enviar Mensagem"):
                                send_result = contact_service.send_messages(
                                    result["valid_numbers"],
                                    message,
                                    webhook_url
                                )
                                
                                if send_result["success"]:
                                    st.success(send_result["message"])
                                else:
                                    st.error(send_result["message"])
                        
                        if result["invalid_numbers"]:
                            st.error(f"❌ Números inválidos ({len(result['invalid_numbers'])}):")
                            st.json(result["invalid_numbers"])
    
    elif menu == "Webhooks":
        st.header("🔗 Gerenciar Webhooks")
        
        # Formulário para novo webhook
        with st.form("new_webhook"):
            st.write("### Adicionar Novo Webhook")
            title = st.text_input("Título:")
            url = st.text_input("URL:")
            
            if st.form_submit_button("Adicionar"):
                if title and url:
                    webhook_service.add_webhook(title, url)
                    st.success("Webhook adicionado com sucesso!")
                    st.rerun()
        
        # Lista webhooks existentes
        st.write("### Webhooks Cadastrados")
        webhooks = webhook_service.list_webhooks()
        
        for webhook in webhooks:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{webhook['title']}**  \n{webhook['url']}")
            
            with col2:
                if st.button("Editar", key=f"edit_{webhook['_id']}"):
                    st.session_state.editing_webhook = webhook['_id']
            
            with col3:
                if st.button("Excluir", key=f"delete_{webhook['_id']}"):
                    webhook_service.delete_webhook(webhook['_id'])
                    st.success("Webhook excluído com sucesso!")
                    st.rerun()
            
            # Formulário de edição
            if hasattr(st.session_state, 'editing_webhook') and st.session_state.editing_webhook == webhook['_id']:
                with st.form(f"edit_webhook_{webhook['_id']}"):
                    new_title = st.text_input("Novo título:", webhook['title'])
                    new_url = st.text_input("Nova URL:", webhook['url'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Salvar"):
                            webhook_service.update_webhook(
                                webhook['_id'],
                                new_title,
                                new_url
                            )
                            st.success("Webhook atualizado com sucesso!")
                            del st.session_state.editing_webhook
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("Cancelar"):
                            del st.session_state.editing_webhook
                            st.rerun()
    
    else:  # Histórico
        st.header("📊 Histórico de Operações")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data inicial")
        with col2:
            end_date = st.date_input("Data final")
        
        if st.button("Buscar"):
            records = history_service.get_records(start_date, end_date)
            
            for record in records:
                with st.expander(f"{record['timestamp']} - {record['operation']}"):
                    st.json(record['details'])

if __name__ == "__main__":
    main()
