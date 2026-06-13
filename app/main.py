import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.utils.session_state import init_session_state
from app.pages import home, recommendations, history

st.set_page_config(
    page_title="[RXZ.] Otaku Recs: Anime & Manga Recommender",
    layout="centered",
)

init_session_state()

PAGES = {
    "Home": home,
    "Recommendations": recommendations,
    "History": history,
}

with st.sidebar:
    st.title("[RXZ.] Otaku Recs")
    st.caption("AI-powered anime & manga guide")
    st.divider()
    selection = st.radio(
        "Navigate",
        list(PAGES.keys()),
        index=1,                   
        label_visibility="collapsed",
    )

PAGES[selection].render()