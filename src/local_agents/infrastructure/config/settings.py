from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from local_agents.domain.policy import PrivacyLevel


class OllamaSettings(BaseModel):
    base_url: str = "http://127.0.0.1:11434"
    chat_model: str = "llama3.1:8b"
    router_model: str = "llama3.2:3b"
    embed_model: str = "nomic-embed-text"


class FileSystemSettings(BaseModel):
    allowed_roots: list[str] = Field(default_factory=lambda: ["data"])


class PrivacySettings(BaseModel):
    default_level: PrivacyLevel = PrivacyLevel.LOCAL_ONLY
    allow_online_tools: bool = False
    require_approval_for: list[str] = Field(default_factory=list)


class CoordinatorSettings(BaseModel):
    default_language: str = "nl"


class StudySettings(BaseModel):
    chroma_path: str = "data/chroma"
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    min_score: float = 0.2


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROMETHEUS_", extra="ignore")

    project_root: Path = Field(default_factory=lambda: Path.cwd())
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    filesystem: FileSystemSettings = Field(default_factory=FileSystemSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    coordinator: CoordinatorSettings = Field(default_factory=CoordinatorSettings)
    study: StudySettings = Field(default_factory=StudySettings)
    use_fake_llm: bool = False


def load_settings(config_path: Path | None = None, project_root: Path | None = None) -> AppSettings:
    root = project_root or Path.cwd()
    path = config_path or root / "config" / "default.yaml"
    data: dict[str, object] = {}
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
            if isinstance(raw, dict):
                data = raw

    merged: dict[str, object] = {
        "project_root": root,
        "ollama": _section(data, "ollama"),
        "filesystem": _section(data, "filesystem"),
        "privacy": _section(data, "privacy"),
        "coordinator": _section(data, "coordinator"),
        "study": _section(data, "study"),
    }
    return AppSettings.model_validate(merged)


def _section(
    data: dict[str, object],
    key: str,
    override: dict[str, object] | None = None,
) -> dict[str, object]:
    if override is not None:
        return override
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}
