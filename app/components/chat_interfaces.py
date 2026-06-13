
import streamlit as st

from app.utils.session_state import (
    get_chat_history,
    get_sources_history,
)
from app.components.anime_card import (
    render_source_list,
)

def render_user_message(content: str) -> None:
    """
    Render a single user chat bubble.
    """

    with st.chat_message("user"):
        st.markdown(content)


def render_assistant_message(
    content: str,
    sources: list[dict] | None = None,
) -> None:
    """
    Render assistant response and optional sources.
    """

    with st.chat_message("assistant"):

        st.markdown(content)

        if sources:
            with st.expander(
                "Sources",
                expanded=False,
            ):
                render_source_list(sources)


def render_empty_state() -> None:
    """
    Displayed before the first conversation.
    """

    st.markdown(
        """
# Welcome to the Anime & Manga Recommender

Tell me what you're looking for and I'll suggest titles
based on the retrieved database.

### Try asking:

- "Recommend a psychological thriller like Death Note"
- "I want wholesome slice-of-life anime"
- "Suggest manga similar to Monster"
- "Give me short romance anime under 24 episodes"
- "Recommend dark fantasy manga with mature themes"

You can also filter recommendations using the sidebar.
"""
    )


def render_chat_history() -> None:
    """
    Render the entire conversation history.

    Sources are matched only to assistant messages.
    """

    chat_history = get_chat_history()

    if not chat_history:
        render_empty_state()
        return

    sources_history = get_sources_history()

    assistant_idx = 0

    for message in chat_history:

        role = message.get("role")
        content = message.get("content", "")

        if role == "user":

            render_user_message(content)

        elif role == "assistant":

            sources = []

            if assistant_idx < len(sources_history):
                sources = (
                    sources_history[assistant_idx]
                    or []
                )

            render_assistant_message(
                content=content,
                sources=sources,
            )

            assistant_idx += 1