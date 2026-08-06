from app.config import settings
from app.services.embedding.base import EmbeddingProvider
from app.services.embedding.ollama_provider import OllamaEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider == "ollama":
        return OllamaEmbeddingProvider()
    raise ValueError(
        f"Unsupported embedding provider: {settings.embedding_provider}"
    )