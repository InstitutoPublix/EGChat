from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    QDRANT_TIMEOUT,
    QDRANT_URL,
)

load_dotenv()

VECTOR_SIZE = 1536

def _qdrant_kwargs() -> dict:
    if not QDRANT_URL:
        raise RuntimeError("QDRANT_URL nao foi configurada.")

    if not QDRANT_API_KEY:
        raise RuntimeError("QDRANT_API_KEY nao foi configurada.")

    return {
        "url": QDRANT_URL,
        "api_key": QDRANT_API_KEY,
        "timeout": QDRANT_TIMEOUT,
    }


def _create_collection(client: QdrantClient) -> None:
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def _create_collection_if_not_exists() -> None:
    client = QdrantClient(**_qdrant_kwargs())
    try:
        if client.collection_exists(QDRANT_COLLECTION):
            print(f"Collection '{QDRANT_COLLECTION}' ja existe.")
            return

        _create_collection(client)
        print(f"Collection '{QDRANT_COLLECTION}' criada com sucesso.")
    finally:
        client.close()


def recreate_collection() -> None:
    client = QdrantClient(**_qdrant_kwargs())
    try:
        if client.collection_exists(QDRANT_COLLECTION):
            client.delete_collection(QDRANT_COLLECTION)
            print(f"Collection '{QDRANT_COLLECTION}' removida.")

        _create_collection(client)
        print(f"Collection '{QDRANT_COLLECTION}' recriada com sucesso.")
    finally:
        client.close()


def get_vectorstore(documents=None):
    embeddings = OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )

    if documents:
        _create_collection_if_not_exists()

        return QdrantVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=QDRANT_COLLECTION,
            **_qdrant_kwargs(),
        )

    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=QDRANT_COLLECTION,
        **_qdrant_kwargs(),
    )
    print(f"Conectado ao vectorstore existente na collection '{QDRANT_COLLECTION}'.")
    return vectorstore


def collection_exists() -> bool:
    client = QdrantClient(**_qdrant_kwargs())
    try:
        return client.collection_exists(QDRANT_COLLECTION)
    finally:
        client.close()
