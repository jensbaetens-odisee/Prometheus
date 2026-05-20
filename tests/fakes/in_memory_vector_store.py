import math
from collections import defaultdict

from local_agents.domain.study import DocumentChunk, RetrievedChunk


class InMemoryVectorStore:
    """Simple in-memory vector store for unit tests."""

    def __init__(self) -> None:
        self._store: dict[str, list[tuple[DocumentChunk, list[float]]]] = defaultdict(list)

    def upsert_chunks(
        self,
        course_id: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> int:
        self._store[course_id] = list(zip(chunks, embeddings, strict=True))
        return len(chunks)

    def query(
        self,
        course_id: str,
        query_embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        items = self._store.get(course_id, [])
        scored: list[RetrievedChunk] = []
        for chunk, emb in items:
            score = _cosine_similarity(query_embedding, emb)
            scored.append(RetrievedChunk(**chunk.model_dump(), score=score))
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]

    def delete_course(self, course_id: str) -> None:
        self._store.pop(course_id, None)

    def list_courses(self) -> list[str]:
        return sorted(self._store.keys())


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
