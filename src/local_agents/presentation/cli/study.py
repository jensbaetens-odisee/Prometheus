from collections.abc import Callable
from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from local_agents.infrastructure.di.container import AppContainer

study_app = typer.Typer(help="Study agent: indexeer leerstof en stel vragen (RAG).")
console = Console()


def register_study_commands(
    get_container: Callable[[typer.Context], AppContainer],
) -> None:
    """Register study commands with shared container factory."""

    @study_app.command("index")
    def study_index(
        ctx: typer.Context,
        path: str = typer.Argument(..., help="Map met PDF/txt/md"),
        name: str | None = typer.Option(None, "--name", "-n", help="Course ID (default: mapnaam)"),
        replace: bool = typer.Option(
            False,
            "--replace",
            help="Bestaande index voor course vervangen",
        ),
    ) -> None:
        """Indexeer leerstof uit een map."""
        container: AppContainer = get_container(ctx)
        source = Path(path).resolve()
        course_id = name or source.name
        result = container.index_courseware.execute(source, course_id, replace=replace)
        console.print(
            f"[green]Geindexeerd[/green]: course={result.course_id}, "
            f"bestanden={result.files_processed}, chunks={result.chunks_indexed}"
        )

    @study_app.command("ask")
    def study_ask(
        ctx: typer.Context,
        question: str = typer.Argument(..., help="Vraag over de leerstof"),
        course: str = typer.Option(..., "--course", "-c", help="Course ID uit study index"),
    ) -> None:
        """Stel een vraag met RAG + bronvermelding."""
        container: AppContainer = get_container(ctx)
        answer = container.ask_study_question.execute(question, course)
        console.print(f"[bold blue]Studie[/bold blue] [dim]({course})[/dim]")
        console.print(escape(answer.answer))
        if answer.citations:
            table = Table(title="Bronnen")
            table.add_column("#", style="dim")
            table.add_column("Bestand")
            table.add_column("Pagina")
            table.add_column("Excerpt")
            for i, cite in enumerate(answer.citations, start=1):
                table.add_row(
                    str(i),
                    Path(cite.source_path).name,
                    str(cite.page or "?"),
                    cite.excerpt[:120] + ("..." if len(cite.excerpt) > 120 else ""),
                )
            console.print(table)

    @study_app.command("repl")
    def study_repl(
        ctx: typer.Context,
        course: str = typer.Option(..., "--course", "-c", help="Course ID"),
    ) -> None:
        """Interactieve studie-sessie (meerdere vragen)."""
        container: AppContainer = get_container(ctx)
        console.print(f"[dim]Studie REPL voor course={course}. Typ 'exit' om te stoppen.[/dim]")
        while True:
            try:
                question = console.input("[bold]> [/bold]").strip()
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
            if not question:
                continue
            if question.lower() in {"exit", "quit", "q"}:
                break
            answer = container.ask_study_question.execute(question, course)
            console.print(escape(answer.answer))
            if answer.citations:
                console.print(f"[dim]{len(answer.citations)} bron(nen)[/dim]\n")
