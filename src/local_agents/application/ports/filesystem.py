from pathlib import Path
from typing import Protocol


class FileSystemPort(Protocol):
    """Port for reading files within configured allowlist roots."""

    def read_text(self, path: Path, *, max_bytes: int = 1_000_000) -> str:
        """Read file contents as UTF-8 text."""
        ...

    def exists(self, path: Path) -> bool:
        """Return True if the path exists and is allowed."""
        ...

    def resolve_allowed(self, path: Path) -> Path:
        """Resolve path and ensure it lies under an allowed root."""
        ...
