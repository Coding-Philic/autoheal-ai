"""Dependency fix strategy — install missing packages."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from autoheal.cece.engine import StructuredErrorContext
from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy
from autoheal.resolution.engine import ResolutionResult, ResolutionStatus


class DependencyFixStrategy:
    """Fix dependency issues by installing missing packages."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    async def fix(
        self, diagnosis: DiagnosisResult, context: StructuredErrorContext
    ) -> ResolutionResult:
        """Attempt to fix dependency issues."""
        package_name = self._extract_package_name(context.error_message)

        if not package_name:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.DEPENDENCY_FIX,
                status=ResolutionStatus.ESCALATED,
                confidence=diagnosis.confidence,
                description="Could not determine which package to install.",
            )

        command = self._build_install_command(package_name, context.language)

        if not command:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.DEPENDENCY_FIX,
                status=ResolutionStatus.ESCALATED,
                confidence=diagnosis.confidence,
                description=(
                    f"No suitable package manager found for {context.language}."
                ),
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                return ResolutionResult(
                    error_id=diagnosis.error_id,
                    strategy=FixStrategy.DEPENDENCY_FIX,
                    status=ResolutionStatus.APPLIED,
                    confidence=diagnosis.confidence,
                    description=f"Installed package: {package_name}",
                    command_executed=command,
                )
            else:
                return ResolutionResult(
                    error_id=diagnosis.error_id,
                    strategy=FixStrategy.DEPENDENCY_FIX,
                    status=ResolutionStatus.FAILED,
                    confidence=diagnosis.confidence,
                    description=(
                        f"Package install failed: {result.stderr[:200]}"
                    ),
                    command_executed=command,
                )

        except subprocess.TimeoutExpired:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.DEPENDENCY_FIX,
                status=ResolutionStatus.FAILED,
                confidence=diagnosis.confidence,
                description="Package installation timed out.",
                command_executed=command,
            )

    def _extract_package_name(self, error_message: str) -> Optional[str]:
        """Try to extract the missing package name from error message."""
        patterns = [
            r"No module named '(\w+)'",
            r"ModuleNotFoundError: No module named '(\w+)'",
            r"ImportError: cannot import name '(\w+)'",
            r"Cannot find module '([^']+)'",
            r"Module not found: Error: Can't resolve '([^']+)'",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)

        return None

    def _build_install_command(
        self, package_name: str, language: str
    ) -> Optional[str]:
        """Build the appropriate install command."""
        if language == "python":
            if shutil.which("pip"):
                return f"pip install {package_name}"
            elif shutil.which("pip3"):
                return f"pip3 install {package_name}"
        elif language in ("javascript", "typescript"):
            if (self.project_dir / "yarn.lock").exists():
                return f"yarn add {package_name}"
            elif (self.project_dir / "pnpm-lock.yaml").exists():
                return f"pnpm add {package_name}"
            elif (self.project_dir / "bun.lockb").exists():
                return f"bun add {package_name}"
            else:
                return f"npm install {package_name}"
        elif language == "ruby":
            return f"gem install {package_name}"
        elif language == "go":
            return f"go get {package_name}"

        return None
