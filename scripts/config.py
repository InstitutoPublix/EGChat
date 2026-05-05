from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None

    return value.replace("\r", "").replace("\n", "").strip()


def _env_bool(name: str, default: bool) -> bool:
    value = _env(name, "true" if default else "false")
    return str(value).lower() in {"1", "true", "yes", "sim", "on"}


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

QUERY_EXPANSION_ENABLED = _env_bool("QUERY_EXPANSION_ENABLED", True)
QUERY_EXPANSION_MAX_QUERIES = int(_env("QUERY_EXPANSION_MAX_QUERIES", "4"))

HYBRID_SEARCH_ENABLED = _env_bool("HYBRID_SEARCH_ENABLED", True)
SEMANTIC_TOP_K = int(_env("SEMANTIC_TOP_K", "8"))
BM25_TOP_K = int(_env("BM25_TOP_K", "12"))
FINAL_TOP_K = int(_env("FINAL_TOP_K", "6"))
SEMANTIC_WEIGHT = float(_env("SEMANTIC_WEIGHT", "0.65"))
BM25_WEIGHT = float(_env("BM25_WEIGHT", "0.35"))
RRF_K = int(_env("RRF_K", "60"))

RERANKER_ENABLED = _env_bool("RERANKER_ENABLED", True)
RERANKER_TOP_K = int(_env("RERANKER_TOP_K", "4"))
RERANKER_BATCH_SIZE = int(_env("RERANKER_BATCH_SIZE", "32"))

DEFAULT_SOURCE_FILES = [
    PROJECT_ROOT / "data" / "contexto1.txt",
    PROJECT_ROOT / "data" / "bibliografias.txt",
    PROJECT_ROOT / "data" / "Template_Projeto_Aplicativo_TJCE2026.txt", 
    PROJECT_ROOT / "data" / "Publix_Resolucao_Criativa_de_Problemas.txt",
    PROJECT_ROOT / "data" / "resolucao_n332.txt",
    PROJECT_ROOT / "data" / "resolucao_n615.txt",
]
