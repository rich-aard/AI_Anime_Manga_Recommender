from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from typing import Generator

from backend.vectorstore.retriever import get_retriever, ContentType
from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)


PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _load_prompt("system_prompt.txt")),
        ("human", _load_prompt("recommendation_prompt.txt")),
    ]
)

_llm = ChatGroq(
    model=settings.groq_llm_model,
    api_key=settings.groq_api_key,
    temperature=0.3,
)

_chain = _prompt | _llm | StrOutputParser()


def _format_docs(docs: list[Document]) -> str:
    """Include key metadata alongside page_content for richer LLM context."""
    formatted = []
    for doc in docs:
        m = doc.metadata
        header = (
            f"[{m.get('content_type', '').upper()}] {m.get('title', 'Unknown')}"
            f" | Score: {m.get('score', 'N/A')}"
            f" | Genres: {m.get('genres', 'N/A')}"
            f" | Status: {m.get('status', 'N/A')}"
        )
        formatted.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def query(
    question: str,
    chat_history: str = "",
    content_type: ContentType = None,
    k: int = 5,
) -> dict:
    try:
        logger.info(
            "Query received | content_type=%s | question=%s",
            content_type,
            question,
        )

        retriever = get_retriever(content_type=content_type, k=k)
        docs = retriever.invoke(question)
        logger.info("Retrieved %d documents", len(docs))

        context = _format_docs(docs)

        answer = _chain.invoke(
            {
                "context": context,
                "question": question,
                "chat_history": chat_history,
            }
        )

        logger.info("Answer generated successfully")

        return {
            "question": question,
            "answer": answer,
            "sources": [doc.metadata for doc in docs],
        }

    except Exception as e:
        raise CustomException("Retrieval chain query failed", e)

def stream_query(
    question: str,
    chat_history: str = "",
    content_type: ContentType = None,
    k: int = 5,
) -> tuple[Generator, list[dict]]:
    """
    Stream LLM response token by token.

    Returns:
        (stream, sources)
        stream  → pass directly to st.write_stream()
        sources → list of metadata dicts for display
    """
    try:
        logger.info(
            "Stream query received | content_type=%s | question=%s",
            content_type,
            question,
        )

        retriever = get_retriever(content_type=content_type, k=k)
        docs = retriever.invoke(question)
        docs = _sort_docs_by_score(docs)
        logger.info("Retrieved %d documents", len(docs))

        context = _format_docs(docs)
        sources = [doc.metadata for doc in docs]

        stream = _chain.stream(
            {
                "context": context,
                "question": question,
                "chat_history": chat_history,
            }
        )

        return stream, sources

    except Exception as e:
        raise CustomException("Stream query failed", e)
    
def _sort_docs_by_score(docs: list[Document]) -> list[Document]:
    """Sort retrieved docs by MAL score descending, unscored last."""
    def score_key(doc):
        score = doc.metadata.get("score", "")
        try:
            return float(score)
        except (ValueError, TypeError):
            return 0.0
    return sorted(docs, key=score_key, reverse=True)