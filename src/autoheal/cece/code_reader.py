"""Read source code around an error location."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def read_code_context(
    file_path: str,
    line_number: int,
    context_lines: int = 10,
    project_dir: str = ".",
) -> Optional[str]:
    """
    Read source code around the error line.
    Returns ±context_lines around the error line with line numbers.
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(project_dir) / path

    if not path.exists():
        return None

    try:
        lines = path.read_text(errors="replace").splitlines()
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)

        result_lines: list[str] = []
        for i in range(start, end):
            line_num = i + 1
            marker = " >>> " if line_num == line_number else "     "
            result_lines.append(f"{line_num:4d}{marker}{lines[i]}")

        return "\n".join(result_lines)
    except Exception:
        return None


def read_full_file(file_path: str, project_dir: str = ".") -> Optional[str]:
    """Read the full content of a source file."""
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(project_dir) / path

    if not path.exists():
        return None

    try:
        return path.read_text(errors="replace")
    except Exception:
        return None
