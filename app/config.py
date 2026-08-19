from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
       # App metadata
    app_name: str = "NaijaPay"
    app_version: str = "0.1.0"
    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True

     # Logging
    log_level: Literal["debug", "info", "warning", "error"] = "info"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    embedding_provider: Literal["openai", "ollama"] = "ollama"
    embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = 768
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_timeout: float = 300.0
    openai_api_key: str = ""
    llm_provider: Literal["openai", "ollama"] = "ollama"
    llm_model: str = "qwen3:8b"
    retrieval_max_distance: float = 0.5  
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5440/naijapay_rag"
    redis_url: str = "redis://localhost:6380/0"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()