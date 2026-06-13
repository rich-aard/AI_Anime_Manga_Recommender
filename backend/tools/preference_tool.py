import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)

EMPTY_PREFERENCES: dict[str, Any] = {
    "liked_genres":    [],
    "disliked_genres": [],
    "liked_titles":    [],
    "disliked_titles": [],
    "mood":            None,
    "content_type":    None,
    "themes":          [],
}

PREFERENCE_PROMPT = """You are a preference extraction system.

Extract anime and manga preferences from the conversation.

Return ONLY valid JSON with no markdown, no explanation, no preamble.

Use exactly this schema:
{
    "liked_genres": [],
    "disliked_genres": [],
    "liked_titles": [],
    "disliked_titles": [],
    "mood": null,
    "content_type": null,
    "themes": []
}

Rules:
- liked_genres: genres the user explicitly likes
- disliked_genres: genres the user explicitly dislikes
- liked_titles: titles explicitly praised
- disliked_titles: titles explicitly disliked
- mood: overall mood preference as a short phrase or null
- content_type: "anime", "manga", or null
- themes: recurring themes mentioned
- Do not infer strong preferences unless clearly supported by the conversation

Conversation History:
{chat_history}

Current User Input:
{user_input}

JSON:"""


_llm = ChatGroq(
    model=settings.groq_llm_model,
    api_key=settings.groq_api_key,
    temperature=0,
)

_chain = (
    ChatPromptTemplate.from_template(PREFERENCE_PROMPT)
    | _llm
    | StrOutputParser()
)


def _parse_preferences(raw: str) -> dict[str, Any]:
    """Strip markdown fences and parse JSON response."""
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


def extract_preferences(
    user_input: str,
    chat_history: str = "",
) -> dict[str, Any]:
    """Extract structured user preferences from conversation."""
    try:
        response = _chain.invoke({
            "chat_history": chat_history,
            "user_input": user_input,
        })

        preferences = _parse_preferences(response)
        logger.info("Preferences extracted: %s", preferences)

        return {**EMPTY_PREFERENCES.copy(), **preferences}

    except json.JSONDecodeError as e:
        logger.warning("Failed to parse preference JSON: %s | raw: %s", e, response)
        return EMPTY_PREFERENCES.copy()

    except Exception as e:
        raise CustomException("Failed to extract preferences", e)


def _tool_func(tool_input: str) -> dict:
    """
    Expects JSON string:
    {"user_input": "...", "chat_history": "..."}
    """
    try:
        payload = json.loads(tool_input)
        return extract_preferences(
            user_input=payload.get("user_input", ""),
            chat_history=payload.get("chat_history", ""),
        )
    except Exception as e:
        logger.warning("Preference tool func failed: %s", e)
        return EMPTY_PREFERENCES.copy()


def get_preference_tool() -> Tool:
    return Tool(
        name="preference_extractor",
        description=(
            "Extracts structured anime and manga preferences from conversation. "
            "Input must be a JSON string with 'user_input' and 'chat_history' keys."
        ),
        func=_tool_func,
    )