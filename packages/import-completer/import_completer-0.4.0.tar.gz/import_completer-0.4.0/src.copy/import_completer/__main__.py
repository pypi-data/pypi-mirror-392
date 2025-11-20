import asyncio
import sys
from pathlib import Path

import click
from loguru import logger

from import_completer.language_server import start_server


@click.group()
def cli():
    """Import Completer - Python import autocompletion language server."""
    pass


@cli.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Set the logging level (default: INFO)",
)
@click.option(
    "--log-output",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to log file. If not specified, logs to stderr.",
)
def serve(log_level: str, log_output: Path | None):
    """Start the language server."""
    # Remove default logger and configure based on options
    logger.remove()

    if log_output:
        logger.add(log_output, level=log_level.upper())
    else:
        # Log to stderr (LSP protocol uses stdout)
        logger.add(sys.stderr, level=log_level.upper())

    logger.info("Starting Import Completer language server with log level: {}", log_level.upper())

    # Run the async server
    asyncio.run(start_server())


if __name__ == "__main__":
    cli()
