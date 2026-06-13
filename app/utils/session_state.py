from typing import Any
import streamlit as st
from config.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_STATE: dict[str, Any] = {
    "chat_history": [],
    "content_type": None,
    "expanded_queries": [],
    "sources_history": [],
    "is_loading": False,
}


def init_session_state() -> None:
    """Initialize all session state keys with defaults if not already set."""
    for key, default_value in _DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = (
                default_value.copy() if isinstance(default_value, list) else default_value
            )
            logger.debug("Initialized session state key: %s", key)


def get_chat_history() -> list[dict[str, str]]:
    return st.session_state.chat_history


def add_user_message(content: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": content})


def add_assistant_message(content: str) -> None:
    st.session_state.chat_history.append({"role": "assistant", "content": content})


def clear_chat_history() -> None:
    st.session_state.chat_history = []


def format_chat_history_as_str() -> str:
    """
    Formats full conversation history as a string for LLM context.
    Includes all messages including the latest user message.

    Example:
        User: Recommend dark anime
        Assistant: You might like Monster.
        User: Something shorter?
    """
    return "\n".join(
        f"{m['role'].capitalize()}: {m['content']}"
        for m in st.session_state.chat_history
    )


def get_content_type() -> str | None:
    return st.session_state.content_type


def set_content_type(value: str | None) -> None:
    st.session_state.content_type = value


def add_expanded_query(query: str) -> None:
    st.session_state.expanded_queries.append(query)


def get_expanded_queries() -> list[str]:
    return st.session_state.expanded_queries


def clear_expanded_queries() -> None:
    st.session_state.expanded_queries = []


def add_sources(sources: list[Any]) -> None:
    st.session_state.sources_history.append(sources)


def get_sources_history() -> list:
    return st.session_state.sources_history


def clear_sources_history() -> None:
    st.session_state.sources_history = []


def is_loading() -> bool:
    return st.session_state.is_loading


def set_loading(value: bool) -> None:
    st.session_state.is_loading = value


def clear_all() -> None:
    """
    Clears entire conversation state while preserving content_type filter.
    """
    clear_chat_history()
    clear_expanded_queries()
    clear_sources_history()
    set_loading(False)
    logger.info("Session state cleared")