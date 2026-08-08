"""Main CLI application for AutoHeal AI."""

from __future__ import annotations

import typer
from rich.console import Console

from autoheal import __version__, __app_name__

app = typer.Typer(
    name="autoheal",
    help="🏥 AutoHeal AI — Autonomous Self-Healing Software Engine",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)

console = Console()


@app.command()
def version() -> None:
    """Show AutoHeal AI version."""
    console.print(f"[bold green]{__app_name__}[/] v{__version__}")


@app.command()
def init(
    path: str = typer.Argument(".", help="Project directory to initialize"),
) -> None:
    """Initialize AutoHeal in a project directory."""
    from autoheal.cli.commands.init_cmd import run_init

    run_init(path)


@app.command()
def run(
    command: str = typer.Argument(..., help="Command to run and monitor"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run a command with AutoHeal monitoring."""
    from autoheal.cli.commands.run_cmd import run_command

    run_command(command, verbose)


@app.command()
def status() -> None:
    """Show current AutoHeal status."""
    from autoheal.cli.commands.status_cmd import show_status

    show_status()


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries to show"),
) -> None:
    """Show error fix history."""
    from autoheal.cli.commands.history_cmd import show_history

    show_history(limit)


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: get, set, list"),
    key: str = typer.Argument(None, help="Config key (e.g., llm.provider)"),
    value: str = typer.Argument(None, help="Config value"),
) -> None:
    """View or modify AutoHeal configuration."""
    from autoheal.cli.commands.config_cmd import manage_config

    manage_config(action, key, value)


@app.command()
def diagnose(
    error: str = typer.Argument(..., help="Error message or file:line to diagnose"),
) -> None:
    """Manually diagnose an error using AI."""
    from autoheal.cli.commands.diagnose_cmd import run_diagnose

    run_diagnose(error)


def main() -> None:
    """Entry point for the CLI."""
    app()
