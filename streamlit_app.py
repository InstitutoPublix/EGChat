from pathlib import Path
import logging
import os
import sys

import streamlit as st
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from rag_chain import MAX_HISTORY_INTERACTIONS, answer_question_with_history


ASSETS_DIR = PROJECT_ROOT / "assets"
LOGO_BOT_PATH = ASSETS_DIR / "icon_tjce_branco.png"
ICON_PATH = ASSETS_DIR / "icon_car.jpg"
LOGO_ESCOLA_PATH = ASSETS_DIR / "logo_escola.png"
LOGO_PUBLIX_PATH = ASSETS_DIR / "logo_publix.png"

WELCOME_MESSAGE = """Ola! Sou o Mentor Virtual e estou aqui para ajudar com o curso de Transformacao Digital.

Voce pode perguntar sobre cronograma, horarios, atividades, aulas presenciais, mentorias e projeto final."""


st.set_page_config(
    page_title="Mentor Virtual TJCE",
    page_icon="🏛️",
    layout="wide",
)


st.markdown(
    """
    <style>
        header, footer, [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
        }

        .block-container {
            max-width: 980px;
            padding-top: 1.25rem;
            padding-bottom: 5rem;
        }

        .app-subtitle {
            color: #3f3f46;
            font-size: 1rem;
            line-height: 1.5;
            margin: 0.25rem 0 1.5rem 0;
        }

        [data-testid="stSidebar"] {
            background: #0f3d2e;
        }

        [data-testid="stSidebar"] * {
            color: white;
        }

        .stChatMessage {
            border-radius: 8px;
        }

        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] div[data-baseweb="textarea"],
        [data-testid="stChatInput"] div[data-baseweb="textarea"] > div {
            background-color: #d1d5db !important;
        }

        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #111827 !important;
            caret-color: #111827 !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748b !important;
            opacity: 1 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _load_image(path: Path) -> Image.Image | None:
    if not path.exists():
        return None

    try:
        return Image.open(path)
    except Exception:
        return None


def _validate_environment() -> None:
    missing_keys = []
    if not os.getenv("CLAUDE_API_KEY"):
        missing_keys.append("CLAUDE_API_KEY")
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    if not os.getenv("QDRANT_URL"):
        missing_keys.append("QDRANT_URL")
    if not os.getenv("QDRANT_API_KEY"):
        missing_keys.append("QDRANT_API_KEY")

    if missing_keys:
        st.error(
            "Configure as variaveis de ambiente: "
            + ", ".join(missing_keys)
            + "."
        )
        st.stop()


def _init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
            }
        ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def _trim_visible_messages() -> None:
    welcome = st.session_state.messages[:1]
    interaction_messages = st.session_state.messages[1:]
    max_messages = MAX_HISTORY_INTERACTIONS * 2
    st.session_state.messages = welcome + interaction_messages[-max_messages:]


def clear_chat() -> None:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
        }
    ]
    st.session_state.chat_history = []


def render_header() -> None:
    icon = _load_image(ICON_PATH)
    if icon:
        col_icon, col_title = st.columns([1, 5], vertical_alignment="center")
        with col_icon:
            st.image(icon, width=92)
        with col_title:
            st.title("Mentor Virtual TJCE")
    else:
        st.title("Mentor Virtual TJCE")

    st.markdown(
        """
        <p class="app-subtitle">
        Sou o Mentor Virtual do curso de Transformacao Digital, feito pelo TJCE em parceria
        com o Instituto Publix. Envie sua pergunta abaixo para consultar o material de apoio.
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    logo_bot = _load_image(LOGO_BOT_PATH)
    if logo_bot:
        st.sidebar.image(logo_bot, width="stretch")
    else:
        st.sidebar.markdown("**Logo do TJCE nao encontrada**")

    for logo_path in [LOGO_ESCOLA_PATH, LOGO_PUBLIX_PATH]:
        logo = _load_image(logo_path)
        if logo:
            st.sidebar.image(logo, width="stretch")

    st.sidebar.divider()
    st.sidebar.caption(
        f"Memoria da conversa: ultimas {MAX_HISTORY_INTERACTIONS} interacoes desta sessao."
    )

    if st.sidebar.button("Limpar historico", use_container_width=True):
        clear_chat()
        st.rerun()


def render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_message(user_input: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Consultando o material de apoio..."):
            try:
                answer, updated_history = answer_question_with_history(
                    question=user_input,
                    chat_history=st.session_state.chat_history,
                )
            except Exception:
                logging.exception("Erro ao gerar resposta no RAG.")
                answer = (
                    "Nao consegui gerar a resposta agora. "
                    "A equipe tecnica deve verificar os logs do Cloud Run."
                )
                updated_history = st.session_state.chat_history

        st.markdown(answer)

    st.session_state.chat_history = updated_history
    st.session_state.messages.append({"role": "assistant", "content": answer})
    _trim_visible_messages()


_validate_environment()
_init_session_state()
render_sidebar()
render_header()
render_messages()

user_input = st.chat_input("Sua pergunta")
if user_input and user_input.strip():
    handle_user_message(user_input.strip())
