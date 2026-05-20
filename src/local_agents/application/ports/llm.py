from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage(BaseModel):
    role: MessageRole
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str


class LLMPort(Protocol):
    """Port for local or fake language model completion."""

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
    ) -> LLMResponse:
        """Generate a completion for the given messages."""
        ...
