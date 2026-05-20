from pathlib import Path
from typing import Any

from local_agents.application.ports.filesystem import FileSystemPort
from local_agents.domain.policy import PrivacyLevel


class FileReadTool:
    """Read a text file under allowed filesystem roots."""

    name = "read_file"
    description = "Read a UTF-8 text file from an allowed project path (e.g. data/...)."
    privacy_level = PrivacyLevel.LOCAL_ONLY

    def __init__(self, filesystem: FileSystemPort, *, project_root: Path) -> None:
        self._filesystem = filesystem
        self._project_root = project_root

    def execute(self, **kwargs: Any) -> str:
        raw_path = kwargs.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError("path is required")
        path = Path(raw_path)
        if not path.is_absolute():
            path = self._project_root / path
        return self._filesystem.read_text(path)
