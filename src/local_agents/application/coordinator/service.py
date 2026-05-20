import re

from local_agents.application.ports.llm import LLMMessage, LLMPort, MessageRole
from local_agents.application.use_cases.ask_study_question import AskStudyQuestionUseCase
from local_agents.domain.policy import AgentIntent
from local_agents.tools.registry import ToolRegistry

_INTENT_PATTERNS: list[tuple[re.Pattern[str], AgentIntent]] = [
    (re.compile(r"\b(mail|e-?mail|inbox|bericht)\b", re.I), AgentIntent.MAIL),
    (re.compile(r"\b(studie|leerstof|cursus|hoofdstuk|exam)\b", re.I), AgentIntent.STUDY),
    (re.compile(r"\b(map|mappen|syllabus|vak|admin)\b", re.I), AgentIntent.ADMIN),
]


class CoordinatorService:
    """Routes requests and produces a first response (Fase 0 skeleton)."""

    def __init__(
        self,
        *,
        llm: LLMPort,
        tools: ToolRegistry,
        router_model: str,
        language: str = "nl",
        ask_study: AskStudyQuestionUseCase | None = None,
        default_course_id: str | None = None,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._router_model = router_model
        self._language = language
        self._ask_study = ask_study
        self._default_course_id = default_course_id

    def classify_intent(self, message: str) -> AgentIntent:
        for pattern, intent in _INTENT_PATTERNS:
            if pattern.search(message):
                return intent
        return AgentIntent.GENERAL

    def handle(self, message: str, *, course_id: str | None = None) -> str:
        intent = self.classify_intent(message)
        if intent == AgentIntent.STUDY and self._ask_study is not None:
            resolved_course = course_id or self._default_course_id
            if resolved_course:
                study_answer = self._ask_study.execute(message, resolved_course)
                cites = "; ".join(
                    f"{c.source_path} p.{c.page or '?'}" for c in study_answer.citations[:3]
                )
                prefix = f"[intent=study][course={resolved_course}]"
                if study_answer.insufficient_context:
                    return f"{prefix}\n{study_answer.answer}"
                cite_line = f"\n\nBronnen: {cites}" if cites else ""
                return f"{prefix}\n{study_answer.answer}{cite_line}"

        system = (
            f"Je bent de Prometheus coordinator. Taal: {self._language}. "
            f"Geclassificeerde intent: {intent.value}. "
            f"Beschikbare tools:\n{self._tools.describe_for_prompt()}\n"
            "Geef een kort, behulpzaam antwoord. Specialized agents komen in latere fases."
        )
        response = self._llm.complete(
            [
                LLMMessage(role=MessageRole.SYSTEM, content=system),
                LLMMessage(role=MessageRole.USER, content=message),
            ],
            model=self._router_model,
        )
        return f"[intent={intent.value}]\n{response.content}"
