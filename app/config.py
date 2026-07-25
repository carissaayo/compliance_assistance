from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

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

    # Integrations (add now, use in later phases)
    openai_api_key: str = ""
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/naijapay_rag"
    redis_url: str = "redis://localhost:6379/0"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()