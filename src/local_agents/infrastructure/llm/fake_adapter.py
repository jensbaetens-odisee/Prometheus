from local_agents.application.ports.llm import LLMMessage, LLMResponse, MessageRole


class FakeLLMPort:
    """Deterministic LLM for tests and offline development."""

    def __init__(
        self,
        *,
        fixed_response: str | None = None,
        fallback_message: str | None = None,
    ) -> None:
        self._fixed_response = fixed_response
        self._fallback_message = fallback_message or "FakeLLM antwoord (stub)."

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
    ) -> LLMResponse:
        if self._fixed_response is not None:
            content = self._fixed_response
        else:
            last_user = next(
                (m.content for m in reversed(messages) if m.role == MessageRole.USER),
                "",
            )
            content = f"{self._fallback_message}\n\n(Echo: {last_user[:200]})"
        return LLMResponse(content=content, model=model or "fake")
