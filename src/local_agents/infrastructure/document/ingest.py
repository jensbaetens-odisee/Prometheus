from pathlib import Path

from local_agents.domain.study import DocumentChunk
from local_agents.infrastructure.document.chunking import chunk_text

_SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md", ".markdown"}


class DocumentIngestService:
    """Extract text from supported files and build document chunks."""

    def __init__(self, *, chunk_size: int = 800, chunk_overlap: int = 100) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def collect_chunks(self, course_id: str, source_dir: Path) -> list[DocumentChunk]:
        if not source_dir.is_dir():
            raise NotADirectoryError(source_dir)

        chunks: list[DocumentChunk] = []
        for file_path in sorted(source_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in _SUPPORTED_SUFFIXES:
                continue
            pages = self._extract_pages(file_path)
            for page_num, page_text in pages:
                for idx, piece in enumerate(
                    chunk_text(
                        page_text,
                        chunk_size=self._chunk_size,
                        overlap=self._chunk_overlap,
                    )
                ):
                    chunk_id = f"{course_id}:{file_path.name}:{page_num}:{idx}"
                    chunks.append(
                        DocumentChunk(
                            id=chunk_id,
                            course_id=course_id,
                            source_path=str(file_path),
                            text=piece,
                            page=page_num,
                            chunk_index=idx,
                        )
                    )
        return chunks

    def _extract_pages(self, path: Path) -> list[tuple[int | None, str]]:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        return [(None, text)]

    def _extract_pdf(self, path: Path) -> list[tuple[int | None, str]]:
        import fitz  # pymupdf

        doc = fitz.open(path)
        pages: list[tuple[int | None, str]] = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                pages.append((i + 1, text))
        doc.close()
        return pages if pages else [(None, "")]
