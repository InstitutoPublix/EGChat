from pathlib import Path
import logging
import os
import sys

from flask import Flask, jsonify, render_template, request, send_from_directory


# Caminhos base do projeto. O Cloud Run inicia o processo a partir de /app,
# mas manter tudo relativo ao arquivo deixa o app portavel para execucao local.
PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from rag_chain import MAX_HISTORY_INTERACTIONS, answer_question_with_history


# Mensagem inicial exibida pelo frontend. Ela fica no backend para evitar
# duplicacao entre template e JavaScript, e para manter o texto versionado aqui.
WELCOME_MESSAGE = """Ola! Sou o Mentor Virtual e estou aqui para ajudar com o curso de Transformacao Digital.

Voce pode perguntar sobre cronograma, horarios, atividades, aulas presenciais, mentorias e projeto final."""

# Variaveis obrigatorias para o fluxo RAG. Validar antes de chamar o modelo
# evita erro opaco no frontend e facilita diagnostico em Cloud Run.
REQUIRED_ENV_KEYS = (
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
)

app = Flask(__name__)


def _missing_environment_keys() -> list[str]:
    """Retorna as variaveis ausentes sem expor valores sensiveis em logs/API."""
    return [key for key in REQUIRED_ENV_KEYS if not os.getenv(key)]


@app.get("/")
def index():
    # Renderiza a aplicacao de chat. O Flask injeta configuracoes pequenas que
    # o JavaScript usa para inicializar o estado da conversa no navegador.
    return render_template(
        "index.html",
        max_history_interactions=MAX_HISTORY_INTERACTIONS,
        welcome_message=WELCOME_MESSAGE,
    )


@app.get("/assets/<path:filename>")
def asset(filename: str):
    # Centraliza o acesso aos logos/imagens em /assets sem mover os arquivos
    # para /static.
    return send_from_directory(PROJECT_ROOT / "assets", filename)


@app.get("/healthz")
def healthz():
    # Rota leve para health checks locais ou do Cloud Run. Nao chama LLM,
    # Qdrant ou OpenAI para nao gerar custo em verificacoes de saude.
    return {"status": "ok"}


@app.post("/api/chat")
def chat():
    # Esta API é estatica, o historico vem do navegador e volta atualizado.
    # assim não precisa de banco, sessao de servidor e instancia presa por usuario, fica mais facil e mais barato
    missing_keys = _missing_environment_keys()
    if missing_keys:
        return jsonify(
            {
                "error": "Configure as variaveis de ambiente: "
                + ", ".join(missing_keys)
                + "."
            }
        ), 500

    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not question:
        return jsonify({"error": "Mensagem vazia"}), 400

    try:
        # apenas traduz HTTP/JSON para a funcao Python e devolve JSON ao app.js.
        answer, updated_history = answer_question_with_history(question, history)
        return jsonify({"answer": answer, "history": updated_history})
    except Exception:
        # Nao retorna detalhes tecnicos ao usuario, mas registra stack
        # trace para investigacao nos logs do Cloud Run.
        logging.exception("Erro ao gerar resposta no RAG.")
        return jsonify(
            {
                "error": (
                    "Nao consegui gerar a resposta agora. "
                    "A equipe tecnica deve verificar os logs do Cloud Run."
                )
            }
        ), 500
