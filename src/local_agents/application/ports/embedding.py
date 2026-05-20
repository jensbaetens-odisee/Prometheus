from typing import Protocol


class EmbeddingPort(Protocol):
    """Port for text embeddings (Ollama or fake)."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple document texts."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single search query."""
        ...
