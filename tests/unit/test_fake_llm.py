from local_agents.application.ports.llm import LLMMessage, MessageRole
from local_agents.infrastructure.llm.fake_adapter import FakeLLMPort


def test_fixed_response() -> None:
    llm = FakeLLMPort(fixed_response="antwoord")
    out = llm.complete([LLMMessage(role=MessageRole.USER, content="x")])
    assert out.content == "antwoord"
    assert out.model == "fake"
