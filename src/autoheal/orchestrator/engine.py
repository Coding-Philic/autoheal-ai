"""Orchestrator Engine — main state machine coordinating all components."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from rich.console import Console

from autoheal.cece.engine import CECEEngine
from autoheal.cli.display import (
    prompt_user_approval,
    show_analyzing,
    show_error_detected,
    show_diagnosis,
    show_escalated,
    show_fix_applied,
    show_fix_suggested,
)
from autoheal.config.settings import AutoHealSettings
from autoheal.diagnostics.engine import DiagnosticsEngine
from autoheal.harness.controller import HarnessController
from autoheal.llm.client import LLMClient
from autoheal.memory.store import MemoryStore
from autoheal.resolution.applicator import PatchApplicator
from autoheal.resolution.engine import ResolutionEngine, ResolutionStatus
from autoheal.scanner.detector import ProjectDetector
from autoheal.sentinel.agent import ErrorEvent, SentinelAgent

console = Console()


class OrchestratorState(str, Enum):
    IDLE = "idle"
    MONITORING = "monitoring"
    TRIAGING = "triaging"
    ANALYZING = "analyzing"
    RESOLVING = "resolving"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    LEARNING = "learning"
    ESCALATED = "escalated"


class OrchestratorEngine:
    """
    Central orchestrator that coordinates the full error resolution pipeline:

    Sentinel → CECE → Diagnostics → Resolution → Harness → Memory
    """

    def __init__(
        self,
        command: str,
        project_dir: Path,
        settings: AutoHealSettings,
    ):
        self.command = command
        self.project_dir = project_dir
        self.settings = settings
        self.state = OrchestratorState.IDLE

        # Detect project
        detector = ProjectDetector(project_dir)
        self.project_info = detector.detect()

        # Initialize components
        self.llm_client = LLMClient(settings)
        self.memory_store = MemoryStore(project_dir / ".autoheal" / "autoheal.db")
        self.memory_store.initialize()

        self.cece = CECEEngine(project_dir)
        self.diagnostics = DiagnosticsEngine(
            self.llm_client, self.memory_store, settings
        )
        self.resolution = ResolutionEngine(
            self.llm_client, project_dir, settings
        )
        self.harness = HarnessController(settings)
        self.applicator = PatchApplicator(project_dir)

        # Sentinel setup
        self.sentinel = SentinelAgent(
            command=command,
            project_dir=project_dir,
            settings=settings,
            language=self.project_info.get("language", "unknown"),
            on_error=self._handle_error,
        )

    async def start(self) -> None:
        """Start the orchestrator — begins monitoring."""
        self.state = OrchestratorState.MONITORING

        memory_count = self.memory_store.get_statistics()["patterns"]
        console.print(
            f"[green]🟢 Memory Store: {memory_count} patterns loaded[/]"
        )
        console.print()

        # Start sentinel (blocks until process exits)
        await self.sentinel.start()

        # Clean up
        self.memory_store.close()

    async def _handle_error(self, error: ErrorEvent) -> None:
        """
        Main error handling pipeline.
        Called by the Sentinel when an error is detected.
        """
        # ── TRIAGING ──
        self.state = OrchestratorState.TRIAGING
        show_error_detected(
            error.error_type,
            error.message,
            error.file_path,
            error.line_number,
        )

        # Record error in memory
        self.memory_store.record_error(
            {
                "error_id": error.error_id,
                "timestamp": error.timestamp.isoformat(),
                "error_type": error.error_type,
                "error_message": error.message,
                "file_path": error.file_path,
                "line_number": error.line_number,
                "stack_trace": error.stack_trace,
                "severity": error.severity,
                "category": error.category,
            }
        )

        # Check if we have LLM capability
        has_llm = bool(self.settings.llm.api_key) or (
            self.settings.llm.provider == "ollama"
        )

        if not has_llm:
            console.print(
                "\n[yellow]⚠️  No LLM API key configured — "
                "showing error details only.[/]"
            )
            console.print(
                "[dim]Set up: autoheal config set llm.api_key YOUR_KEY[/]"
            )
            self.memory_store.log_audit(
                error.error_id, "escalated", "No LLM configured"
            )
            self.state = OrchestratorState.MONITORING
            return

        # ── ANALYZING ──
        self.state = OrchestratorState.ANALYZING
        show_analyzing()

        # Build full context (CECE)
        context = await self.cece.build_context(error)

        # Run diagnostics
        diagnosis = await self.diagnostics.diagnose(context)

        show_diagnosis(
            diagnosis.root_cause,
            diagnosis.confidence,
            diagnosis.fix_strategy.value,
        )

        # Log diagnosis
        self.memory_store.log_audit(
            error.error_id,
            "diagnosed",
            (
                f"Root cause: {diagnosis.root_cause} | "
                f"Confidence: {diagnosis.confidence:.2f} | "
                f"Strategy: {diagnosis.fix_strategy.value}"
            ),
        )

        # ── RESOLVING ──
        self.state = OrchestratorState.RESOLVING

        # Check harness gates
        auto_apply = self.harness.should_auto_apply(diagnosis)
        should_suggest = self.harness.should_suggest(diagnosis)

        if not auto_apply and not should_suggest:
            show_escalated(
                f"Confidence ({diagnosis.confidence:.2f}) too low for action."
            )
            self._record_resolution(error, diagnosis, "escalated")
            self.state = OrchestratorState.ESCALATED
            return

        # Generate resolution
        resolution = await self.resolution.resolve(
            diagnosis,
            context,
            process_restart_callback=(
                self.sentinel.restart_process if auto_apply else None
            ),
        )

        # Handle resolution result
        if resolution.status == ResolutionStatus.APPLIED:
            show_fix_applied(resolution.description)
            self._record_resolution(
                error, diagnosis, "resolved", resolution
            )
            self.state = OrchestratorState.RESOLVED

        elif resolution.status == ResolutionStatus.SUGGESTED:
            show_fix_suggested(
                resolution.description,
                resolution.patch.diff if resolution.patch else None,
            )

            # Ask user to approve code patch
            if resolution.patch and self.settings.general.mode == "auto":
                approved = prompt_user_approval(
                    resolution.description,
                    resolution.patch.diff,
                )

                if approved:
                    # Create rollback point
                    rollback_ref = self.applicator.create_rollback_point(
                        f"AutoHeal: before fix for {error.error_type}"
                    )
                    resolution.rollback_ref = rollback_ref

                    # Apply patch
                    success = self.applicator.apply_patch(
                        resolution.patch.file_path,
                        resolution.patch.patched_content,
                    )

                    if success:
                        show_fix_applied(
                            f"Patch applied to {resolution.patch.file_path}"
                        )
                        self._record_resolution(
                            error, diagnosis, "resolved", resolution
                        )
                    else:
                        show_escalated("Failed to apply patch.")
                        self._record_resolution(
                            error, diagnosis, "failed", resolution
                        )
                else:
                    console.print("[dim]Fix declined by user.[/]")
                    self._record_resolution(
                        error, diagnosis, "suggested", resolution
                    )

            self.state = OrchestratorState.RESOLVED

        elif resolution.status == ResolutionStatus.ESCALATED:
            show_escalated(resolution.description)
            self._record_resolution(
                error, diagnosis, "escalated", resolution
            )
            self.state = OrchestratorState.ESCALATED

        elif resolution.status == ResolutionStatus.FAILED:
            show_escalated(f"Fix attempt failed: {resolution.description}")
            self._record_resolution(
                error, diagnosis, "failed", resolution
            )
            self.state = OrchestratorState.ESCALATED

        # ── LEARNING ──
        self.state = OrchestratorState.LEARNING
        console.print("[dim]📝 Resolution stored in memory[/]")
        console.print()

        self.state = OrchestratorState.MONITORING

    def _record_resolution(
        self, error, diagnosis, status, resolution=None
    ) -> None:
        """Record resolution in memory store."""
        self.memory_store.update_resolution(
            error.error_id,
            {
                "error_type": error.error_type,
                "error_message": error.message,
                "root_cause": diagnosis.root_cause,
                "fix_strategy": diagnosis.fix_strategy.value,
                "fix_description": (
                    resolution.description if resolution else ""
                ),
                "confidence": diagnosis.confidence,
                "status": status,
                "patch_diff": (
                    resolution.patch.diff
                    if resolution and resolution.patch
                    else ""
                ),
                "rollback_ref": (
                    resolution.rollback_ref if resolution else ""
                ),
            },
        )

        self.memory_store.log_audit(
            error.error_id,
            status,
            (
                f"Strategy: {diagnosis.fix_strategy.value} | "
                f"Description: "
                f"{resolution.description if resolution else 'N/A'}"
            ),
        )
