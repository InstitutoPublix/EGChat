from langchain_core.documents import Document
from vectorstore import get_vectorstore


def get_retriever(pergunta: str) -> list[Document]:
    vectorstore = get_vectorstore(documents=None)
    try:
        results = vectorstore.similarity_search(pergunta, k=5)

    finally:
        vectorstore.client.close()

    return results
