"""autoheal diagnose — Manually diagnose an error."""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console

from autoheal.cli.display import show_diagnosis

console = Console()


def run_diagnose(error: str) -> None:
    """Manually diagnose an error message or file:line reference."""
    from autoheal.config.settings import AutoHealSettings
    from autoheal.diagnostics.engine import DiagnosticsEngine
    from autoheal.llm.client import LLMClient
    from autoheal.memory.store import MemoryStore

    project_dir = Path(".").resolve()
    settings = AutoHealSettings.load(project_dir)

    if not settings.llm.api_key and settings.llm.provider != "ollama":
        console.print("[red]Error: No LLM API key configured.[/]")
        console.print("[dim]Run: autoheal config set llm.api_key YOUR_KEY[/]")
        return

    llm_client = LLMClient(settings)
    db_path = project_dir / ".autoheal" / "autoheal.db"
    store = MemoryStore(db_path)
    store.initialize()

    diagnostics = DiagnosticsEngine(
        llm_client=llm_client,
        memory_store=store,
        settings=settings,
    )

    console.print(f"[bold yellow]🔍 Diagnosing:[/] {error}\n")

    result = asyncio.run(diagnostics.diagnose_manual(error))

    show_diagnosis(
        root_cause=result.root_cause,
        confidence=result.confidence,
        strategy=result.fix_strategy.value,
    )
    console.print(f"\n[dim]Explanation: {result.explanation}[/]")
    store.close()
