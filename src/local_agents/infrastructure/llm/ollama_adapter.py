import httpx

from local_agents.application.ports.llm import LLMMessage, LLMResponse
from local_agents.infrastructure.config.settings import OllamaSettings


class OllamaAdapter:
    """HTTP adapter for Ollama chat API."""

    def __init__(self, settings: OllamaSettings, *, timeout_seconds: float = 120.0) -> None:
        self._settings = settings
        self._timeout = timeout_seconds

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
    ) -> LLMResponse:
        chosen = model or self._settings.chat_model
        payload = {
            "model": chosen,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "stream": False,
        }
        url = f"{self._settings.base_url.rstrip('/')}/api/chat"
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
        content = str(body.get("message", {}).get("content", ""))
        return LLMResponse(content=content, model=chosen)

    def is_available(self) -> bool:
        try:
            url = f"{self._settings.base_url.rstrip('/')}/api/tags"
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                return response.status_code == 200
        except httpx.HTTPError:
            return False
