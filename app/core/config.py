from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    qdrant_collection: str = "financial_documents"

    upload_dir: str = "uploads/raw_pdfs"

    embedding_model: str = "gemini-embedding-001"

    chunk_size: int = 1200
    chunk_overlap: int = 150

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()