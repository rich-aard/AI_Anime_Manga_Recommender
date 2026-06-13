import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)


def _sanitize(value) -> str:
    """Convert NaN / None to empty string for FAISS metadata safety."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def load_documents() -> list[Document]:
    try:
        csv_path = settings.data_processed_path / "combined_dataset.csv"
        logger.info("Loading processed dataset from %s", csv_path)

        df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip",low_memory=False)
        logger.info("Loaded %d rows", len(df))

        before = len(df)
        df["embed_text"] = df["embed_text"].fillna("").astype(str)
        df["score"] = df["score"].fillna("").astype(str)
        df = df[~((df["embed_text"].str.strip() == "") & (df["score"].str.strip() == ""))]

        logger.info("Filtered %d low-quality rows, %d remaining", before - len(df), len(df))

        documents = []
        for row in df.itertuples(index=False):
            documents.append(
                Document(
                    page_content=_sanitize(row.embed_text),
                    metadata={
                        # shared
                        "mal_id":        str(row.mal_id),
                        "title":         _sanitize(row.title),
                        "title_english": _sanitize(row.title_english),
                        "content_type":  _sanitize(row.content_type),  # "anime" | "manga"
                        "type":          _sanitize(row.type),
                        "genres":        _sanitize(row.genres),
                        "themes":        _sanitize(row.themes),
                        "demographics":  _sanitize(row.demographics),
                        "score":         _sanitize(row.score),
                        "rank":          _sanitize(row.rank),
                        "popularity":    _sanitize(row.popularity),
                        "status":        _sanitize(row.status),
                        "image_url":     _sanitize(row.image_url),
                        # anime
                        "episodes":      _sanitize(row.episodes),
                        "season":        _sanitize(row.season),
                        "year":          _sanitize(row.year),
                        "studios":       _sanitize(row.studios),
                        "rating":        _sanitize(row.rating),
                        "source":        _sanitize(row.source),
                        # manga
                        "chapters":      _sanitize(row.chapters),
                        "volumes":       _sanitize(row.volumes),
                        "authors":       _sanitize(row.authors),
                        "serializations": _sanitize(row.serializations),
                    },
                )
            )

        logger.info("Built %d documents", len(documents))
        return documents

    except Exception as e:
        raise CustomException("Failed to load documents from CSV", e)


def ingest() -> None:
    try:
        docs = load_documents()

        logger.info("Initializing embedding model: %s", settings.huggingface_embedding_model)
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.huggingface_embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},  #cosine similarity used
        )
        #no text splitter because synopsis are short, and there will be loss of content if splitted
        logger.info("Embedding %d documents and building FAISS index...", len(docs))
        vectorstore = FAISS.from_documents(docs, embeddings)

        settings.db_faiss_path.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(settings.db_faiss_path))

        logger.info("FAISS index saved to %s", settings.db_faiss_path)
        logger.info("Ingestion complete — %d documents indexed", len(docs))

    except Exception as e:
        raise CustomException("Ingestion pipeline failed", e)


if __name__ == "__main__":
    ingest()