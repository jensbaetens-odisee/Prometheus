from pathlib import Path

import chromadb

from local_agents.domain.study import DocumentChunk, RetrievedChunk


class ChromaVectorStoreAdapter:
    """Persistent ChromaDB storage per course collection."""

    def __init__(self, persist_path: Path) -> None:
        persist_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_path))

    def _collection_name(self, course_id: str) -> str:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in course_id)
        return f"course_{safe}"

    def upsert_chunks(
        self,
        course_id: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            return 0
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        collection = self._client.get_or_create_collection(
            name=self._collection_name(course_id),
            metadata={"course_id": course_id},
        )
        collection.upsert(
            ids=[c.id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "course_id": c.course_id,
                    "source_path": c.source_path,
                    "page": c.page if c.page is not None else -1,
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ],
        )
        return len(chunks)

    def query(
        self,
        course_id: str,
        query_embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        name = self._collection_name(course_id)
        try:
            collection = self._client.get_collection(name)
        except Exception:
            return []

        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        ids = (result.get("ids") or [[]])[0]
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        retrieved: list[RetrievedChunk] = []
        for idx, doc_id in enumerate(ids):
            meta = metas[idx] if idx < len(metas) else {}
            page_raw = meta.get("page", -1)
            page = int(page_raw) if isinstance(page_raw, (int, float)) and page_raw >= 0 else None
            distance = float(distances[idx]) if idx < len(distances) else 0.0
            score = 1.0 / (1.0 + distance)
            retrieved.append(
                RetrievedChunk(
                    id=str(doc_id),
                    course_id=course_id,
                    source_path=str(meta.get("source_path", "")),
                    text=str(docs[idx]) if idx < len(docs) else "",
                    page=page,
                    chunk_index=int(meta.get("chunk_index", 0)),
                    score=score,
                )
            )
        return retrieved

    def delete_course(self, course_id: str) -> None:
        try:
            self._client.delete_collection(self._collection_name(course_id))
        except Exception:
            pass

    def list_courses(self) -> list[str]:
        courses: list[str] = []
        for col in self._client.list_collections():
            meta = col.metadata or {}
            if "course_id" in meta:
                courses.append(str(meta["course_id"]))
            elif col.name.startswith("course_"):
                courses.append(col.name.removeprefix("course_"))
        return sorted(set(courses))
