from pathlib import Path

from click.testing import CliRunner

from pybeli.cli.main import main


def test_main_system_exit_1() -> None:
    runner = CliRunner()
    args = ["--config_file", "invalid/path/to/config.yaml"]
    result = runner.invoke(main, args)
    assert result.exit_code == 1


def test_main() -> None:
    runner = CliRunner()
    test_config_file = Path(__file__).parent.parent / "files/config.yaml"
    result = runner.invoke(main, ["--config_file", str(test_config_file)])
    assert result.exit_code == 0
