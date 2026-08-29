from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume-to-JD Gap Analyzer"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    DATABASE_URL: Optional[str] = None

    # Phase 7: RAG and Retrieval Settings
    KNOWLEDGE_BASE_DIR: str = "data/knowledge"
    VECTOR_STORE_PATH: str = "data/vector_store.json"
    RETRIEVAL_TOP_K: int = 3
    RETRIEVAL_MIN_SIMILARITY: float = 0.40
    MAX_RECOMMENDATIONS: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

