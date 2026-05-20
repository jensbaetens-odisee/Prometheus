from pathlib import Path

from tests.fakes.in_memory_vector_store import InMemoryVectorStore

from local_agents.application.use_cases.ask_study_question import AskStudyQuestionUseCase
from local_agents.application.use_cases.index_courseware import IndexCoursewareUseCase
from local_agents.infrastructure.document.chunking import chunk_text
from local_agents.infrastructure.document.ingest import DocumentIngestService
from local_agents.infrastructure.embedding.fake_adapter import FakeEmbeddingAdapter
from local_agents.infrastructure.llm.fake_adapter import FakeLLMPort


def test_chunk_text_overlap() -> None:
    text = "a" * 900
    chunks = chunk_text(text, chunk_size=400, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c) <= 400 for c in chunks)


def test_index_and_ask_study(tmp_path: Path) -> None:
    course_dir = tmp_path / "fysica"
    course_dir.mkdir()
    (course_dir / "notes.md").write_text(
        "Kinetische energie is 0.5 * m * v^2. Potentiele energie is m * g * h.",
        encoding="utf-8",
    )

    store = InMemoryVectorStore()
    embed = FakeEmbeddingAdapter()
    ingest = DocumentIngestService(chunk_size=200, chunk_overlap=20)
    index_uc = IndexCoursewareUseCase(ingest=ingest, embeddings=embed, vector_store=store)
    result = index_uc.execute(course_dir, "fysica")
    assert result.chunks_indexed > 0

    ask_uc = AskStudyQuestionUseCase(
        llm=FakeLLMPort(fixed_response="Kinetische energie hangt af van massa en snelheid."),
        embeddings=embed,
        vector_store=store,
        chat_model="fake",
        top_k=3,
        min_score=-1.0,
    )
    answer = ask_uc.execute("Wat is kinetische energie?", "fysica")
    assert not answer.insufficient_context
    assert len(answer.citations) >= 1
    assert "Kinetische" in answer.answer
