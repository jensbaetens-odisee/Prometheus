from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    id: str
    course_id: str
    source_path: str
    text: str
    page: int | None = None
    chunk_index: int = 0


class RetrievedChunk(DocumentChunk):
    score: float = 0.0


class Citation(BaseModel):
    source_path: str
    page: int | None = None
    chunk_index: int = 0
    excerpt: str = Field(max_length=300)


class StudyAnswer(BaseModel):
    answer: str
    citations: list[Citation]
    course_id: str | None = None
    insufficient_context: bool = False
