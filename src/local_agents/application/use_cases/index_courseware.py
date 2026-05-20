from dataclasses import dataclass
from pathlib import Path

from local_agents.application.ports.embedding import EmbeddingPort
from local_agents.application.ports.vector_store import VectorStorePort
from local_agents.infrastructure.document.ingest import DocumentIngestService


@dataclass(frozen=True)
class IndexCoursewareResult:
    course_id: str
    source_dir: Path
    files_processed: int
    chunks_indexed: int


class IndexCoursewareUseCase:
    """Index documents from a directory into the vector store for a course."""

    def __init__(
        self,
        *,
        ingest: DocumentIngestService,
        embeddings: EmbeddingPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._ingest = ingest
        self._embeddings = embeddings
        self._vector_store = vector_store

    def execute(
        self,
        source_dir: Path,
        course_id: str,
        *,
        replace: bool = False,
    ) -> IndexCoursewareResult:
        if replace:
            self._vector_store.delete_course(course_id)

        chunks = self._ingest.collect_chunks(course_id, source_dir)
        if not chunks:
            return IndexCoursewareResult(
                course_id=course_id,
                source_dir=source_dir,
                files_processed=0,
                chunks_indexed=0,
            )

        vectors = self._embeddings.embed_documents([c.text for c in chunks])
        count = self._vector_store.upsert_chunks(course_id, chunks, vectors)
        unique_files = len({c.source_path for c in chunks})
        return IndexCoursewareResult(
            course_id=course_id,
            source_dir=source_dir,
            files_processed=unique_files,
            chunks_indexed=count,
        )
