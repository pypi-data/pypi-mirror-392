import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from .interpreter import ConslyricInterpreter, ConslyricRuntimeError
from .parser import (
    ConslyricParseError,
    ConslyricParser,
    ConslyricValidationError,
)

app = typer.Typer()


@app.command()
def run(
    file_path: Path = typer.Argument(..., help="Path to the lyrics.yml file"),
    debug: Optional[bool] = typer.Option(
        None,
        "-V",
        "--verbose",
        help="Enable debug logging output.",
    ),
):
    """
    Run a Conslyric file.
    """
    logging_args = {
        "format": "%(message)s",
        "datefmt": "[%X]",
        "handlers": [RichHandler()],
    }
    if debug:
        logging.basicConfig(level="DEBUG", **logging_args)
    else:
        logging.basicConfig(level="INFO", **logging_args)

    console = Console()
    try:
        parser = ConslyricParser(str(file_path))
        conslyric_data = parser.get_data()
        interpreter = ConslyricInterpreter(conslyric_data)
        interpreter.run()
    except (
        ConslyricParseError,
        ConslyricValidationError,
        ConslyricRuntimeError,
    ) as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except FileNotFoundError:
        console.print(f"[red]Error: File not found at {file_path}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        sys.exit(1)


def main():
    app()
