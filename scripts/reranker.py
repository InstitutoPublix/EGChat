import os
from functools import lru_cache
from pathlib import Path
from config import RERANKER_BATCH_SIZE, PROJECT_ROOT
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

MODEL_DIR = PROJECT_ROOT / "models"
# mmarco é treinado em MS MARCO multilingual, inclui português nativamente
MODEL_REPO_ID = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MODEL_CACHE_PATH = MODEL_DIR / "mmarco-reranker"
REQUIRED_MODEL_FILES = (
    "config.json",
    "model.safetensors",
    "tokenizer_config.json",
)


def _ensure_model_dir() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_CACHE_PATH.mkdir(parents=True, exist_ok=True)


def _missing_model_files() -> list[str]:
    return [
        file_name
        for file_name in REQUIRED_MODEL_FILES
        if not (MODEL_CACHE_PATH / file_name).is_file()
    ]


def ensure_local_reranker_model() -> None:
    missing_files = _missing_model_files()
    if missing_files:
        missing = ", ".join(missing_files)
        raise RuntimeError(
            "Modelo de reranker nao encontrado em "
            f"{MODEL_CACHE_PATH}. Arquivos ausentes: {missing}. "
            "Execute `python scripts/download_reranker_model.py` antes do build."
        )


def _configure_model_cache() -> None:
    os.environ.setdefault("HF_HOME", str(MODEL_DIR))
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(MODEL_DIR))


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    _ensure_model_dir()
    ensure_local_reranker_model()
    _configure_model_cache()
    return CrossEncoder(str(MODEL_CACHE_PATH))


def rerank_documents(
    query: str,
    documents: list[Document],
    top_k: int,
) -> list[Document]:
    
    query = query.strip()
    if not documents or not query or top_k <= 0:
        return documents[:top_k] if top_k > 0 else []

    try:
        reranker = _get_reranker()

        doc_texts = [doc.page_content for doc in documents]
        scores = reranker.predict(
            [[query, text] for text in doc_texts],
            batch_size=RERANKER_BATCH_SIZE,
        )

        scored_docs = list(zip(documents, scores))
        ranked = sorted(scored_docs, key=lambda x: x[1], reverse=True)

        reranked_documents = []
        for document, score in ranked[:top_k]:
            metadata = dict(document.metadata or {})
            metadata["reranker_score"] = round(float(score), 6)
            reranked_documents.append(
                Document(page_content=document.page_content, metadata=metadata)
            )

        return reranked_documents

    except Exception as e:
        print(f"Erro ao reranquear documentos: {e}")
        return documents[:top_k] if top_k > 0 else []
