from local_agents.application.coordinator.service import CoordinatorService
from local_agents.domain.policy import AgentIntent
from local_agents.infrastructure.llm.fake_adapter import FakeLLMPort
from local_agents.tools.registry import ToolRegistry


def test_classify_study_intent() -> None:
    service = CoordinatorService(
        llm=FakeLLMPort(fixed_response="ok"),
        tools=ToolRegistry(),
        router_model="fake",
    )
    assert service.classify_intent("Vraag over hoofdstuk 3") == AgentIntent.STUDY


def test_classify_mail_intent() -> None:
    service = CoordinatorService(
        llm=FakeLLMPort(fixed_response="ok"),
        tools=ToolRegistry(),
        router_model="fake",
    )
    assert service.classify_intent("Beantwoord deze email") == AgentIntent.MAIL


def test_handle_returns_intent_prefix() -> None:
    service = CoordinatorService(
        llm=FakeLLMPort(fixed_response="Hallo"),
        tools=ToolRegistry(),
        router_model="fake",
    )
    result = service.handle("Vraag over leerstof hoofdstuk 3")
    assert result.startswith("[intent=study]")
    assert "Hallo" in result
