from pathlib import Path

from local_agents.application.coordinator.service import CoordinatorService
from local_agents.application.ports.embedding import EmbeddingPort
from local_agents.application.ports.filesystem import FileSystemPort
from local_agents.application.ports.llm import LLMPort
from local_agents.application.ports.vector_store import VectorStorePort
from local_agents.application.use_cases.ask_study_question import AskStudyQuestionUseCase
from local_agents.application.use_cases.index_courseware import IndexCoursewareUseCase
from local_agents.infrastructure.config.settings import AppSettings, load_settings
from local_agents.infrastructure.document.ingest import DocumentIngestService
from local_agents.infrastructure.embedding.fake_adapter import FakeEmbeddingAdapter
from local_agents.infrastructure.embedding.ollama_adapter import OllamaEmbeddingAdapter
from local_agents.infrastructure.filesystem.local_adapter import LocalFileSystemAdapter
from local_agents.infrastructure.llm.fake_adapter import FakeLLMPort
from local_agents.infrastructure.llm.ollama_adapter import OllamaAdapter
from local_agents.infrastructure.vector.chroma_adapter import ChromaVectorStoreAdapter
from local_agents.tools.filesystem_read import FileReadTool
from local_agents.tools.registry import ToolRegistry


class AppContainer:
    """Composition root: wires ports, tools, and application services."""

    def __init__(
        self,
        settings: AppSettings,
        *,
        llm: LLMPort | None = None,
        filesystem: FileSystemPort | None = None,
        embeddings: EmbeddingPort | None = None,
        vector_store: VectorStorePort | None = None,
    ) -> None:
        self.settings = settings
        self.filesystem = filesystem or LocalFileSystemAdapter(
            settings.filesystem,
            settings.project_root,
        )
        self.llm = llm or self._build_llm(settings)
        self.embeddings = embeddings or self._build_embeddings(settings)
        self.vector_store = vector_store or ChromaVectorStoreAdapter(
            settings.project_root / settings.study.chroma_path
        )
        self.ingest = DocumentIngestService(
            chunk_size=settings.study.chunk_size,
            chunk_overlap=settings.study.chunk_overlap,
        )
        self.index_courseware = IndexCoursewareUseCase(
            ingest=self.ingest,
            embeddings=self.embeddings,
            vector_store=self.vector_store,
        )
        self.ask_study_question = AskStudyQuestionUseCase(
            llm=self.llm,
            embeddings=self.embeddings,
            vector_store=self.vector_store,
            chat_model=settings.ollama.chat_model,
            top_k=settings.study.top_k,
            min_score=settings.study.min_score,
        )
        self.tools = ToolRegistry()
        self._register_default_tools()
        self.coordinator = CoordinatorService(
            llm=self.llm,
            tools=self.tools,
            router_model=settings.ollama.router_model,
            language=settings.coordinator.default_language,
            ask_study=self.ask_study_question,
        )

    @classmethod
    def from_config(
        cls,
        config_path: Path | None = None,
        project_root: Path | None = None,
        *,
        use_fake_llm: bool = False,
    ) -> "AppContainer":
        root = project_root or Path.cwd()
        settings = load_settings(config_path, root)
        settings.use_fake_llm = use_fake_llm
        return cls(settings)

    def _build_llm(self, settings: AppSettings) -> LLMPort:
        if settings.use_fake_llm:
            return FakeLLMPort()
        adapter = OllamaAdapter(settings.ollama)
        if adapter.is_available():
            return adapter
        return FakeLLMPort(
            fallback_message=(
                "Ollama is niet bereikbaar; FakeLLMPort actief. "
                "Start Ollama of gebruik --fake-llm."
            )
        )

    def _build_embeddings(self, settings: AppSettings) -> EmbeddingPort:
        if settings.use_fake_llm:
            return FakeEmbeddingAdapter()
        return OllamaEmbeddingAdapter(settings.ollama)

    def _register_default_tools(self) -> None:
        self.tools.register(
            FileReadTool(self.filesystem, project_root=self.settings.project_root)
        )
