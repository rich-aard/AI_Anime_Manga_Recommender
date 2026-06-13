import streamlit as st

from app.utils.session_state import (
    get_chat_history,
    get_sources_history,
    clear_all,
)

from app.components.anime_card import (
    render_source_list,
)


def render():

    st.title("Recommendation History")

    chat_history = get_chat_history()
    sources_history = get_sources_history()

    if not chat_history:

        st.info("No history yet.")

        return

    assistant_idx = 0
    pending_user = None

    for message in chat_history:

        role = message["role"]

        if role == "user":

            pending_user = message["content"]

        elif role == "assistant":

            response = message["content"]

            sources = []

            if assistant_idx < len(sources_history):
                sources = sources_history[
                    assistant_idx
                ]

            assistant_idx += 1

            with st.expander(f"{pending_user or 'Conversation'}"):
                st.write(response)
                if sources:
                    st.divider()
                    render_source_list(sources)

    st.divider()
    if st.button(
        "Clear History",
        type="secondary",
    ):
        clear_all()
        st.rerun()