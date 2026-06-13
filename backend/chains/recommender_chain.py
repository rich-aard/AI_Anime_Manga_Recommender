from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from backend.vectorstore.retriever import ContentType
from backend.chains.retrieval_chain import query as retrieval_query
from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)


QUERY_EXPANSION_PROMPT = """You are an anime and manga search expert.

Convert the user's request into descriptive prose that mimics how anime synopses are written.
Include specific plot elements, character archetypes, narrative atmosphere, and story themes.
Do NOT use genre labels like "psychological" or "dark" — describe what those mean in story terms.

Examples:
Input: "dark psychological anime"
Output: "a high school student discovers a supernatural notebook that kills anyone whose name is written in it, using it to eliminate criminals while a genius detective tries to catch him, themes of justice, god complex, moral corruption, cat and mouse mind games"

Input: "something like Noragami"
Output: "a minor god who does odd jobs for humans to gain worshippers, a human girl who can see supernatural beings, fighting evil spirits called phantoms, themes of belonging, life and death, Japanese mythology, action comedy with emotional depth"

Input: "wholesome slice of life"
Output: "students enjoying everyday school life, cooking together, seasonal festivals, warm friendships, no conflict or drama, heartwarming and relaxing atmosphere"

User Input: {input}

Expanded Query (descriptive prose only, 2-3 sentences):"""


# Build once at module level
_expansion_llm = ChatGroq(
    model=settings.groq_llm_model,
    api_key=settings.groq_api_key,
    temperature=0,
)

_expansion_chain = (
    ChatPromptTemplate.from_template(QUERY_EXPANSION_PROMPT)
    | _expansion_llm
    | StrOutputParser()
)


def _expand_query(user_input: str) -> str:
    """Use LLM to expand user input into a richer search query."""
    try:
        expanded = _expansion_chain.invoke({"input": user_input})
        logger.info("Expanded query: %s", expanded)
        return expanded
    except Exception as e:
        logger.warning("Query expansion failed, using raw input. Reason: %s", e)
        return user_input


def _resolve_content_type(content_type: str | None) -> ContentType:
    """Normalize content_type — 'combined' maps to None (search both)."""
    if content_type == "combined":
        return None
    return content_type


def recommend(
    user_input: str,
    content_type: str | None = None,
    k: int = 5,
    use_query_expansion: bool = True,
    chat_history: str = "",
) -> dict:
    try:
        logger.info(
            "Recommendation request | content_type=%s | input=%s",
            content_type,
            user_input,
        )

        expanded = _expand_query(user_input) if use_query_expansion else user_input

        resolved_type = _resolve_content_type(content_type)

        result = retrieval_query(
            question=expanded,
            content_type=resolved_type,
            k=k,
            chat_history=chat_history,
        )

        return {
            "user_input": user_input,
            "expanded_query": expanded,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception as e:
        raise CustomException("Recommendation failed", e)
