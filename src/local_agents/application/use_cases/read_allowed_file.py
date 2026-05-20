from pathlib import Path

from local_agents.application.ports.filesystem import FileSystemPort


class ReadAllowedFileUseCase:
    """Read file content via FileSystemPort (allowlist enforced in adapter)."""

    def __init__(self, filesystem: FileSystemPort) -> None:
        self._filesystem = filesystem

    def execute(self, path: Path) -> str:
        return self._filesystem.read_text(path)
