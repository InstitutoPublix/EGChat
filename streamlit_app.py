import streamlit as st
import anthropic
import openai
import os
from PIL import Image
import time
import json
import streamlit.components.v1 as components
import speech_recognition as sr



# Configurações iniciais
st.set_page_config(
    page_title=" TJCE Professor Virtual",
    page_icon="🏛️",
    layout="wide",
)


# CSS personalizado para estilizar o balão de upload e o aviso

st.markdown(
    """
    <style>

/* Esconde os elementos indesejados */
    ._link_gzau3_10, ._profileContainer_gzau3_53 {
        display: none !important;
        visibility: hidden !important;
    }

        /* Remover barra inferior completa */
        footer { 
            visibility: hidden !important;
            display: none !important;
        }

        /* Remover qualquer iframe que possa conter o branding */
        iframe[title="streamlit branding"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Remover a toolbar do Streamlit */
        [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Remover qualquer div fixa que possa conter os botões */
        div[data-testid="stActionButtonIcon"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Ocultar qualquer elemento fixo no canto inferior direito */
        div[style*="position: fixed"][style*="right: 0px"][style*="bottom: 0px"] {
            display: none !important;
            visibility: hidden !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
        /* Remover botões no canto inferior direito */
        iframe[title="streamlit branding"] {
            display: none !important;
        }
        
        footer { 
            display: none !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Tentar esconder qualquer outro elemento fixo */
        div[style*="position: fixed"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>

/* Remover barra superior do Streamlit */
header {visibility: hidden;}

/* Remover botão de configurações */
[data-testid="stToolbar"] {visibility: hidden !important;}

/* Remover rodapé do Streamlit */
footer {visibility: hidden;}

/* Remover botão de compartilhamento */
[data-testid="stActionButtonIcon"] {display: none !important;}

/* Ajustar margem para evitar espaços vazios */
.block-container {padding-top: 1rem;}

 .overlay {
            position: fixed;
            bottom: 0;
            right: 0;
            width: 150px;
            height: 50px;
            background-color: white;
            z-index: 1000;
        }

    /* Estilo para o texto na sidebar */
    .stSidebar .stMarkdown, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stExpander {
        color: white !important;  /* Cor do texto na sidebar */
    }

    /* Estilo para o texto na parte principal */
    .stMarkdown, .stTextInput, .stTextArea, .stButton, .stExpander {
        color: black !important;  /* Cor do texto na parte principal */
    }

    /* Estilo para o container de upload de arquivos */
    .stFileUploader > div > div {
        background-color: white;  /* Fundo branco */
        color: black;  /* Texto preto */
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;  /* Borda cinza para destacar */
    }

    /* Estilo para o texto dentro do balão de upload */
    .stFileUploader label {
        color: black !important;  /* Texto preto */
    }

    /* Estilo para o botão de upload */
    .stFileUploader button {
        background-color: #8dc50b;  /* Verde */
        color: white;  /* Texto branco */
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
    }

    /* Estilo para o texto de drag and drop */
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {
        color: black !important;  /* Texto preto */
    }

    /* Estilo para o container de avisos (st.warning) */
    div[data-testid="stNotification"] > div > div {
        background-color: white !important;  /* Fundo branco */
        color: black !important;  /* Texto preto */
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #ccc !important;  /* Borda cinza para destacar */
    }

    /* Estilo para o ícone de aviso */
    div[data-testid="stNotification"] > div > div > div:first-child {
        color: #8dc50b !important;  /* Cor do ícone (verde) */
    }

    /* Estilo para o subtítulo */
    .subtitulo {
        font-size: 16px !important;  /* Tamanho da fonte reduzido */
        color: black !important;  /* Cor do texto alterada para preto */
    }

    /* Estilo para o rótulo do campo de entrada na sidebar */
    .stSidebar label {
        color: white !important;  /* Cor do texto branco */
    }

    /* Estilo para o texto na caixa de entrada do chat */
    .stChatInput input {
        color: white !important;  /* Cor do texto branco */
    }

    /* Estilo para o placeholder na caixa de entrada do chat */
    .stChatInput input::placeholder {
        color: white !important;  /* Cor do placeholder branco */
    }

    /* Estilo para o texto na caixa de entrada do chat */
div.stChatInput textarea {
    color: white !important;  /* Cor do texto branco */
}

/* Estilo para o placeholder na caixa de entrada do chat */
div.stChatInput textarea::placeholder {
    color: white !important;  /* Cor do placeholder branco */
    opacity: 1;  /* Garante que o placeholder seja totalmente visível */
}
    
     /* Estilo para o ícone */
    .stImage > img {
        filter: drop-shadow(0 0 0 #8dc50b);  /* Aplica a cor #8dc50b ao ícone */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Caminho para a logo do bot
LOGO_BOT_PATH = "assets/icon_tjce_branco.png"

# Verificar se o arquivo da logo existe
if os.path.exists(LOGO_BOT_PATH):
    try:
        LOGO_BOT = Image.open(LOGO_BOT_PATH)
    except Exception as e:
        st.error(f"Erro ao carregar a logo: {e}")
        LOGO_BOT = None
else:
    LOGO_BOT = None

# Caminho para o ícone personalizado (CASO QUEIRA LOGO AO LADO DO TÍTULO, ALTERAR AQUI)
ICON_PATH = "assets/icon_car.jpg"

# Verificar se o arquivo do ícone existe
if os.path.exists(ICON_PATH):
    try:
        # Usar st.columns para posicionar o ícone ao lado do título
        col1, col2 = st.columns([1.5, 4])  # Ajuste as proporções conforme necessário
        with col1:
            st.image(ICON_PATH, width=10000000)  # Exibe o ícone com largura de 30px
        with col2:
            st.title("Professor Virtual TJCE")  # Exibe o título
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("Professor Virtual TJCE")  # Fallback se o ícone não existir

# Subtítulo com fonte reduzida e texto preto
st.markdown(
    '<cp class="subtitulo">Olá, tudo bem? Sou um assistente virtual feito pelo TJCE em parceria com o Instituto Publix para te auxiliar na realização do curso de Transformação Digital [nome do curso aqui]. Eu posso te dar dicas de caminhos a seguir, tirar dúvidas, e muito mais! Pra iniciar, é só mandar uma mensagem na caixa de perguntas aqui embaixo!</p>',
    unsafe_allow_html=True
)

# Inicialização segura das variáveis de estado
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []

# Função para limpar o histórico do chat
def limpar_historico():
    st.session_state.mensagens_chat = []
 
# Carregar arquivos de texto nativos como contexto
def carregar_contexto():
    contexto = ""
    # Adicione aqui os arquivos de texto que você deseja usar como contexto
    arquivos_contexto = [
        "contexto1.txt",
   
    ]

    for arquivo in arquivos_contexto:
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                contexto += f.read() + "\n\n"
        else:
            st.error(f"Arquivo de contexto não encontrado: {arquivo}")
    
    return contexto

# Carregar o contexto ao iniciar o aplicativo
contexto = carregar_contexto()

# Função para dividir o texto em chunks
def dividir_texto(texto, max_tokens=800):  # Chunks menores (800 tokens)
    palavras = texto.split()
    chunks = []
    chunk_atual = ""
    for palavra in palavras:
        if len(chunk_atual.split()) + len(palavra.split()) <= max_tokens:
            chunk_atual += palavra + " "
        else:
            chunks.append(chunk_atual.strip())
            chunk_atual = palavra + " "
    if chunk_atual:
        chunks.append(chunk_atual.strip())
    return chunks

# Função para selecionar chunks relevantes com base na pergunta
def selecionar_chunks_relevantes(pergunta, chunks):
    # Lógica simples para selecionar chunks com base em palavras-chave
    palavras_chave = pergunta.lower().split()
    chunks_relevantes = []
    for chunk in chunks:
        if any(palavra in chunk.lower() for palavra in palavras_chave):
            chunks_relevantes.append(chunk)
    return chunks_relevantes[:2]  # Limita a 2 chunks para evitar excesso de tokens

# Função para gerar resposta com OpenAI usando GPT-3.5 ou Claude Haiku
def gerar_resposta(texto_usuario, contexto_base, openai_api_key=None, claude_api_key=None):
    chunks = dividir_texto(contexto_base)
    chunks_relevantes = selecionar_chunks_relevantes(texto_usuario, chunks)

    # Montar contexto para prompt
    contexto_prompt = "Você é um assistente virtual educacional do TJCE, desenvolvido com o apoio do Instituto Publix. Ajude o aluno a compreender melhor seu curso de transformação digital. Use uma linguagem simples, clara e amigável.\n\n"
    for i, chunk in enumerate(chunks_relevantes):
        contexto_prompt += f"--- Parte {i+1} do Contexto ---\n{chunk}\n\n"

    prompt_completo = contexto_prompt + f"Pergunta do aluno: {texto_usuario}"

    if claude_api_key:
        client = anthropic.Anthropic(api_key=claude_api_key)
        resposta = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=800,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt_completo.strip()}
            ]
        )
        return resposta.content[0].text.strip()

    elif openai_api_key:
        openai.api_key = openai_api_key
        mensagens = [
            {"role": "system", "content": contexto_prompt},
            {"role": "user", "content": texto_usuario}
        ]
        for tentativa in range(3):
            try:
                time.sleep(1)
                resposta = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=mensagens,
                    temperature=0.3,
                    max_tokens=800
                )
                return resposta["choices"][0]["message"]["content"]
            except Exception as e:
                if tentativa < 2:
                    time.sleep(2)
                    continue
                else:
                    return f"Erro ao gerar a resposta: {str(e)}"
    else:
        return "Erro: nenhuma chave de API fornecida."

# Adicionar a logo na sidebar
if LOGO_BOT:
    st.sidebar.image(LOGO_BOT, width=300)
else:
    st.sidebar.markdown("**Logo não encontrada**")

# Interface do Streamlit
api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
claude_api_key = st.sidebar.text_input("🔑 Chave API Claude (Anthropic)", type="password", placeholder="sk-ant-...")

if api_key or claude_api_key:
    if st.sidebar.button("🧹 Limpar Histórico do Chat", key="limpar_historico"):
        limpar_historico()
        st.sidebar.success("Histórico do chat limpo com sucesso!")
else:
    st.warning("Por favor, insira sua chave de API para continuar.")

user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    st.session_state.mensagens_chat.append({"user": user_input, "bot": None})
    resposta = gerar_resposta(user_input, contexto, api_key, claude_api_key)
    st.session_state.mensagens_chat[-1]["bot"] = resposta

with st.container():
    if st.session_state.mensagens_chat:
        for mensagem in st.session_state.mensagens_chat:
            if mensagem["user"]:
                with st.chat_message("user"):
                    st.markdown(f"**Você:** {mensagem['user']}", unsafe_allow_html=True)
            if mensagem["bot"]:
                with st.chat_message("assistant"):
                    st.markdown(f"**Professor Virtual TJCE:**\n\n{mensagem['bot']}", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown("*Professor Virtual TJCE:* Nenhuma mensagem ainda.", unsafe_allow_html=True)