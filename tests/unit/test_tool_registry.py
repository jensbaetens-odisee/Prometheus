from local_agents.domain.policy import PrivacyLevel
from local_agents.tools.filesystem_read import FileReadTool
from local_agents.tools.registry import ToolRegistry


def test_register_and_execute(tmp_path, monkeypatch) -> None:
    from local_agents.infrastructure.config.settings import FileSystemSettings
    from local_agents.infrastructure.filesystem.local_adapter import LocalFileSystemAdapter

    data = tmp_path / "data"
    data.mkdir()
    (data / "a.txt").write_text("inhoud", encoding="utf-8")
    fs = LocalFileSystemAdapter(FileSystemSettings(allowed_roots=["data"]), tmp_path)
    registry = ToolRegistry()
    registry.register(FileReadTool(fs, project_root=tmp_path))
    tool = registry.get("read_file")
    assert tool.privacy_level == PrivacyLevel.LOCAL_ONLY
    result = tool.execute(path="data/a.txt")
    assert result == "inhoud"
