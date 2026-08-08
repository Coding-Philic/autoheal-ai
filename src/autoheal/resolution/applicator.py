"""Patch applicator — apply code patches with git backup."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class PatchApplicator:
    """Apply code patches to files with git rollback support."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def create_rollback_point(
        self, message: str = "AutoHeal: pre-fix backup"
    ) -> Optional[str]:
        """Create a git commit as a rollback point. Returns commit hash or None."""
        try:
            import git

            repo = git.Repo(str(self.project_dir))

            # Stage all changes
            repo.git.add("-A")

            # Only commit if there are changes
            if repo.is_dirty(untracked_files=True):
                commit = repo.index.commit(message)
                return str(commit.hexsha)[:8]

            return str(repo.head.commit.hexsha)[:8]
        except Exception:
            return None

    def apply_patch(self, file_path: str, patched_content: str) -> bool:
        """Apply patched content to a file."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_dir / path

        try:
            path.write_text(patched_content)
            return True
        except Exception as e:
            console.print(f"[red]Error applying patch: {e}[/]")
            return False

    def rollback(self, commit_hash: str) -> bool:
        """Rollback to a specific git commit."""
        try:
            import git

            repo = git.Repo(str(self.project_dir))
            repo.git.checkout(commit_hash, "--", ".")
            return True
        except Exception as e:
            console.print(f"[red]Error rolling back: {e}[/]")
            return False
