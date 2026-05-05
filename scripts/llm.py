import anthropic
from config import CLAUDE_API_KEY, CLAUDE_MODEL
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT_TEMPLATE

load_dotenv()


def _format_chat_history(chat_history: list[dict] | None) -> str:
    if not chat_history:
        return "Sem historico anterior."

    history_parts = []
    for index, interaction in enumerate(chat_history, 1):
        question = interaction.get("question", "").strip()
        answer = interaction.get("answer", "").strip()
        history_parts.append(
            "\n".join(
                [
                    f"Interacao anterior {index}:",
                    f"Pergunta: {question}",
                    f"Resposta: {answer}",
                ]
            )
        )

    return "\n\n".join(history_parts)

def generate_answer(question: str, context: str, chat_history: list[dict] | None = None) -> str:
    formatted_history = _format_chat_history(chat_history)
    sys_prompt_formatado = SYSTEM_PROMPT_TEMPLATE.format(
        context=context,
        chat_history=formatted_history,
    )
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        temperature=0.1,
        system=sys_prompt_formatado,                    
        messages=[{"role": "user", "content": question}]
    )

    return resp.content[0].text.strip()
