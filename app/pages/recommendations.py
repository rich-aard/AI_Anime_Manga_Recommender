import streamlit as st

from backend.chains.retrieval_chain import stream_query
from app.utils.session_state import (
    init_session_state,
    get_content_type,
    set_content_type,
    add_user_message,
    add_assistant_message,
    add_sources,
    format_chat_history_as_str,
    set_loading,
    is_loading,
)
from app.components.chat_interfaces import (
    render_chat_history,
    render_user_message,
)
from app.components.anime_card import render_source_list


def render():
    init_session_state()

    with st.sidebar:
        choice = st.radio(
            "Content Type",
            ["Both", "Anime", "Manga"],
        )
        mapping = {"Both": None, "Anime": "anime", "Manga": "manga"}
        set_content_type(mapping[choice])

    render_chat_history()

    prompt = st.chat_input("What would you like to watch or read?")

    if not prompt:
        return

    if is_loading():
        st.warning("Please wait for the current response...")
        return

    set_loading(True)

    try:
        add_user_message(prompt)
        render_user_message(prompt)

        history = format_chat_history_as_str()

        stream, sources = stream_query(
            question=prompt,
            chat_history=history,
            content_type=get_content_type(),
            k=5,
        )

       
        with st.chat_message("assistant"):
            answer = st.write_stream(stream)   

            if sources:
                with st.expander("Sources"):
                    render_source_list(sources)

        add_assistant_message(answer)
        add_sources(sources)

    except Exception as e:
        st.error(f"Something went wrong: {e}")

    finally:
        set_loading(False)