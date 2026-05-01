from pathlib import Path
from typing import Iterable
from langchain_core.documents import Document
from pypdf import PdfReader

EXTENCOES_PERMITIDAS = [".txt", ".pdf"]

def load_documents(paths: Iterable[Path]) -> list[Document]:
    documentos: list[Document] = []

    for path in paths:
        if path.suffix in EXTENCOES_PERMITIDAS:

            if path.suffix == ".pdf":
                reader = PdfReader(path)
                texto = "\n".join(page.extract_text() or "" for page in reader.pages)
                documentos.append(Document(page_content=texto, 
                                           metadata={"source": str(path),
                                                     "file_name": path.name, 
                                                     "file_extension": path.suffix}
                                           ))

            elif path.suffix == ".txt":
                with open(path, "r", encoding="utf-8") as f:
                    texto = f.read()
                    documentos.append(
                        Document(page_content=texto, 
                                 metadata={
                                     "source": str(path), 
                                     "file_name": path.name, 
                                     "file_extension": path.suffix}
                                 )
                        )
        else:
            print(f"Extensão {path.suffix} não é permitida. Pulando arquivo {path}.")
    
    print(f"\n{len(documentos)} documentos carregados com sucesso.")
    return documentos
