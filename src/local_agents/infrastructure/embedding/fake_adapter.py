import hashlib
import struct


class FakeEmbeddingAdapter:
    """Deterministic fake embeddings for offline tests."""

    def __init__(self, *, dimensions: int = 32) -> None:
        self._dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        while len(values) < self._dimensions:
            for i in range(0, len(digest) - 3, 4):
                values.append(struct.unpack("!f", digest[i : i + 4])[0])
                if len(values) >= self._dimensions:
                    break
            digest = hashlib.sha256(digest).digest()
        norm = sum(v * v for v in values) ** 0.5 or 1.0
        return [v / norm for v in values]
