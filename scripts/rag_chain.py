from langchain_core.documents import Document
from llm import generate_answer
from reranker import rerank_documents
from retriever import get_retriever
from config import RERANKER_ENABLED, RERANKER_TOP_K

FALLBACK_MESSAGE = "Informacao nao disponivel no material de apoio."
MAX_HISTORY_INTERACTIONS = 2

def trim_chat_history(chat_history: list[dict] | None) -> list[dict]:
    return list(chat_history or [])[-MAX_HISTORY_INTERACTIONS:]

def append_to_chat_history(
    chat_history: list[dict] | None,
    question: str,
    answer: str,
) -> list[dict]:
    
    updated_history = trim_chat_history(chat_history)
    updated_history.append(
        {
            "question": question,
            "answer": answer,
        }
    )
    return updated_history[-MAX_HISTORY_INTERACTIONS:]


def _format_context(documents: list[Document]) -> str:
    context_parts = []

    for index, document in enumerate(documents, 1):
        metadata = document.metadata or {}
        source = metadata.get("file_name") or metadata.get("source") or "fonte desconhecida"
        chunk_id = metadata.get("chunk_id", "sem chunk_id")

        context_parts.append(
            "\n".join(
                [
                    f"[Trecho {index}]",
                    f"Fonte: {source}",
                    f"Chunk: {chunk_id}",
                    document.page_content.strip(),
                ]
            )
        )

    return "\n\n".join(context_parts)


def answer_question(question: str, chat_history: list[dict] | None = None) -> str:
    clean_question = question.strip()
    if not clean_question:
        return "Digite uma pergunta para que eu possa ajudar."

    recent_history = trim_chat_history(chat_history)
    documents = get_retriever(clean_question)
    if not documents:
        return FALLBACK_MESSAGE

    if RERANKER_ENABLED:
        documents = rerank_documents(clean_question, documents, RERANKER_TOP_K)

    context = _format_context(documents)
    return generate_answer(
        question=clean_question,
        context=context,
        chat_history=recent_history,
    )


def answer_question_with_history(
    question: str,
    chat_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    
    answer = answer_question(question, chat_history)
    clean_question = question.strip()

    if not clean_question:
        return answer, trim_chat_history(chat_history)

    updated_history = append_to_chat_history(chat_history, clean_question, answer)
    return answer, updated_history

