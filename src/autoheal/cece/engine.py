"""CECE Engine — Contextual Error Comprehension Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from autoheal.cece.code_reader import read_code_context
from autoheal.cece.env_capture import capture_environment, detect_runtime_version
from autoheal.scanner.detector import ProjectDetector
from autoheal.sentinel.agent import ErrorEvent


@dataclass
class StructuredErrorContext:
    """Structured Error Context Document (SECD)."""

    error_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "P2"
    category: str = "unknown"
    error_type: str = ""
    error_message: str = ""
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    stack_trace: str = ""
    code_context: Optional[str] = None
    language: str = "unknown"
    framework: Optional[str] = None
    dependencies: dict = field(default_factory=dict)
    environment: dict = field(default_factory=dict)
    runtime_version: Optional[str] = None
    raw_output: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "category": self.category,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "stack_trace": self.stack_trace,
            "code_context": self.code_context,
            "language": self.language,
            "framework": self.framework,
            "dependencies": self.dependencies,
            "environment": self.environment,
            "runtime_version": self.runtime_version,
        }


class CECEEngine:
    """
    Contextual Error Comprehension Engine.

    Takes a raw ErrorEvent from the Sentinel and builds a complete
    Structured Error Context Document (SECD) for the Diagnostics Engine.
    """

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self._project_info: Optional[dict] = None

    def _get_project_info(self) -> dict:
        """Lazy-load project info."""
        if self._project_info is None:
            detector = ProjectDetector(self.project_dir)
            self._project_info = detector.detect()
        return self._project_info

    async def build_context(self, error: ErrorEvent) -> StructuredErrorContext:
        """Build a complete SECD from an ErrorEvent."""
        ctx = StructuredErrorContext()

        # Error details
        ctx.error_id = error.error_id
        ctx.timestamp = error.timestamp
        ctx.severity = error.severity
        ctx.category = error.category
        ctx.error_type = error.error_type
        ctx.error_message = error.message
        ctx.file_path = error.file_path
        ctx.line_number = error.line_number
        ctx.stack_trace = error.stack_trace
        ctx.raw_output = error.raw_output

        # Code context (read source around error line)
        if error.file_path and error.line_number:
            ctx.code_context = read_code_context(
                error.file_path,
                error.line_number,
                context_lines=15,
                project_dir=str(self.project_dir),
            )

        # Project info
        project_info = self._get_project_info()
        ctx.language = error.language or project_info.get("language", "unknown")
        ctx.framework = project_info.get("framework")
        ctx.dependencies = project_info.get("dependencies", {})

        # Environment
        ctx.environment = capture_environment()
        ctx.runtime_version = detect_runtime_version(ctx.language)

        return ctx
