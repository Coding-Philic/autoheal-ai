"""autoheal init — Initialize AutoHeal in a project directory."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def run_init(path: str = ".") -> None:
    """Initialize AutoHeal AI in the given project directory."""
    from autoheal.cli.display import show_banner, show_init_success
    from autoheal.config.settings import AutoHealSettings
    from autoheal.memory.store import MemoryStore
    from autoheal.scanner.detector import ProjectDetector

    project_dir = Path(path).resolve()

    if not project_dir.exists():
        console.print(f"[red]Error: Directory '{path}' does not exist.[/]")
        raise SystemExit(1)

    show_banner()
    console.print(f"[dim]Initializing AutoHeal in: {project_dir}[/]\n")

    # Step 1: Scan project
    detector = ProjectDetector(project_dir)
    project_info = detector.detect()

    # Step 2: Create .autoheal/ directory and config
    autoheal_dir = project_dir / ".autoheal"
    autoheal_dir.mkdir(exist_ok=True)

    settings = AutoHealSettings()
    settings.save(project_dir)

    # Step 3: Initialize database
    store = MemoryStore(autoheal_dir / "autoheal.db")
    store.initialize()
    store.close()

    # Step 4: Add .autoheal/ to .gitignore if git project
    gitignore = project_dir / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".autoheal/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# AutoHeal AI\n.autoheal/\n")
    else:
        gitignore.write_text("# AutoHeal AI\n.autoheal/\n")

    show_init_success(
        language=project_info.get("language", "Unknown"),
        framework=project_info.get("framework"),
        project_dir=str(project_dir),
    )
