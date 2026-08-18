from app.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.ollama_provider import OllamaLLMProvider


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaLLMProvider()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
