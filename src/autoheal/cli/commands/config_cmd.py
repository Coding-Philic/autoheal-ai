"""autoheal config — View or modify configuration."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def manage_config(action: str, key: str | None = None, value: str | None = None) -> None:
    """Manage AutoHeal configuration."""
    from autoheal.config.settings import AutoHealSettings

    project_dir = Path(".").resolve()

    if action == "list":
        settings = AutoHealSettings.load(project_dir)
        data = settings.model_dump()
        table = Table(
            title="AutoHeal Configuration",
            box=box.ROUNDED,
            border_style="cyan",
        )
        table.add_column("Key", style="bold")
        table.add_column("Value")

        for section_name, section in data.items():
            if isinstance(section, dict):
                for k, v in section.items():
                    display_val = "****" if "key" in k.lower() and v else str(v)
                    table.add_row(f"{section_name}.{k}", display_val)

        console.print(table)

    elif action == "get":
        if not key:
            console.print("[red]Usage: autoheal config get <key>[/]")
            return
        settings = AutoHealSettings.load(project_dir)
        val = settings.get_nested(key)
        if val is not None:
            display_val = "****" if "key" in key.lower() and val else str(val)
            console.print(f"[bold]{key}[/] = {display_val}")
        else:
            console.print(f"[red]Unknown config key: {key}[/]")

    elif action == "set":
        if not key or value is None:
            console.print("[red]Usage: autoheal config set <key> <value>[/]")
            return

        autoheal_dir = project_dir / ".autoheal"
        if not autoheal_dir.exists():
            console.print(
                "[red]Error: AutoHeal not initialized. Run 'autoheal init' first.[/]"
            )
            return

        settings = AutoHealSettings.load(project_dir)
        settings.set_nested(key, value)
        settings.save(project_dir)
        display_val = "****" if "key" in key.lower() else value
        console.print(f"[green]✓[/] Set [bold]{key}[/] = {display_val}")

    else:
        console.print(f"[red]Unknown action: {action}. Use: list, get, set[/]")
