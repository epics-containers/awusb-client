"""Interface for ``python -m awusb_client``."""

from argparse import ArgumentParser
from collections.abc import Sequence

import typer

from . import __version__
from .client import attach_device, list_devices
from .server import CommandServer

__all__ = ["main"]

app = typer.Typer()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"awusb-client {__version__}")
        raise typer.Exit()


@app.callback()
def common_options(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Common options for all commands."""
    pass


@app.command()
def server() -> None:
    """Start the USB sharing server."""
    server = CommandServer()
    server.start()


@app.command()
def client(
    action: str = typer.Argument(..., help="Action to perform: 'list' or 'attach'"),
) -> None:
    """Client commands for USB device management."""
    if action == "list":
        typer.echo(list_devices())
    elif action == "attach":
        attach_device("hello")
        print("attach called")
    else:
        typer.echo(f"Unknown action: {action}. Use 'list' or 'attach'.")
        raise typer.Exit(1)


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    app()


if __name__ == "__main__":
    main()
