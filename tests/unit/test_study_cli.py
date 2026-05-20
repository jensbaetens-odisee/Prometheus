from typer.testing import CliRunner

from local_agents.presentation.cli.app import app


def test_study_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["study", "--help"])
    assert result.exit_code == 0
    assert "index" in result.stdout
    assert "ask" in result.stdout


def test_study_index_and_ask(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    course = tmp_path / "wiskunde"
    course.mkdir()
    (course / "les.txt").write_text("Een afgeleide meet de veranderingssnelheid.", encoding="utf-8")

    runner = CliRunner()
    index = runner.invoke(
        app,
        ["--fake-llm", "study", "index", str(course), "--name", "wiskunde"],
    )
    assert index.exit_code == 0, index.stdout
    assert "chunks=" in index.stdout

    ask = runner.invoke(
        app,
        ["--fake-llm", "study", "ask", "Wat is een afgeleide?", "--course", "wiskunde"],
    )
    assert ask.exit_code == 0, ask.stdout
    assert "Bronnen" in ask.stdout or "afgeleide" in ask.stdout.lower()
