import os
from functools import lru_cache
from pathlib import Path
from config import RERANKER_BATCH_SIZE, PROJECT_ROOT
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

MODEL_DIR = PROJECT_ROOT / "models"
# mmarco é treinado em MS MARCO multilingual, inclui português nativamente
MODEL_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MODEL_CACHE_PATH = MODEL_DIR / "mmarco-reranker"


def _ensure_model_dir() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    _ensure_model_dir()
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODEL_DIR)
    return CrossEncoder(
        MODEL_NAME,
        model_kwargs={"cache_dir": str(MODEL_CACHE_PATH)},
    )


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
