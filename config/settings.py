from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # apis
    hf_token: str = Field(default="", alias="HF_TOKEN")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")

    # models
    groq_llm_model: str = "llama-3.3-70b-versatile"
    huggingface_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    log_level: str = "INFO"
    app_env: str = "development"

    # paths for data and vectorstore
    base_dir: Path = BASE_DIR
    data_raw_path: Path = BASE_DIR / "data" / "raw"
    data_processed_path: Path = BASE_DIR / "data" / "processed"
    db_faiss_path: Path = BASE_DIR / "data" / "vectorstore" / "faiss_index"

    # chunks values
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # type of content
    content_types: list[str] = ["anime", "manga"]


settings = Settings()
