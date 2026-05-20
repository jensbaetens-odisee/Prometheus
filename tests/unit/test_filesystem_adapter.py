from pathlib import Path

import pytest

from local_agents.domain.exceptions import PathNotAllowed
from local_agents.infrastructure.config.settings import FileSystemSettings
from local_agents.infrastructure.filesystem.local_adapter import LocalFileSystemAdapter


def test_read_allowed_file(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    sample = data_dir / "note.txt"
    sample.write_text("hello", encoding="utf-8")
    adapter = LocalFileSystemAdapter(FileSystemSettings(allowed_roots=["data"]), tmp_path)
    assert adapter.read_text(sample) == "hello"


def test_reject_path_outside_root(tmp_path: Path) -> None:
    outside = tmp_path / "outside.txt"
    outside.write_text("nope", encoding="utf-8")
    adapter = LocalFileSystemAdapter(FileSystemSettings(allowed_roots=["data"]), tmp_path)
    with pytest.raises(PathNotAllowed):
        adapter.read_text(outside)
