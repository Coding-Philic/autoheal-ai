"""autoheal run — Run a command with AutoHeal monitoring."""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console

console = Console()


def run_command(command: str, verbose: bool = False) -> None:
    """Run a command with AutoHeal monitoring."""
    from autoheal.cli.display import show_banner, show_monitoring_started
    from autoheal.config.settings import AutoHealSettings
    from autoheal.orchestrator.engine import OrchestratorEngine

    project_dir = Path(".").resolve()
    autoheal_dir = project_dir / ".autoheal"

    # Check if initialized
    if not autoheal_dir.exists():
        console.print(
            "[red]Error: AutoHeal not initialized. Run 'autoheal init' first.[/]"
        )
        raise SystemExit(1)

    # Load settings
    settings = AutoHealSettings.load(project_dir)
    if verbose:
        settings.general.verbose = True

    # Check LLM API key
    if not settings.llm.api_key and settings.llm.provider != "ollama":
        console.print(
            f"[yellow]⚠️  No API key set for provider '{settings.llm.provider}'.[/]"
        )
        console.print(
            "[dim]Set it via: autoheal config set llm.api_key YOUR_KEY[/]"
        )
        console.print(
            "[dim]Or use local models: autoheal config set llm.provider ollama[/]"
        )
        console.print()
        console.print("[dim]Continuing in detect-only mode (no AI diagnosis)...[/]")

    show_banner()
    show_monitoring_started(command)
    console.print()

    # Start orchestrator (main event loop)
    orchestrator = OrchestratorEngine(
        command=command,
        project_dir=project_dir,
        settings=settings,
    )

    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]AutoHeal stopped by user.[/]")
