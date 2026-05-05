from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents: list[Document], verbose: bool = True) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, 
                                              chunk_overlap=300,
                                              separators=["\n\n", "\n", ". ", " ", ""])
    
    chunks = splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    if verbose:
        if chunks:
            print(f"\nDocumentos divididos em {len(chunks)} chunks.")
        else:
            print("Nenhum chunk foi criado. Verifique os documentos de entrada.")

    return chunks
