import json
from textwrap import dedent
import uuid

from langchain.messages import AnyMessage, HumanMessage, ToolMessage
from sqlalchemy.orm import Session
from app.agent.constants import COMPANY_ALIASES, ALLOWED_METRICS
from app.core.config import settings
from app.model.chat_session import ChatSession
from app.model.user import User
from app.core.logger import logger


def ndjson(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def parse_tool_content(content):
    if isinstance(content, (dict, list)):
        return content

    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

    return None


def normalize_company(name: str) -> str:
    return COMPANY_ALIASES.get(name.lower().strip(), name)


def validate_metrics(metrics: list[str]):
    valid = [m for m in metrics if m in ALLOWED_METRICS]
    invalid = list(set(metrics) - set(valid))
    return valid, invalid


def get_or_create_session(
    session_id: str | None,
    user: User,
    db: Session,
) -> str:
    if session_id:
        logger.info(f"Using existing session_id: {session_id}")
        return session_id

    session_id = str(uuid.uuid4())

    chat_session = ChatSession(
        session_id=session_id,
        user_id=user.id,
    )

    db.add(chat_session)
    db.commit()

    return session_id


def sql_to_markdown_table(
    query: str,
    results: list[dict],
) -> str:
    if not results:
        return "No results found."

    query = dedent(query).strip()

    headers = list(results[0].keys())

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    rows = []
    for row in results:
        values = []

        for header in headers:
            value = row[header]

            if isinstance(value, (int, float)) and abs(value) >= 1_000:
                value = f"{value:,.0f}"

            values.append(str(value))

        rows.append("| " + " | ".join(values) + " |")

    table = "\n".join([header_row, separator_row, *rows])

    return f"### SQL Query\n\n```sql\n{query}\n```\n\n### Results\n\n{table}"


def extract_sources(messages: list[AnyMessage]) -> list[dict]:
    sources = []
    seen = set()

    last_human_idx = max(
        i for i, m in enumerate(messages) if isinstance(m, HumanMessage)
    )
    latest_messages = messages[last_human_idx:]

    for msg in latest_messages:
        if not isinstance(msg, ToolMessage):
            continue

        result = parse_tool_content(msg.content)
        if not isinstance(result, dict):
            continue

        if msg.name == "sql_query":
            if result.get("found"):
                sources.append(
                    {
                        "type": "markdown",
                        "content": sql_to_markdown_table(
                            result["query"],
                            result["results"],
                        ),
                    }
                )

        elif msg.name == "rag_search":
            for source in result.get(
                "sources",
                [],
            ):
                key = (
                    source["document"],
                    source["page"],
                )

                if key in seen:
                    continue

                seen.add(key)

                sources.append(
                    {
                        "type": "url",
                        "title": (
                            f"{source['document']} "
                            f"- page {source['page']}"
                            f" (score: {source['score']:.2f})"
                        ),
                        "url": (
                            f"{settings.BASE_URL}"
                            f"/sources/{source['document']}"
                            f"#page={source['page']}"
                        ),
                    }
                )
    return sources
