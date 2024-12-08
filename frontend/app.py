import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

# Configuração da página
st.set_page_config(
    page_title="SBsender",
    page_icon="💬",
    layout="wide"
)

load_dotenv()

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8080")

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
                    print(f"URL da requisição: {API_GATEWAY_URL}/auth/token")
                    
                    # Enviar como form-data conforme esperado pelo OAuth2
                    response = requests.post(
                        f"{API_GATEWAY_URL}/auth/token",
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
                            error_msg = response.json().get('detail', 'Erro ao realizar cadastro')
                            st.error(error_msg)

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
    if 'token' not in st.session_state:
        return None
    
    try:
        response = requests.get(
            f"{API_GATEWAY_URL}/auth/users/me",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Erro ao obter usuário: {str(e)}")
        return None

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
                    <div style="font-size: 24px; margin-right: 10px; color: #3B82F6;">👤</div>
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
            options=["Dashboard", "Mensagem", "Webhooks", "Clientes", "Relatório", "Sair"],
            icons=["speedometer2", "whatsapp", "box-arrow-in-right", "building", "graph-up", "box-arrow-left"],
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
            
    elif selected == "Mensagem":
        st.title("Mensagens")
        st.info("Em breve você poderá gerenciar suas mensagens aqui!")
        
    elif selected == "Configurações":
        st.title("Configurações")
        st.info("Em breve você poderá ajustar suas configurações aqui!")
