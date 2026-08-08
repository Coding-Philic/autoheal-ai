"""autoheal status — Show current status."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from autoheal.cli.display import show_status_table
from autoheal.memory.store import MemoryStore

console = Console()


def show_status() -> None:
    """Show AutoHeal status report."""
    project_dir = Path(".").resolve()
    db_path = project_dir / ".autoheal" / "autoheal.db"

    if not db_path.exists():
        console.print(
            "[red]Error: AutoHeal not initialized. Run 'autoheal init' first.[/]"
        )
        return

    store = MemoryStore(db_path)
    store.initialize()
    stats = store.get_statistics()
    store.close()

    show_status_table(
        uptime="N/A (not running)",
        errors_caught=stats["total_errors"],
        auto_fixed=stats["resolved"],
        escalated=stats["escalated"],
        patterns=stats["patterns"],
    )
