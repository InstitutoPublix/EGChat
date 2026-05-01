from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                              chunk_overlap=300,
                                              separators=[" ", "", "\n"])
    
    chunks = splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    if chunks:
        print(f"\nDocumentos divididos em {len(chunks)} chunks.")
    else:
        print("Nenhum chunk foi criado. Verifique os documentos de entrada.")

    return chunks

if __name__ == "__main__":
    from config import DATA_DIR, DEFAULT_SOURCE_FILES
    from loaders import load_documents

    path = DATA_DIR / "contexto1.txt"
    documentos = load_documents([path])
    print(documentos[0].metadata)  # Imprime os primeiros 200 caracteres do conteúdo
    chunks = split_documents(documentos)
    print(chunks[0])  # Imprime o primeiro chunk
    print(chunks[0].metadata)  # Imprime os metadados do primeiro chunk
