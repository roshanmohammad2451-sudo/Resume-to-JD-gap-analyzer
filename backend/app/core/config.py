from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume-to-JD Gap Analyzer"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # Groq LLM Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_FALLBACK_MODEL: Optional[str] = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MAX_RETRIES: int = 4
    GROQ_RETRY_INITIAL_DELAY: float = 1.0
    GROQ_RETRY_BACKOFF_FACTOR: float = 2.0
    GROQ_RETRY_JITTER: float = 0.5

    # Embedding Configuration (Kept for Phase 6 embedding stability)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

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

