"""Interface for ``python -m awusb_client``."""

from collections.abc import Sequence

import typer

from . import __version__
from .client import attach_device, list_devices
from .server import CommandServer
from .usbdevice import get_devices

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
def list(
    local: bool = typer.Option(
        False,
        "--local",
        "-l",
        help="List local USB devices instead of querying the server",
    ),
) -> None:
    """List the available USB devices from the server."""
    if local:
        devices = get_devices()
    else:
        devices = list_devices()

    for device in devices:
        print(device)


@app.command()
def attach(
    id: str | None = typer.Option(None, "--id", "-d", help="Device ID e.g. 0bda:5400"),
    serial: str | None = typer.Option(
        None, "--serial", "-s", help="Device serial number"
    ),
    desc: str | None = typer.Option(
        None, "--desc", help="Device description substring"
    ),
    host: str | None = typer.Option(
        None, "--host", "-H", help="Server hostname or IP address"
    ),
    first: bool = typer.Option(
        False, "--first", "-f", help="Attach the first match if multiple found"
    ),
) -> None:
    """Attach a USB device from the server."""
    print(f"Attaching device with ID: {id}")
    result = attach_device(
        id=id,
        server_host=host if host else "localhost",
        server_port=5000,
    )

    if result.get("status") == "success":
        typer.echo("OK")
    else:
        typer.echo(f"Failed to attach device: {result.get('message', 'Unknown error')}")


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    app()


if __name__ == "__main__":
    main()
