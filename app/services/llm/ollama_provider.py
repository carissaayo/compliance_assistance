import httpx

from app.config import settings


class OllamaLLMProvider:
    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        model: str = settings.llm_model,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str) -> str:
        with httpx.Client(timeout=300.0) as client:  # 5 minutes for local 8B + long context:
            response = client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
