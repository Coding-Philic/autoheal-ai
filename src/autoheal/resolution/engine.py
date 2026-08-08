"""Resolution Engine — orchestrates fix generation and application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

from autoheal.cece.engine import StructuredErrorContext
from autoheal.config.settings import AutoHealSettings
from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy
from autoheal.llm.client import LLMClient


class ResolutionStatus(str, Enum):
    APPLIED = "applied"
    SUGGESTED = "suggested"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class PatchInfo:
    """Details of a code patch."""

    file_path: str
    original_content: str
    patched_content: str
    diff: str
    description: str


@dataclass
class ResolutionResult:
    """Result from the resolution engine."""

    error_id: str
    strategy: FixStrategy
    status: ResolutionStatus
    confidence: float
    description: str
    patch: Optional[PatchInfo] = None
    command_executed: Optional[str] = None
    rollback_ref: Optional[str] = None
    resolved_at: datetime = field(default_factory=datetime.utcnow)


class ResolutionEngine:
    """
    Orchestrates fix generation and application.

    Based on the diagnosis, selects the appropriate resolution strategy
    and either auto-applies (restart, dependency) or suggests (code patch).
    """

    def __init__(
        self,
        llm_client: LLMClient,
        project_dir: Path,
        settings: AutoHealSettings,
    ):
        self.llm_client = llm_client
        self.project_dir = project_dir
        self.settings = settings

    async def resolve(
        self,
        diagnosis: DiagnosisResult,
        context: StructuredErrorContext,
        process_restart_callback: Optional[Callable[[], Awaitable[None]]] = None,
    ) -> ResolutionResult:
        """Generate and potentially apply a fix based on the diagnosis."""
        strategy = diagnosis.fix_strategy

        # Check confidence threshold
        if diagnosis.confidence < self.settings.resolution.confidence_threshold:
            if strategy != FixStrategy.ESCALATE:
                return ResolutionResult(
                    error_id=diagnosis.error_id,
                    strategy=strategy,
                    status=ResolutionStatus.ESCALATED,
                    confidence=diagnosis.confidence,
                    description=(
                        f"Confidence ({diagnosis.confidence:.2f}) below threshold "
                        f"({self.settings.resolution.confidence_threshold}). "
                        f"Requires human review."
                    ),
                )

        # Route to appropriate strategy
        if strategy == FixStrategy.RESTART:
            return await self._handle_restart(diagnosis, process_restart_callback)
        elif strategy == FixStrategy.CODE_PATCH:
            return await self._handle_code_patch(diagnosis, context)
        elif strategy == FixStrategy.DEPENDENCY_FIX:
            return await self._handle_dependency_fix(diagnosis, context)
        elif strategy == FixStrategy.ESCALATE:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.ESCALATE,
                status=ResolutionStatus.ESCALATED,
                confidence=diagnosis.confidence,
                description=diagnosis.explanation,
            )
        else:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=strategy,
                status=ResolutionStatus.ESCALATED,
                confidence=diagnosis.confidence,
                description=(
                    f"Strategy '{strategy.value}' not yet implemented. "
                    f"{diagnosis.explanation}"
                ),
            )

    async def _handle_restart(
        self,
        diagnosis: DiagnosisResult,
        restart_callback: Optional[Callable[[], Awaitable[None]]],
    ) -> ResolutionResult:
        """Handle restart strategy."""
        if restart_callback:
            await restart_callback()
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.RESTART,
                status=ResolutionStatus.APPLIED,
                confidence=diagnosis.confidence,
                description="Process restarted.",
                command_executed="process restart",
            )
        return ResolutionResult(
            error_id=diagnosis.error_id,
            strategy=FixStrategy.RESTART,
            status=ResolutionStatus.FAILED,
            confidence=diagnosis.confidence,
            description="No restart callback available.",
        )

    async def _handle_code_patch(
        self, diagnosis: DiagnosisResult, context: StructuredErrorContext
    ) -> ResolutionResult:
        """Handle code patch strategy — generates patch, returns as suggestion."""
        from autoheal.resolution.strategies.code_patch import CodePatchStrategy

        if not context.file_path:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.CODE_PATCH,
                status=ResolutionStatus.ESCALATED,
                confidence=diagnosis.confidence,
                description="Cannot generate code patch: unknown file location.",
            )

        strategy = CodePatchStrategy(self.llm_client, self.project_dir)
        return await strategy.generate_patch(diagnosis, context)

    async def _handle_dependency_fix(
        self, diagnosis: DiagnosisResult, context: StructuredErrorContext
    ) -> ResolutionResult:
        """Handle dependency fix strategy."""
        from autoheal.resolution.strategies.dependency_fix import (
            DependencyFixStrategy,
        )

        strategy = DependencyFixStrategy(self.project_dir)
        return await strategy.fix(diagnosis, context)
