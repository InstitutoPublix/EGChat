from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None

    return value.replace("\r", "").replace("\n", "").strip()


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

OPENAI_API_KEY = _env("OPENAI_API_KEY")
CLAUDE_API_KEY = _env("CLAUDE_API_KEY")

QDRANT_URL = _env("QDRANT_URL")
QDRANT_API_KEY = _env("QDRANT_API_KEY")
QDRANT_COLLECTION = _env("QDRANT_COLLECTION", "egchat_tjce")
QDRANT_TIMEOUT = int(_env("QDRANT_TIMEOUT", "90"))

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
CLAUDE_MODEL = _env("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

DEFAULT_SOURCE_FILES = [
    PROJECT_ROOT / "data" / "contexto1.txt",
    PROJECT_ROOT / "data" / "Template_Projeto_Aplicativo_TJCE2026.txt", 
    PROJECT_ROOT / "data" / "Publix_Resolucao_Criativa_de_Problemas.txt",
    PROJECT_ROOT / "data" / "resolucao_n332.txt",
    PROJECT_ROOT / "data" / "resolucao_n615.txt",
]
