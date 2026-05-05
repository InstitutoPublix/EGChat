import json

import anthropic
from config import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    QUERY_EXPANSION_ENABLED,
    QUERY_EXPANSION_MAX_QUERIES,
)
from dotenv import load_dotenv

load_dotenv()

SYS_PROMPT = """
Voce e um assistente de pesquisa que expande consultas para melhorar retrieval.
Gere variacoes curtas que preservem a intencao original e usem sinonimos provaveis
no material de apoio.

Regras:
- Retorne somente JSON valido, sem markdown.
- O formato deve ser uma lista de strings: ["query 1", "query 2"].
- A primeira query deve ser a pergunta original.
- Retorne no maximo {max_queries} queries, incluindo a original.
- Nao responda a pergunta; apenas gere as queries.
""".strip()


def _normalize_query(query: str) -> str:
    return " ".join(query.lower().split())


def _extract_json_payload(text: str) -> str:
    clean_text = text.strip()
    if clean_text.startswith("```"):
        clean_text = clean_text.strip("`").strip()
        if clean_text.startswith("json"):
            clean_text = clean_text[4:].strip()

    start = clean_text.find("[")
    end = clean_text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return clean_text[start : end + 1]

    return clean_text


def _parse_queries(raw_text: str, original_question: str) -> list[str]:
    payload = _extract_json_payload(raw_text)
    parsed = json.loads(payload)

    if isinstance(parsed, dict):
        parsed = parsed.get("queries") or parsed.get("consultas") or []

    if not isinstance(parsed, list):
        return [original_question]

    queries = [original_question]
    seen = {_normalize_query(original_question)}

    for item in parsed:
        if not isinstance(item, str):
            continue

        query = item.strip()
        normalized_query = _normalize_query(query)
        if not query or normalized_query in seen:
            continue

        seen.add(normalized_query)
        queries.append(query)

        if len(queries) >= QUERY_EXPANSION_MAX_QUERIES:
            break

    return queries


def expand_query(pergunta: str) -> list[str]:
    pergunta = pergunta.strip()
    if not pergunta:
        return []

    if not QUERY_EXPANSION_ENABLED or not CLAUDE_API_KEY:
        return [pergunta]

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    try:
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=400,
            temperature=0,
            system=SYS_PROMPT.format(max_queries=QUERY_EXPANSION_MAX_QUERIES),
            messages=[{"role": "user", "content": pergunta}],
        )
        raw_queries = resp.content[0].text.strip()
        return _parse_queries(raw_queries, pergunta)
    except Exception as e:
        print(f"Erro ao expandir a consulta: {e}")
        return [pergunta]
