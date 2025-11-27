from typer.testing import CliRunner

from core.nfs import main

runner = CliRunner()


def test_cli_shows_commands() -> None:
    result = runner.invoke(main.cli, ["--help"])
    assert result.exit_code == 0
    assert "nrf" in result.stdout
    assert "nf" in result.stdout


def test_nf_requires_port() -> None:
    result = runner.invoke(
        main.cli,
        [
            "nf",
            "--nf-type",
            "amf",
            "--instance",
            "amf-1",
            "--nrf-url",
            "http://localhost:7777",
        ],
    )
    assert result.exit_code != 0
    assert "Port must be set" in result.stderr
