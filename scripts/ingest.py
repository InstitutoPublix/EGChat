import argparse

from chunking import split_documents
from config import DEFAULT_SOURCE_FILES
from loaders import load_documents
from vectorstore import collection_exists, get_vectorstore, recreate_collection


def ingest_documents(force: bool = False) -> None:
    exists = collection_exists()

    if exists and not force:
        print("A collection Qdrant ja existe. Use --force para recriar/reindexar.")
        return

    if exists and force:
        print("Recriando collection Qdrant por causa do --force...")
        recreate_collection()

    all_documents = []
    for path in DEFAULT_SOURCE_FILES:
        print(f"Carregando documentos de {path}...")
        documents = load_documents([path])
        all_documents.extend(documents)

    if not all_documents:
        print("Nenhum documento encontrado!")
        return

    print("Dividindo documentos em chunks...")
    chunks = split_documents(all_documents)
    print(f"Chunks criados: {len(chunks)}")

    if not chunks:
        print("Nenhum chunk criado!")
        return

    print("Criando vectorstore e indexando no Qdrant...")
    vectorstore = None
    try:
        vectorstore = get_vectorstore(chunks)
    finally:
        if vectorstore:
            vectorstore.client.close()

    print("Indexacao concluida!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Index EGChat documents in Qdrant.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate/reindex the Qdrant collection even if it already exists.",
    )
    args = parser.parse_args()
    ingest_documents(force=args.force)


if __name__ == "__main__":
    main()
