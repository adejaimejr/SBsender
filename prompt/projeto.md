# SBsender

## Descrição do Projeto

SBsender é um sistema desenvolvido para facilitar o envio de mensagens via WhatsApp para números brasileiros. O sistema permite que o usuário importe uma lista de contatos através de uma caixa de texto (onde os números podem ser colados separados por vírgulas ou quebras de linha) ou importando um arquivo CSV. O software corrige automaticamente os números para o formato reconhecido pelo WhatsApp no Brasil.

O sistema apresenta um painel administrativo que mantém o histórico dos envios, mostrando o que foi importado e o que foi enviado. No painel, há um campo para cadastro de webhooks, permitindo que o usuário registre links de webhook com títulos personalizados. Ao importar a lista de contatos, é possível selecionar um webhook pré-cadastrado para enviar as informações. Com a lista tratada e o webhook selecionado, o sistema envia as informações para o webhook correspondente, que então processa e dispara as mensagens.

**Tecnologias Utilizadas:**
- **Backend:** Python
- **Frontend:** Streamlit
- **Banco de Dados:** MongoDB

## Plano de Ação Passo a Passo

1. **Análise de Requisitos:**
   - Revisar a descrição do projeto e entender todas as funcionalidades desejadas.
   - Identificar os requisitos funcionais e não funcionais.
   - Listar as tecnologias e ferramentas a serem utilizadas: Python, Streamlit e MongoDB.

2. **Planejamento:**
   - Dividir o projeto em módulos:
     - Importação e tratamento de contatos.
     - Cadastro e gestão de webhooks.
     - Histórico de envios.
     - Interface do usuário com Streamlit.
     - Integração com o webhook de disparo.
   - Estabelecer um cronograma com prazos para cada módulo.
   - Definir critérios de sucesso para cada etapa.

3. **Configuração do Ambiente de Desenvolvimento:**
   - Configurar o repositório de código usando Git.
   - Instalar Python e configurar o ambiente virtual.
   - Instalar o Streamlit e as bibliotecas necessárias.
   - Configurar o MongoDB e preparar o banco de dados.

4. **Desenvolvimento:**
   - **Módulo de Importação e Tratamento de Contatos:**
     - Implementar a importação de contatos via caixa de texto e CSV.
     - Desenvolver a lógica para corrigir os números para o formato do WhatsApp.
   - **Módulo de Cadastro e Gestão de Webhooks:**
     - Criar funcionalidades para cadastrar, editar e remover webhooks.
     - Implementar a seleção de webhooks ao importar contatos.
   - **Módulo de Histórico de Envios:**
     - Desenvolver a interface para visualizar o histórico de importações e envios.
     - Armazenar logs no MongoDB.
   - **Interface do Usuário:**
     - Construir a interface usando Streamlit, garantindo usabilidade e intuitividade.
   - **Integração com Webhook de Disparo:**
     - Implementar o envio das informações tratadas para o webhook selecionado.
     - Garantir a segurança e a confiabilidade na transmissão dos dados.
   - Realizar testes unitários em cada funcionalidade desenvolvida.
   - Documentar o código seguindo as melhores práticas.

5. **Integração e Testes:**
   - Integrar todos os módulos desenvolvidos.
   - Realizar testes de integração e testes de sistema completos.
   - Corrigir bugs e inconsistências encontradas durante os testes.

6. **Documentação Final:**
   - Elaborar a documentação completa do software.
   - Incluir instruções de instalação, configuração, uso e manutenção.
   - Preparar um manual do usuário e documentação técnica.

## Instruções para a IDE IA

1. **Seguir o Plano de Ação:**
   - Utilize os passos listados no plano de ação como guia principal para o desenvolvimento.
   - Execute cada etapa de forma sequencial, garantindo a conclusão de uma antes de iniciar a próxima.

2. **Registrar o Progresso:**
   - Crie ou atualize um arquivo chamado `progresso.md` no repositório do projeto.
   - Para cada passo concluído, adicione uma entrada no seguinte formato:

     ```markdown
     ## [Data e Hora]
     ### Passo [Número]: [Título do Passo]
     - **Status:** Concluído
     - **Descrição:** [Breve descrição do que foi realizado]
     ```

   - Se um passo estiver em andamento, atualize o status para "Em andamento" e, ao concluir, marque como "Concluído".

3. **Gerenciar Atualizações do Plano:**
   - Caso seja necessário alterar o plano de ação inicial, crie um documento de atualização chamado `update_v[Versão].md` (por exemplo, `update_v2.md`).
   - No arquivo de atualização, descreva as alterações feitas no plano de ação original.
   - Ao identificar um arquivo de atualização, a IDE deve:
     - Referenciar a versão original do plano.
     - Integrar as mudanças propostas sem descartar o histórico das versões anteriores.
     - Atualizar o `progresso.md` conforme as novas diretrizes.

4. **Manter o Histórico de Versões:**
   - Utilize tags ou comentários nos arquivos para indicar a versão do plano de ação em uso.
   - Assegure-se de que cada atualização mantenha um registro claro das alterações para facilitar o acompanhamento.

## Exemplo de Atualização do Plano de Ação

```markdown
# Update v2 - 15/10/2023

## Alterações no Plano de Ação Original

1. **Desenvolvimento:**
   - **Módulo de Autenticação de Usuários:**
     - Adicionado um sistema de login e controle de acesso.
     - Implementar autenticação via OAuth2.

2. **Integração com API Externa:**
   - Incluir integração com a API do WhatsApp Business para envio direto de mensagens.

3. **Documentação Final:**
   - Adicionar seção sobre configurações de segurança e privacidade dos dados dos usuários.