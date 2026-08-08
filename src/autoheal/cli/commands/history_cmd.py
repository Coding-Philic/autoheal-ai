"""autoheal history — Show fix history."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from autoheal.cli.display import show_history_table
from autoheal.memory.store import MemoryStore

console = Console()


def show_history(limit: int = 20) -> None:
    """Show error fix history."""
    project_dir = Path(".").resolve()
    db_path = project_dir / ".autoheal" / "autoheal.db"

    if not db_path.exists():
        console.print(
            "[red]Error: AutoHeal not initialized. Run 'autoheal init' first.[/]"
        )
        return

    store = MemoryStore(db_path)
    store.initialize()
    records = store.get_history(limit=limit)
    store.close()

    if not records:
        console.print("[dim]No error history yet. Run your app with 'autoheal run' first.[/]")
        return

    show_history_table(records)
