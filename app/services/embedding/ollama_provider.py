import httpx

from app.config import settings


class OllamaEmbeddingProvider:
    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        model: str = settings.embedding_model,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        with httpx.Client(timeout = 60.0) as client:
            for text in texts:
                response = client.post(
                    f"{self.base_url}/api/embeddings",
                    json= {"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                vectors.append(data['embedding'])
        return vectors