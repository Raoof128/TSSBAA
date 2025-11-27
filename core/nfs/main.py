"""Entrypoint for running simulated NRF and NF services via Typer CLI."""
from __future__ import annotations

import typer
import uvicorn
from rich.console import Console

from .config import NFSettings, NRFSettings
from .nf_service import build_nf_app
from .nrf_service import build_nrf_app

cli = typer.Typer(help="5G SBA NF simulator")
console = Console()


@cli.command()
def nrf(
    host: str = typer.Option("0.0.0.0", help="Host for NRF"),
    port: int = typer.Option(7777, help="Port for NRF"),
    jwt_secret: str = typer.Option("change-me", help="Shared JWT secret for attestation"),
    enforce_mtls: bool = typer.Option(False, help="Require mTLS (simulated toggle)"),
) -> None:
    """Run the simulated NRF service."""

    settings = NRFSettings(jwt_secret=jwt_secret, enforce_mtls=enforce_mtls)
    app = build_nrf_app(settings)
    console.print("[blue]Starting NRF[/blue] with settings", settings)
    uvicorn.run(app, host=host, port=port)


@cli.command()
def nf(
    nf_type: str = typer.Option(..., help="NF type, e.g., AMF, SMF"),
    instance: str = typer.Option(..., help="NF instance identifier"),
    nrf_url: str = typer.Option("http://localhost:7777", help="NRF base URL"),
    host: str = typer.Option("0.0.0.0", help="Host to bind NF"),
    port: int = typer.Option(0, help="Port to bind NF"),
    jwt_secret: str = typer.Option("change-me", help="Shared JWT secret"),
    tls_enabled: bool = typer.Option(False, help="Enable HTTPS (demo flag)"),
    slices: str | None = typer.Option(None, help="Comma-separated slice identifiers"),
) -> None:
    """Run a simulated NF that registers itself with the NRF."""

    if port == 0:
        raise typer.BadParameter("Port must be set for NF service")

    settings = NFSettings(
        nf_type=nf_type.upper(),
        nf_instance_id=instance,
        nrf_url=nrf_url.rstrip("/"),
        exposed_host=host,
        exposed_port=port,
        jwt_secret=jwt_secret,
        tls_enabled=tls_enabled,
        slices=slices.split(",") if slices else ["001-data"],
    )
    console.print(
        f"[blue]Starting {settings.nf_type}[/blue] as {settings.nf_instance_id} on {host}:{port}"
    )
    uvicorn.run(build_nf_app(settings), host=host, port=port)


if __name__ == "__main__":  # pragma: no cover - CLI
    cli()
