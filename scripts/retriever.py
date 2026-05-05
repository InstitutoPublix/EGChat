import hashlib
from bm25_retriever import bm25_search
from config import (
    BM25_TOP_K,
    BM25_WEIGHT,
    HYBRID_SEARCH_ENABLED,
    RRF_K,
    SEMANTIC_TOP_K,
    SEMANTIC_WEIGHT,
)
from langchain_core.documents import Document
from query_expansion import expand_query
from vectorstore import get_vectorstore

def _document_key(document: Document) -> str:
    metadata = document.metadata or {}
    source = metadata.get("source") or metadata.get("file_name") or ""
    chunk_id = metadata.get("chunk_id")

    if source and chunk_id is not None:
        return f"{source}:{chunk_id}"

    content_hash = hashlib.sha1(document.page_content.encode("utf-8")).hexdigest()
    return f"{source}:{content_hash}"


def _add_rrf_scores(
    documents_by_key: dict[str, Document],
    scores_by_key: dict[str, float],
    documents: list[Document],
    weight: float,
) -> None:
    for rank, document in enumerate(documents, 1):
        key = _document_key(document)
        documents_by_key.setdefault(key, document)
        scores_by_key[key] = scores_by_key.get(key, 0) + weight / (RRF_K + rank)


def get_retriever(pergunta: str) -> list[Document]:
    clean_question = pergunta.strip()
    if not clean_question:
        return []

    queries = expand_query(clean_question)
    documents_by_key: dict[str, Document] = {}
    scores_by_key: dict[str, float] = {}

    vectorstore = get_vectorstore(documents=None)
    try:
        for query in queries:
            _add_rrf_scores(
                documents_by_key=documents_by_key,
                scores_by_key=scores_by_key,
                documents=vectorstore.similarity_search(query, k=SEMANTIC_TOP_K),
                weight=SEMANTIC_WEIGHT,
            )
    finally:
        vectorstore.client.close()

    if HYBRID_SEARCH_ENABLED:
        for query in queries:
            _add_rrf_scores(
                documents_by_key=documents_by_key,
                scores_by_key=scores_by_key,
                documents=bm25_search(query, k=BM25_TOP_K),
                weight=BM25_WEIGHT,
            )

    documents = []
    for key in scores_by_key:
        document = documents_by_key[key]
        metadata = dict(document.metadata or {})
        metadata["retrieval_score"] = round(scores_by_key[key])
        documents.append(Document(page_content=document.page_content, metadata=metadata))
        
    return documents