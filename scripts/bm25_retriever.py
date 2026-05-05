import re
import unicodedata
from functools import lru_cache

from chunking import split_documents
from config import DEFAULT_SOURCE_FILES
from langchain_core.documents import Document
from loaders import load_documents
from rank_bm25 import BM25Okapi

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
STOPWORDS = {
    "a",
    "as",
    "ao",
    "aos",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "o",
    "os",
    "para",
    "por",
    "qual",
    "quais",
    "quando",
    "que",
    "sao",
    "sobre",
}


def _normalize_text(text: str) -> str:
    normalized_text = unicodedata.normalize("NFKD", text.lower())
    return "".join(
        char for char in normalized_text if not unicodedata.combining(char)
    )


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(_normalize_text(text))
        if len(token) > 2 and token not in STOPWORDS
    ]


@lru_cache(maxsize=1)
def _load_chunks() -> tuple[Document, ...]:
    documents = []
    for path in DEFAULT_SOURCE_FILES:
        documents.extend(load_documents([path], verbose=False))

    return tuple(split_documents(documents, verbose=False))


@lru_cache(maxsize=1)
def _get_bm25_index():
    chunks = _load_chunks()
    tokenized_chunks = [_tokenize(chunk.page_content) for chunk in chunks]
    return BM25Okapi(tokenized_chunks), chunks


def bm25_search(query: str, k: int) -> list[Document]:
    query_tokens = _tokenize(query)
    if not query_tokens or k <= 0:
        return []

    bm25, chunks = _get_bm25_index()
    if not chunks:
        return []

    scores = bm25.get_scores(query_tokens)
    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True,
    )

    results = []
    for index in ranked_indexes:
        score = float(scores[index])
        if score <= 0:
            continue

        results.append(chunks[index])
        if len(results) >= k:
            break

    return results
