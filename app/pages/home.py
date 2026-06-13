import streamlit as st


def render():
    st.title("Anime & Manga Recommender")

    st.markdown(
        """
Find personalized anime and manga recommendations using
retrieval-augmented generation (RAG).

### Features
- AI-powered recommendations
- Source-backed suggestions
- Anime, manga, or both
- Persistent recommendation history
"""
    )

    st.info("Open the Recommendations page from the sidebar to begin.")

    st.button(
        "Start Recommending",
        disabled=True,
        help="Use the sidebar navigation to open Recommendations.",
    )