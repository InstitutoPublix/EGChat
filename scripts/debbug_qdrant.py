from qdrant_client import QdrantClient

from config import QDRANT_COLLECTION, QDRANT_PATH
from vectorstore import get_vectorstore


def verificar_collection():
    client = QdrantClient(path=str(QDRANT_PATH))
    try:
        collections = client.get_collections()
        print("Collections existentes:")
        for col in collections.collections:
            print(f"  - {col.name}")

        if client.collection_exists(QDRANT_COLLECTION):
            info = client.get_collection(QDRANT_COLLECTION)
            print(f"\nCollection '{QDRANT_COLLECTION}':")
            print(f"  - Pontos totais: {info.points_count}")
        else:
            print(f"\nCollection '{QDRANT_COLLECTION}' nao existe!")
    finally:
        client.close()


def testar_busca_langchain(pergunta: str):
    vectorstore = get_vectorstore(documents=None)
    try:
        results = vectorstore.similarity_search(pergunta, k=3)

        print(f"Resultados para: '{pergunta}'\n")
        print([result.page_content for result in results]) if results else print("Nenhum resultado encontrado.")
    finally:
        vectorstore.client.close()

if __name__ == "__main__":
    verificar_collection()
    testar_busca_langchain("qual o cronograma de aula da turma 1?")
