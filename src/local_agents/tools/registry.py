from typing import Any, Protocol

from local_agents.domain.policy import PrivacyLevel


class Tool(Protocol):
    name: str
    description: str
    privacy_level: PrivacyLevel

    def execute(self, **kwargs: Any) -> str:
        """Run the tool with keyword arguments."""
        ...


class ToolRegistry:
    """Registry of tools available to agents and the coordinator."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def describe_for_prompt(self) -> str:
        lines = [f"- {t.name}: {t.description}" for t in self.list_tools()]
        return "\n".join(lines) if lines else "(geen tools)"
