from typer.testing import CliRunner

from local_agents.presentation.cli.app import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ask" in result.stdout


def test_cli_ask_fake_llm() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--fake-llm", "ask", "Beantwoord deze email"])
    assert result.exit_code == 0
    assert "[intent=mail]" in result.stdout
