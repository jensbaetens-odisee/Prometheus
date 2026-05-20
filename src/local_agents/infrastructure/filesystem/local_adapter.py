from pathlib import Path

from local_agents.domain.exceptions import PathNotAllowed
from local_agents.infrastructure.config.settings import FileSystemSettings


class LocalFileSystemAdapter:
    """Reads files only under configured project-relative roots."""

    def __init__(self, settings: FileSystemSettings, project_root: Path) -> None:
        self._roots = [
            (project_root / Path(root)).resolve()
            for root in settings.allowed_roots
        ]

    def resolve_allowed(self, path: Path) -> Path:
        candidate = path.resolve()
        for root in self._roots:
            try:
                candidate.relative_to(root)
                return candidate
            except ValueError:
                continue
        roots_display = ", ".join(str(r) for r in self._roots)
        raise PathNotAllowed(f"Path {path} is not under allowed roots: {roots_display}")

    def exists(self, path: Path) -> bool:
        try:
            resolved = self.resolve_allowed(path)
        except PathNotAllowed:
            return False
        return resolved.is_file()

    def read_text(self, path: Path, *, max_bytes: int = 1_000_000) -> str:
        resolved = self.resolve_allowed(path)
        if not resolved.is_file():
            raise FileNotFoundError(resolved)
        raw = resolved.read_bytes()
        if len(raw) > max_bytes:
            raise ValueError(f"File exceeds max_bytes={max_bytes}")
        return raw.decode("utf-8")
