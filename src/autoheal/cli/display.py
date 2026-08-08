"""Rich terminal display utilities for AutoHeal AI."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box

console = Console()


def show_banner() -> None:
    """Display AutoHeal AI startup banner."""
    banner = Text()
    banner.append("🏥 AutoHeal AI", style="bold cyan")
    banner.append(" — ", style="dim")
    banner.append("Autonomous Self-Healing Engine", style="italic")
    console.print(Panel(banner, border_style="cyan", box=box.DOUBLE))


def show_error_detected(
    error_type: str,
    message: str,
    file_path: str | None = None,
    line: int | None = None,
) -> None:
    """Display error detection notification."""
    location = f" at {file_path}:{line}" if file_path else ""
    console.print(f"\n[bold red]🔴 ERROR DETECTED:[/] {error_type}{location}")
    console.print(f"   [dim]{message[:200]}[/]")


def show_analyzing() -> None:
    """Display analysis in progress."""
    console.print("[bold yellow]🔍 Analyzing execution path...[/]")


def show_diagnosis(root_cause: str, confidence: float, strategy: str) -> None:
    """Display diagnosis result."""
    color = "green" if confidence >= 0.8 else "yellow" if confidence >= 0.6 else "red"
    console.print(f"[bold yellow]🔍 Root cause:[/] {root_cause}")
    console.print(
        f"[bold {color}]🔧 Fix strategy:[/] {strategy} "
        f"(Confidence: {confidence:.2f})"
    )


def show_fix_applied(description: str) -> None:
    """Display fix application."""
    console.print(f"[bold green]✅ FIX APPLIED:[/] {description}")


def show_fix_suggested(description: str, diff: str | None = None) -> None:
    """Display suggested fix (for code patches)."""
    console.print(f"\n[bold cyan]💡 FIX SUGGESTED:[/] {description}")
    if diff:
        console.print()
        console.print(Syntax(diff, "diff", theme="monokai", line_numbers=False))


def show_escalated(reason: str) -> None:
    """Display escalation to human."""
    console.print(f"[bold yellow]⚠️  ESCALATED:[/] {reason}")
    console.print("   [dim]This error requires human intervention.[/]")


def show_status_table(
    uptime: str,
    errors_caught: int,
    auto_fixed: int,
    escalated: int,
    patterns: int,
) -> None:
    """Display status report table."""
    table = Table(
        title="AutoHeal AI — Status Report",
        box=box.ROUNDED,
        border_style="cyan",
        title_style="bold cyan",
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    fix_rate = f"{(auto_fixed / errors_caught * 100):.1f}%" if errors_caught > 0 else "N/A"

    table.add_row("Uptime", uptime)
    table.add_row("Errors caught", str(errors_caught))
    table.add_row("Auto-fixed", f"{auto_fixed} ({fix_rate})")
    table.add_row("Escalated", str(escalated))
    table.add_row("Memory patterns", str(patterns))

    console.print(table)


def show_history_table(records: list[dict]) -> None:
    """Display fix history table."""
    table = Table(
        title="AutoHeal AI — Fix History",
        box=box.ROUNDED,
        border_style="cyan",
        title_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Timestamp", width=12)
    table.add_column("Error", max_width=35)
    table.add_column("Strategy", width=12)
    table.add_column("Status", width=8)

    status_icons = {
        "resolved": "✅",
        "applied": "✅",
        "failed": "❌",
        "escalated": "⚠️",
        "suggested": "💡",
        "detected": "🔵",
    }

    for i, record in enumerate(records, 1):
        status = record.get("status", "")
        icon = status_icons.get(status, "❓")
        timestamp = record.get("timestamp", "")
        if isinstance(timestamp, str) and len(timestamp) > 8:
            timestamp = timestamp[11:19] if "T" in timestamp else timestamp[:8]

        table.add_row(
            str(i),
            timestamp,
            (record.get("error_message", "") or "")[:35],
            record.get("fix_strategy", "") or record.get("category", ""),
            icon,
        )

    console.print(table)


def show_init_success(
    language: str,
    framework: str | None = None,
    project_dir: str = ".",
) -> None:
    """Display initialization success."""
    fw = f" + {framework}" if framework else ""
    console.print(f"[green]✓[/] Detected: [bold]{language}{fw}[/]")
    console.print(f"[green]✓[/] Config created: [dim].autoheal/config.toml[/]")
    console.print(f"[green]✓[/] Database initialized: [dim].autoheal/autoheal.db[/]")
    console.print(f"[green]✓[/] [bold green]AutoHeal is ready.[/]")


def show_monitoring_started(command: str) -> None:
    """Display monitoring start."""
    console.print(f"[green]🟢 Monitoring started for:[/] [bold]{command}[/]")
    console.print("[green]🟢 Sentinel Agent active[/]")
    console.print("[green]🟢 Diagnostics Engine ready[/]")


def create_spinner(message: str) -> Progress:
    """Create a Rich spinner for async operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def prompt_user_approval(description: str, diff: str | None = None) -> bool:
    """Ask user to approve a code patch."""
    console.print(
        Panel(
            f"[bold]Proposed Fix:[/] {description}",
            border_style="yellow",
            title="🔧 Code Patch Review",
        )
    )
    if diff:
        console.print(Syntax(diff, "diff", theme="monokai", line_numbers=False))
    response = console.input("\n[bold yellow]Apply this fix? (y/n): [/]")
    return response.lower().strip() in ("y", "yes")
