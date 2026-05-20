import httpx

from local_agents.infrastructure.config.settings import OllamaSettings


class OllamaEmbeddingAdapter:
    """Embeddings via Ollama /api/embed."""

    def __init__(self, settings: OllamaSettings, *, timeout_seconds: float = 120.0) -> None:
        self._settings = settings
        self._timeout = timeout_seconds

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        payload = {"model": self._settings.embed_model, "input": text}
        url = f"{self._settings.base_url.rstrip('/')}/api/embed"
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
        embeddings = body.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            first = embeddings[0]
            if isinstance(first, list):
                return [float(x) for x in first]
        embedding = body.get("embedding")
        if isinstance(embedding, list):
            return [float(x) for x in embedding]
        raise ValueError("Ollama embed response missing embeddings")
