import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import pandas as pd
import io

# Configuração da página
st.set_page_config(
    page_title="SBsender",
    page_icon="💬",
    layout="wide"
)

load_dotenv()

# URLs dos serviços
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8080")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8001")

def check_password_requirements(password):
    """Verifica quais requisitos da senha foram atendidos"""
    requirements = {
        'length': len(password) >= 8,
        'upper': any(c.isupper() for c in password),
        'lower': any(c.islower() for c in password),
        'digit': any(c.isdigit() for c in password),
        'special': any(c in "!@#$%^&*(),.?-_=+" for c in password)
    }
    all_met = all(requirements.values())
    return requirements, all_met

def validate_password_strength(password):
    """Valida a força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    if not any(c.isupper() for c in password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    if not any(c.islower() for c in password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    if not any(c.isdigit() for c in password):
        return False, "A senha deve conter pelo menos um número"
    if not any(c in "!@#$%^&*(),.?-_=+" for c in password):
        return False, "A senha deve conter pelo menos um caractere especial (!@#$%^&*(),.?-_=+)"
    return True, ""

def show_login():
    """Mostra a tela de login ou cadastro"""
    # Inicializa o estado se necessário
    if 'show_login_form' not in st.session_state:
        st.session_state.show_login_form = True
        st.session_state.form_reset_counter = 0
        st.session_state.show_success = False
        st.session_state.registration_success = False

    if 'show_success' not in st.session_state:
        st.session_state.show_success = False

    if 'registration_success' not in st.session_state:
        st.session_state.registration_success = False

    if 'form_reset_counter' not in st.session_state:
        st.session_state.form_reset_counter = 0

    if 'show_login_form' not in st.session_state:
        st.session_state.show_login_form = True  # Exibir o formulário de login por padrão

    st.markdown('<div class="login-header"><h3>💬 SBsender</h3></div>', unsafe_allow_html=True)

    if st.session_state.show_login_form:
        # Formulário de Login
        st.markdown('<div class="login-header">Bem-vindo ao SBsender</div>', unsafe_allow_html=True)

        # Campos para login com chaves dinâmicas
        key_login_username = f'login_username_{st.session_state.form_reset_counter}'
        key_login_password = f'login_password_{st.session_state.form_reset_counter}'

        username = st.text_input("Nome de usuário", placeholder="Digite seu nome de usuário", key=key_login_username)
        password = st.text_input("Senha", type="password", placeholder="Digite sua senha", key=key_login_password)
        login_button = st.button("Entrar", key='login_button')

        # Ação de login
        if login_button:
            # Verificar se o username contém espaços
            if ' ' in username:
                st.error("O nome de usuário não pode conter espaços em branco")
            elif not username or not password:
                st.error("Por favor, preencha todos os campos")
            else:
                try:
                    print(f"Tentando login para usuário: {username.lower()}")
                    print(f"URL da requisição: {AUTH_SERVICE_URL}/auth/token")
                    
                    # Enviar como form-data conforme esperado pelo OAuth2
                    response = requests.post(
                        f"{AUTH_SERVICE_URL}/auth/token",
                        data={"username": username.lower(), "password": password}
                    )
                    
                    print(f"Status code: {response.status_code}")
                    print(f"Resposta: {response.text}")
                    
                    if response.status_code == 200:
                        st.session_state['token'] = response.json()['access_token']
                        st.session_state['authenticated'] = True
                        # Incrementa o contador para resetar os campos
                        st.session_state.form_reset_counter += 1
                        st.experimental_rerun()
                    else:
                        error_msg = response.json().get('detail', '')
                        print(f"Erro recebido: {error_msg}")
                        if error_msg == 'Inactive user':
                            st.error("Sua conta ainda não foi ativada. Por favor, aguarde a aprovação do administrador")
                        else:
                            st.error("Usuário ou senha incorretos")
                except Exception as e:
                    print(f"Erro na requisição: {str(e)}")
                    st.error("Erro de conexão. Por favor, tente novamente mais tarde.")

        # Link para cadastro
        st.write("Ainda não possui uma conta?")
        if st.button("Criar nova conta", key='go_to_register'):
            st.session_state.show_login_form = False
            st.session_state.form_reset_counter += 1
            st.experimental_rerun()
    else:
        # Formulário de Cadastro
        st.markdown('<div class="login-header">Criar nova conta</div>', unsafe_allow_html=True)

        # Mostrar mensagem de sucesso se o cadastro foi realizado
        if st.session_state.registration_success:
            st.success("Cadastro realizado com sucesso! Em breve você receberá um e-mail quando sua conta for aprovada.")
            st.session_state.registration_success = False  # Reseta o flag após mostrar a mensagem

        # Campos de cadastro com chaves dinâmicas
        key_username = f'register_username_{st.session_state.form_reset_counter}'
        key_email = f'register_email_{st.session_state.form_reset_counter}'
        key_password = f'password_input_{st.session_state.form_reset_counter}'
        key_confirm_password = f'confirm_password_input_{st.session_state.form_reset_counter}'

        new_username = st.text_input("Nome de usuário", placeholder="Escolha seu nome de usuário", key=key_username)
        new_email = st.text_input("E-mail", placeholder="Digite seu e-mail", key=key_email)

        # Verificar se o username contém espaços
        if ' ' in new_username:
            st.error("O nome de usuário não pode conter espaços em branco")

        # Campo de senha com verificação em tempo real
        new_password = st.text_input(
            "Senha",
            type="password",
            placeholder="Crie sua senha",
            key=key_password
        )

        # Campo de confirmação de senha
        confirm_password = st.text_input(
            "Confirmar Senha",
            type="password",
            placeholder="Digite a senha novamente",
            key=key_confirm_password
        )

        # Mostrar os requisitos da senha apenas se não forem atendidos
        requirements, all_requirements_met = check_password_requirements(new_password)
        if not all_requirements_met and new_password:
            # Define as cores e símbolos baseado nos requisitos
            colors = {True: "#00ff00", False: "gray"}
            symbols = {True: "✓", False: "•"}

            # Mostra os requisitos da senha com marcadores visuais
            st.markdown(f"""
                <style>
                .password-requirements {{
                    font-size: 0.9em;
                    margin-top: -1em;
                    margin-bottom: 1em;
                }}
                </style>
                <div class="password-requirements">
                    <small>
                    Requisitos para uma senha segura:
                    <ul>
                        <li style='color: {colors[requirements["length"]]}'>{symbols[requirements["length"]]} Mínimo de 8 caracteres</li>
                        <li style='color: {colors[requirements["upper"]]}'>{symbols[requirements["upper"]]} Uma letra maiúscula</li>
                        <li style='color: {colors[requirements["lower"]]}'>{symbols[requirements["lower"]]} Uma letra minúscula</li>
                        <li style='color: {colors[requirements["digit"]]}'>{symbols[requirements["digit"]]} Um número</li>
                        <li style='color: {colors[requirements["special"]]}'>{symbols[requirements["special"]]} Um caractere especial (!@#$%^&*(),.?-_=+)</li>
                    </ul>
                    </small>
                </div>
            """, unsafe_allow_html=True)

        register_button = st.button("Criar conta", key='register_button')

        # Ação de cadastro
        if register_button:
            if not new_username or not new_email or not new_password or not confirm_password:
                st.error("Por favor, preencha todos os campos")
            # Verificar se o username contém espaços
            elif ' ' in new_username:
                st.error("O nome de usuário não pode conter espaços em branco")
            # Valida o email
            elif '@' not in new_email or '.' not in new_email:
                st.error("Por favor, insira um endereço de e-mail válido")
            else:
                # Valida a força da senha
                is_strong, password_error = validate_password_strength(new_password)
                if not is_strong:
                    st.error(password_error)
                elif new_password != confirm_password:
                    st.error("As senhas digitadas não são iguais")
                else:
                    try:
                        # Enviar username e email em minúsculas
                        response = requests.post(
                            f"{API_GATEWAY_URL}/auth/users",
                            json={
                                "username": new_username.lower(),
                                "email": new_email.lower(),
                                "password": new_password,
                                "profile": "cliente",
                                "is_active": False,
                                "is_admin": False,
                                "avatar_emoji": "👤"
                            }
                        )
                        if response.status_code == 200:
                            # Seta o flag de sucesso do cadastro
                            st.session_state.registration_success = True
                            # Incrementa o contador para resetar os campos
                            st.session_state.form_reset_counter += 1
                            st.experimental_rerun()
                        else:
                            error_detail = response.json().get('detail', error_detail)
                            st.error(f"Erro ao realizar cadastro: {error_detail}")
                    except Exception as e:
                        st.error(f"Erro ao realizar cadastro: {str(e)}")

        # Link para login (apenas na tela de cadastro)
        if not st.session_state.show_login_form:
            st.write("Já tem uma conta?")
            if st.button("Voltar para login", key='back_to_login'):
                # Limpar todos os estados relevantes
                for key in list(st.session_state.keys()):
                    if key not in ['authenticated', 'token']:
                        del st.session_state[key]
                st.session_state.show_login_form = True
                st.session_state.form_reset_counter = 0
                st.experimental_rerun()

def get_current_user():
    """Obtém informações do usuário atual"""
    if st.session_state.get('token'):
        try:
            response = requests.get(
                f"{AUTH_SERVICE_URL}/auth/users/me",
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # Garante que o avatar_emoji está presente nos dados do usuário
                if 'avatar_emoji' not in user_data:
                    user_data['avatar_emoji'] = "👤"  # Emoji padrão caso não exista
                return user_data
        except Exception as e:
            print(f"Erro ao obter informações do usuário: {str(e)}")
            return None
    return None

# Funções de callback para gerenciamento de formulários
def reset_form_data():
    """Reseta os dados do formulário no session_state"""
    keys_to_reset = ['client_name', 'client_description', 'client_limit']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def process_csv_file(file):
    """Processa o arquivo CSV e retorna uma lista de contatos"""
    try:
        # Lê o CSV
        df = pd.read_csv(file)
        
        # Verifica as colunas necessárias
        required_columns = {'nome', 'numero'}
        if not required_columns.issubset(df.columns):
            return None, "O arquivo CSV deve conter as colunas 'nome' e 'numero'"
        
        # Processa os contatos
        contacts = []
        for _, row in df.iterrows():
            # Garante que o número está no formato string e remove caracteres não numéricos
            numero = str(row['numero']).strip()
            numero = ''.join(filter(str.isdigit, numero))
            
            # Só adiciona se tiver nome e número válido
            nome = str(row['nome']).strip()
            if nome and numero:
                contact = {
                    "name": nome,
                    "phone": numero
                }
                # Adiciona grupo se existir
                if 'grupo' in df.columns:
                    grupo = str(row['grupo']).strip()
                    if grupo:
                        contact["group"] = grupo
                contacts.append(contact)
        
        if not contacts:
            return None, "Nenhum contato válido encontrado no arquivo"
        
        return contacts, None
    except Exception as e:
        return None, f"Erro ao processar CSV: {str(e)}"

def handle_client_submit():
    """Callback para lidar com o submit do formulário de cliente"""
    if not st.session_state.client_name:
        st.error("O nome do cliente é obrigatório!")
        return

    try:
        # Prepara os dados básicos do cliente
        client_data = {
            "name": st.session_state.client_name,
            "description": st.session_state.client_description if st.session_state.client_description else None,
            "daily_limit": st.session_state.client_limit,
            "contacts": []
        }
        
        contacts_processed = 0
        # Processa o arquivo CSV se fornecido
        if st.session_state.client_contacts is not None:
            with st.spinner('Processando contatos...'):
                contacts, error = process_csv_file(st.session_state.client_contacts)
                if error:
                    st.error(error)
                    return
                
                if contacts:
                    client_data["contacts"] = contacts
                    contacts_processed = len(contacts)
                else:
                    st.warning("Nenhum contato válido encontrado no arquivo CSV")
                    return
        
        # Envia para a API
        with st.spinner('Cadastrando cliente...'):
            response = requests.post(
                f"{API_GATEWAY_URL}/clients",
                headers={"Authorization": f"Bearer {st.session_state['token']}"},
                json=client_data
            )
            
            if response.status_code in [200, 201]:
                st.session_state.show_success_message = True
                st.session_state.contacts_processed = contacts_processed
                reset_form_data()
            else:
                error_detail = response.json().get('detail', "Erro desconhecido")
                st.error(f"Erro ao cadastrar cliente: {error_detail}")
    except Exception as e:
        st.error(f"Erro ao cadastrar cliente: {str(e)}")

def handle_update_contacts(client_id: str, client_name: str):
    """Atualiza os contatos de um cliente via CSV"""
    try:
        if 'update_contacts' not in st.session_state:
            st.error("Nenhum arquivo CSV selecionado")
            return
        
        csv_file = st.session_state.update_contacts.get(client_id)
        if not csv_file:
            st.error("Nenhum arquivo CSV selecionado")
            return
        
        # Processa o CSV
        with st.spinner('Processando contatos...'):
            contacts, error = process_csv_file(csv_file)
            if error:
                st.error(error)
                return
            
            if not contacts:
                st.warning("Nenhum contato válido encontrado no arquivo CSV")
                return
            
            # Prepara os dados para atualização
            update_data = {
                "contacts": contacts
            }
            
            # Envia para a API
            with st.spinner(f'Atualizando contatos do cliente {client_name}...'):
                response = requests.patch(
                    f"{API_GATEWAY_URL}/clients/{client_id}",
                    headers={"Authorization": f"Bearer {st.session_state['token']}"},
                    json=update_data
                )
                
                if response.status_code == 200:
                    st.success(f"Contatos do cliente {client_name} atualizados com sucesso!")
                    st.success(f"{len(contacts)} contatos processados")
                    # Limpa o arquivo do state
                    st.session_state.update_contacts[client_id] = None
                    # Força recarregamento dos clientes
                    st.session_state.clients_data = None
                else:
                    error_detail = response.json().get('detail', "Erro desconhecido")
                    st.error(f"Erro ao atualizar contatos: {error_detail}")
    except Exception as e:
        st.error(f"Erro ao atualizar contatos: {str(e)}")

def handle_client_update(client_id):
    """Callback para lidar com a atualização do cliente"""
    form_prefix = f"edit_{client_id}"
    
    try:
        # Prepara os dados para atualização
        update_data = {}
        
        # Verifica cada campo e adiciona apenas os alterados
        if f"{form_prefix}_name" in st.session_state:
            update_data["name"] = st.session_state[f"{form_prefix}_name"]
        
        if f"{form_prefix}_description" in st.session_state:
            update_data["description"] = st.session_state[f"{form_prefix}_description"]
        
        if f"{form_prefix}_daily_limit" in st.session_state:
            update_data["daily_limit"] = st.session_state[f"{form_prefix}_daily_limit"]
        
        # Processa o CSV se fornecido
        if f"{form_prefix}_contacts" in st.session_state and st.session_state[f"{form_prefix}_contacts"] is not None:
            with st.spinner('Processando contatos...'):
                contacts, error = process_csv_file(st.session_state[f"{form_prefix}_contacts"])
                if error:
                    st.error(error)
                    return
                
                if contacts:
                    update_data["contacts"] = contacts
                else:
                    st.warning("Nenhum contato válido encontrado no arquivo CSV")
                    return
        
        if not update_data:
            st.warning("Nenhuma alteração detectada")
            return
        
        # Envia para a API
        with st.spinner('Atualizando cliente...'):
            response = requests.put(
                f"{API_GATEWAY_URL}/clients/{client_id}",
                headers={"Authorization": f"Bearer {st.session_state['token']}"},
                json=update_data
            )
            
            if response.status_code == 200:
                st.session_state.show_update_success = True
                if "contacts" in update_data:
                    st.session_state.contacts_updated = len(update_data["contacts"])
                # Limpa os campos do formulário
                for key in list(st.session_state.keys()):
                    if key.startswith(form_prefix):
                        del st.session_state[key]
                # Força recarregamento dos clientes
                st.session_state.clients_data = None
            else:
                error_detail = response.json().get('detail', "Erro desconhecido")
                st.error(f"Erro ao atualizar cliente: {error_detail}")
    except Exception as e:
        st.error(f"Erro ao atualizar cliente: {str(e)}")

def handle_client_delete(client_id):
    """Callback para lidar com a exclusão do cliente"""
    try:
        response = requests.delete(
            f"{API_GATEWAY_URL}/clients/{client_id}",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )
        
        if response.status_code == 200:
            st.session_state.show_delete_success = True
        else:
            error_msg = response.json().get('detail', 'Erro desconhecido')
            st.error(f"Erro ao excluir cliente: {error_msg}")
    except Exception as e:
        st.error(f"Erro ao excluir cliente: {str(e)}")

def show_clients():
    """Mostra a tela de gerenciamento de clientes"""
    st.markdown("<h2>Gerenciamento de Clientes</h2>", unsafe_allow_html=True)
    
    # Inicializa variáveis de estado
    if 'show_success_message' not in st.session_state:
        st.session_state.show_success_message = False
    if 'show_update_success' not in st.session_state:
        st.session_state.show_update_success = False
    if 'show_delete_success' not in st.session_state:
        st.session_state.show_delete_success = False
    if 'clients_data' not in st.session_state:
        st.session_state.clients_data = None
    if 'contacts_processed' not in st.session_state:
        st.session_state.contacts_processed = 0
    if 'contacts_updated' not in st.session_state:
        st.session_state.contacts_updated = 0
    
    # Mostra mensagens de sucesso se necessário
    if st.session_state.show_success_message:
        st.success("Cliente cadastrado com sucesso!")
        if st.session_state.contacts_processed > 0:
            st.success(f"{st.session_state.contacts_processed} contatos processados com sucesso!")
        st.session_state.show_success_message = False
        st.session_state.contacts_processed = 0
        st.session_state.clients_data = None
    
    if st.session_state.show_update_success:
        st.success("Cliente atualizado com sucesso!")
        if st.session_state.contacts_updated > 0:
            st.success(f"{st.session_state.contacts_updated} contatos atualizados com sucesso!")
        st.session_state.show_update_success = False
        st.session_state.contacts_updated = 0
        st.session_state.clients_data = None
    
    if st.session_state.show_delete_success:
        st.success("Cliente excluído com sucesso!")
        st.session_state.show_delete_success = False
        st.session_state.clients_data = None
    
    # Seção para adicionar novo cliente
    with st.expander("Adicionar Novo Cliente", expanded=False):
        with st.form("new_client_form", clear_on_submit=True):
            st.text_input("Nome do Cliente", key="client_name")
            st.text_area("Descrição (opcional)", key="client_description")
            st.number_input("Limite Diário de Mensagens", min_value=1, value=100, key="client_limit")
            
            # Upload de arquivo de contatos com exemplo
            st.markdown("""
            **Upload de Contatos (CSV)**
            O arquivo CSV deve conter as seguintes colunas:
            - nome (obrigatório)
            - numero (obrigatório)
            - grupo (opcional)
            """)
            st.file_uploader("Lista de Contatos (CSV)", type=['csv'], key="client_contacts")
            
            st.form_submit_button("Cadastrar Cliente", on_click=handle_client_submit)
    
    # Seção para listar clientes cadastrados
    st.markdown("<h3>Clientes Cadastrados</h3>", unsafe_allow_html=True)
    
    # Carrega os clientes apenas se necessário
    if st.session_state.clients_data is None:
        try:
            response = requests.get(
                f"{API_GATEWAY_URL}/clients/",
                headers={"Authorization": f"Bearer {st.session_state['token']}"}
            )
            
            if response.status_code == 200:
                st.session_state.clients_data = response.json()
            else:
                st.error("Erro ao carregar lista de clientes")
                return
        except Exception as e:
            st.error(f"Erro ao carregar clientes: {str(e)}")
            return
    
    # Mostra os clientes do cache
    if not st.session_state.clients_data:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        for client in st.session_state.clients_data:
            with st.expander(f"{client['name']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Descrição:** {client.get('description', 'N/A')}")
                    st.write(f"**Limite Diário:** {client.get('daily_limit', 'N/A')}")
                    
                    # Mostra os contatos se existirem
                    if client.get('contacts'):
                        st.write("**Contatos:**")
                        contacts_df = pd.DataFrame(client['contacts'])
                        st.dataframe(contacts_df)
                
                with col2:
                    user_data = get_current_user()
                    is_admin = user_data.get('is_admin', False)
                    
                    if not is_admin:
                        st.warning("Apenas administradores podem editar ou excluir clientes.")
                    else:
                        form_prefix = f"edit_{client['id']}"
                        with st.form(key=f"edit_form_{client['id']}", clear_on_submit=True):
                            st.text_input(
                                "Novo Nome",
                                value=client['name'],
                                key=f"{form_prefix}_name"
                            )
                            
                            st.text_area(
                                "Nova Descrição",
                                value=client.get('description', ''),
                                key=f"{form_prefix}_description"
                            )
                            
                            st.number_input(
                                "Novo Limite Diário",
                                min_value=1,
                                value=client.get('daily_limit', 100),
                                key=f"{form_prefix}_daily_limit"
                            )
                            
                            st.file_uploader(
                                "Atualizar Lista de Contatos (CSV)",
                                type=['csv'],
                                key=f"{form_prefix}_contacts",
                                help="Selecione um arquivo CSV com as colunas: nome, numero, grupo (opcional)"
                            )
                            
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                st.form_submit_button(
                                    "Salvar Alterações",
                                    on_click=handle_client_update,
                                    args=(client['id'],)
                                )
                            
                            with col_delete:
                                st.form_submit_button(
                                    "Excluir Cliente",
                                    type="secondary",
                                    on_click=handle_client_delete,
                                    args=(client['id'],)
                                )

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['token'] = None

if not st.session_state['authenticated']:
    show_login()
else:
    # Menu de navegação com ícones
    with st.sidebar:
        # Informações do usuário
        user_data = get_current_user()
        if user_data:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; padding: 1rem 0.5rem; margin-bottom: 1rem;">
                    <div style="font-size: 24px; margin-right: 10px; color: #3B82F6;">{user_data.get('avatar_emoji', '👤')}</div>
                    <div style="color: white; font-size: 18px;">{user_data.get('username', 'Usuário')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Adiciona espaço antes do menu
        st.markdown('<div style="margin-left: -1rem;">', unsafe_allow_html=True)
        
        # Menu com bordas arredondadas no item selecionado
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Clientes", "Mensagens", "Histórico", "Configurações", "Sair"],
            icons=["speedometer2", "people-fill", "whatsapp", "clock-history", "gear", "box-arrow-left"],
            menu_icon=None,
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {
                    "color": "white",
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0.5rem 1rem",
                    "padding": "0.5rem 1rem",
                    "--hover-color": "rgba(255, 255, 255, 0.1)",
                    "border-radius": "12px",
                },
                "nav-link-selected": {
                    "background-color": "#FF4B4B",
                    "color": "white",
                    "font-weight": "normal",
                    "border-radius": "12px",
                },
                "separator": "color: #ffffff22",
            }
        )
        
        # Fecha a div do margin-left
        st.markdown('</div>', unsafe_allow_html=True)
        
        if selected == "Sair":
            st.session_state['authenticated'] = False
            st.session_state['token'] = None
            st.experimental_rerun()
    
    # Conteúdo principal
    if selected == "Dashboard":
        st.title("Dashboard")
        st.write("Bem-vindo ao SBsender!")
        
        # Layout do dashboard em duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Resumo")
            st.info("Aqui você verá um resumo das suas atividades")
            
        with col2:
            st.header("Status")
            st.info("Aqui você verá o status do sistema")
            
    elif selected == "Clientes":
        show_clients()
    elif selected == "Mensagens":
        st.title("Mensagens")
        st.info("Em breve você poderá gerenciar suas mensagens aqui!")
    elif selected == "Histórico":
        st.title("Histórico")
        st.info("Em breve você poderá visualizar o histórico aqui!")
    elif selected == "Configurações":
        st.title("Configurações")
        st.info("Em breve você poderá ajustar suas configurações aqui!")
