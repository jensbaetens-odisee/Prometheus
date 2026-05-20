from typing import Protocol

from local_agents.domain.study import DocumentChunk, RetrievedChunk


class VectorStorePort(Protocol):
    """Port for course-scoped vector storage and retrieval."""

    def upsert_chunks(
        self,
        course_id: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> int:
        """Store or replace chunks for a course collection."""
        ...

    def query(
        self,
        course_id: str,
        query_embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve the most similar chunks."""
        ...

    def delete_course(self, course_id: str) -> None:
        """Remove all chunks for a course."""
        ...

    def list_courses(self) -> list[str]:
        """Return indexed course identifiers."""
        ...
