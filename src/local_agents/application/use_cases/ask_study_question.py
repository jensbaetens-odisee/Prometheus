from local_agents.application.ports.embedding import EmbeddingPort
from local_agents.application.ports.llm import LLMMessage, LLMPort, MessageRole
from local_agents.application.ports.vector_store import VectorStorePort
from local_agents.domain.study import Citation, StudyAnswer


class AskStudyQuestionUseCase:
    """RAG: retrieve course chunks and answer with citations."""

    def __init__(
        self,
        *,
        llm: LLMPort,
        embeddings: EmbeddingPort,
        vector_store: VectorStorePort,
        chat_model: str,
        top_k: int = 5,
        min_score: float = 0.2,
    ) -> None:
        self._llm = llm
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._chat_model = chat_model
        self._top_k = top_k
        self._min_score = min_score

    def execute(self, question: str, course_id: str) -> StudyAnswer:
        query_vector = self._embeddings.embed_query(question)
        retrieved = self._vector_store.query(
            course_id,
            query_vector,
            top_k=self._top_k,
        )
        relevant = [c for c in retrieved if c.score >= self._min_score]

        if not relevant:
            return StudyAnswer(
                answer=(
                    "Onvoldoende context in de geindexeerde leerstof voor deze vraag. "
                    f"Indexeer eerst materiaal met: study index <pad> --name {course_id}"
                ),
                citations=[],
                course_id=course_id,
                insufficient_context=True,
            )

        context_blocks: list[str] = []
        citations: list[Citation] = []
        for i, chunk in enumerate(relevant, start=1):
            page = f"p.{chunk.page}" if chunk.page else "p.?"
            context_blocks.append(
                f"[{i}] ({chunk.source_path}, {page}, chunk {chunk.chunk_index})\n{chunk.text}"
            )
            citations.append(
                Citation(
                    source_path=chunk.source_path,
                    page=chunk.page,
                    chunk_index=chunk.chunk_index,
                    excerpt=chunk.text[:300],
                )
            )

        system = (
            "Je bent een studie-assistent. Beantwoord ALLEEN op basis van de bronnen. "
            "Citeer bronnen als [1], [2], etc. Als het antwoord niet in de bronnen staat, "
            'zeg dat expliciet. Antwoord in het Nederlands.'
        )
        user = f"Vraag: {question}\n\nBronnen:\n" + "\n\n".join(context_blocks)
        response = self._llm.complete(
            [
                LLMMessage(role=MessageRole.SYSTEM, content=system),
                LLMMessage(role=MessageRole.USER, content=user),
            ],
            model=self._chat_model,
        )
        return StudyAnswer(
            answer=response.content,
            citations=citations,
            course_id=course_id,
            insufficient_context=False,
        )
