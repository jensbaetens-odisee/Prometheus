from pathlib import Path

from local_agents.infrastructure.di.container import AppContainer
from local_agents.infrastructure.llm.fake_adapter import FakeLLMPort


def test_container_uses_fake_llm_when_requested(tmp_path: Path) -> None:
    config = tmp_path / "config"
    config.mkdir()
    (config / "default.yaml").write_text(
        "filesystem:\n  allowed_roots:\n    - data\n",
        encoding="utf-8",
    )
    container = AppContainer.from_config(
        config_path=config / "default.yaml",
        project_root=tmp_path,
        use_fake_llm=True,
    )
    assert isinstance(container.llm, FakeLLMPort)
    assert container.tools.get("read_file").name == "read_file"
