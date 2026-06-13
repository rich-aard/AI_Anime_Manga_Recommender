import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from huggingface_hub import snapshot_download

from app.utils.session_state import init_session_state
from app.pages import home, recommendations, history
from config.settings import settings


def _ensure_faiss_index() -> None:
    """Download FAISS index from HF Hub if not present locally."""
    index_path = settings.db_faiss_path
    if not (index_path / "index.faiss").exists():
        st.info("Downloading recommendation index... this may take a minute.")
        snapshot_download(
            repo_id="ryczard/anime-manga-faiss-index",
            repo_type="dataset",
            local_dir=str(index_path),
        )
        st.success("Index ready.")
        st.rerun()


st.set_page_config(
    page_title="[RXZ.] Otaku Recs: Anime & Manga Recommender",
    layout="centered",
)

_ensure_faiss_index()

init_session_state()

PAGES = {
    "[RXZ.] Home": home,
    "[RXZ.] Recommendations": recommendations,
    "[RXZ.] History": history,
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