from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from local_agents import __version__
from local_agents.application.use_cases.read_allowed_file import ReadAllowedFileUseCase
from local_agents.infrastructure.di.container import AppContainer
from local_agents.presentation.cli.study import register_study_commands, study_app

app = typer.Typer(
    name="local-agents",
    help="Prometheus — local agentic AI (Ollama, clean architecture).",
    no_args_is_help=True,
)
console = Console()


def _project_root() -> Path:
    return Path.cwd()


def _container(*, fake_llm: bool = False) -> AppContainer:
    return AppContainer.from_config(project_root=_project_root(), use_fake_llm=fake_llm)


@app.callback()
def main(
    ctx: typer.Context,
    fake_llm: bool = typer.Option(
        False,
        "--fake-llm",
        help="Use FakeLLMPort instead of Ollama (tests/offline).",
    ),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["fake_llm"] = fake_llm


def _fake_from_ctx(ctx: typer.Context) -> bool:
    return bool(ctx.obj.get("fake_llm", False)) if ctx.obj else False


def _get_container(ctx: typer.Context) -> AppContainer:
    return _container(fake_llm=_fake_from_ctx(ctx))


register_study_commands(_get_container)
app.add_typer(study_app, name="study")


@app.command("ask")
def ask_command(
    ctx: typer.Context,
    message: str = typer.Argument(..., help="Vraag of opdracht voor de coordinator."),
) -> None:
    """Route a message through the coordinator (Fase 0 skeleton)."""
    container = _container(fake_llm=_fake_from_ctx(ctx))
    result = container.coordinator.handle(message)
    console.print("[bold green]Coordinator[/bold green]")
    console.print(escape(result))


@app.command("tools")
def tools_command(ctx: typer.Context) -> None:
    """List registered tools."""
    container = _container(fake_llm=_fake_from_ctx(ctx))
    for tool in container.tools.list_tools():
        console.print(f"[bold]{tool.name}[/bold] ({tool.privacy_level.value}): {tool.description}")


@app.command("read-file")
def read_file_command(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Pad onder allowed root, bv. data/voorbeeld.txt"),
) -> None:
    """Read a file via FileSystemPort + allowlist."""
    container = _container(fake_llm=_fake_from_ctx(ctx))
    use_case = ReadAllowedFileUseCase(container.filesystem)
    resolved = container.filesystem.resolve_allowed(_project_root() / path)
    content = use_case.execute(resolved)
    console.print(Panel(content, title=str(path), border_style="blue"))


@app.command("version")
def version_command() -> None:
    """Show package version."""
    console.print(f"prometheus {__version__}")


def run_cli() -> None:
    app()


if __name__ == "__main__":
    run_cli()
