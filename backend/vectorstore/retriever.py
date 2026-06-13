from functools import lru_cache
from typing import Literal

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever

from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)

ContentType = Literal["anime", "manga"] | None

@lru_cache(maxsize=1)
def _load_vectorstore() -> FAISS:
    """Load FAISS index once and cache it for the lifetime of the process."""
    try:
        logger.info("Loading embedding model: %s", settings.huggingface_embedding_model)
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.huggingface_embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},  #must match to ingest.py 
        )

        logger.info("Loading FAISS index from %s", settings.db_faiss_path)
        vectorstore = FAISS.load_local(
            str(settings.db_faiss_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )

        logger.info("FAISS index loaded successfully")
        return vectorstore

    except Exception as e:
        raise CustomException("Failed to load FAISS vectorstore", e)

def get_retriever(
    content_type: ContentType = None,
    k: int = 5,
) -> VectorStoreRetriever:
    try:
        vectorstore = _load_vectorstore()

        search_kwargs: dict = {
            "k": k,
            "fetch_k": k * 20,
        }

        if content_type is not None:
            search_kwargs["filter"] = {"content_type": content_type}
            logger.info("Retriever scoped to content_type='%s', k=%d", content_type, k)
        else:
            logger.info("Retriever scoped to all content, k=%d", k)

        return vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs,
        )

    except Exception as e:
        raise CustomException("Failed to create retriever", e)