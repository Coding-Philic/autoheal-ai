"""Tests for the project scanner."""

from __future__ import annotations

from pathlib import Path

from autoheal.scanner.detector import ProjectDetector


class TestProjectDetector:
    """Test project language and framework detection."""

    def test_detect_python(self, temp_project: Path):
        """Detect Python project."""
        detector = ProjectDetector(temp_project)
        info = detector.detect()

        assert info["language"] == "python"
        assert "fastapi" in str(info.get("dependencies", {})).lower() or \
               info["framework"] == "FastAPI"

    def test_detect_node(self, node_project: Path):
        """Detect Node.js project."""
        detector = ProjectDetector(node_project)
        info = detector.detect()

        assert info["language"] == "javascript"
        assert info.get("framework") == "Express"

    def test_parse_requirements_txt(self, temp_project: Path):
        """Parse requirements.txt dependencies."""
        detector = ProjectDetector(temp_project)
        deps = detector._parse_requirements_txt()

        assert "fastapi" in deps
        assert deps["fastapi"] == "0.111.0"

    def test_parse_package_json(self, node_project: Path):
        """Parse package.json dependencies."""
        detector = ProjectDetector(node_project)
        deps = detector._parse_package_json()

        assert "express" in deps

    def test_unknown_project(self, tmp_path: Path):
        """Handle empty project directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        detector = ProjectDetector(empty_dir)
        info = detector.detect()

        assert info["language"] == "unknown"
        assert info["framework"] is None
