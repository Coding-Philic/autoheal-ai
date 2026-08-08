"""Dependency mapper — parse dependency files for any project."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from autoheal.scanner.detector import ProjectDetector


class DependencyMapper:
    """Parse and map project dependencies."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.detector = ProjectDetector(project_dir)

    def get_dependencies(self, language: Optional[str] = None) -> dict[str, str]:
        """Get all dependencies for the project."""
        if language is None:
            info = self.detector.detect()
            language = info.get("language", "unknown")
        return self.detector._detect_dependencies(language)

    def get_package_manager(self, language: str) -> str:
        """Determine the appropriate package manager."""
        if language == "python":
            if (self.project_dir / "Pipfile").exists():
                return "pipenv"
            elif (self.project_dir / "pyproject.toml").exists():
                return "poetry"
            return "pip"
        elif language in ("javascript", "typescript"):
            if (self.project_dir / "yarn.lock").exists():
                return "yarn"
            elif (self.project_dir / "pnpm-lock.yaml").exists():
                return "pnpm"
            elif (self.project_dir / "bun.lockb").exists():
                return "bun"
            return "npm"
        elif language == "go":
            return "go mod"
        elif language == "rust":
            return "cargo"
        elif language == "ruby":
            return "bundler"
        elif language == "java":
            if (self.project_dir / "build.gradle").exists():
                return "gradle"
            return "maven"
        elif language == "php":
            return "composer"
        return "unknown"
