"""Shared test fixtures for AutoHeal AI tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from autoheal.config.settings import AutoHealSettings


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with sample files."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create a simple Python file
    (project_dir / "app.py").write_text(
        '''"""Sample app."""
import time


def main():
    x = None
    print(x.name)  # TypeError


if __name__ == "__main__":
    main()
'''
    )

    # Create requirements.txt
    (project_dir / "requirements.txt").write_text(
        "fastapi==0.111.0\nuvicorn==0.30.0\n"
    )

    return project_dir


@pytest.fixture
def node_project(tmp_path: Path) -> Path:
    """Create a temporary Node.js project."""
    project_dir = tmp_path / "node_project"
    project_dir.mkdir()

    (project_dir / "index.js").write_text(
        'const x = undefined;\nconsole.log(x.name);\n'
    )

    (project_dir / "package.json").write_text(
        '{"name": "test", "dependencies": {"express": "^4.18.0"}}'
    )

    return project_dir


@pytest.fixture
def mock_settings() -> AutoHealSettings:
    """Create test settings."""
    settings = AutoHealSettings()
    settings.llm.provider = "openai"
    settings.llm.api_key = "test-key"
    return settings
