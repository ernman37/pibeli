from pathlib import Path

import click

from pybeli.models.config import Config


@click.command()
@click.option(
    "-c",
    "--config_file",
    default="config/config.yaml",
    help="Path to the configuration file.",
)
def main(
    config_file: str,
) -> None:
    """
    Main entry point for the PyBeli CLI.
    """
    config_path = Path(config_file)
    if not config_path.is_file():
        click.echo(f"Configuration file not found: {config_path}")
        SystemExit(1)
    config = Config.from_file(config_path)
    print(config)
