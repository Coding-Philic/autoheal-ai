"""Harness Controller — safety gates and validation."""

from __future__ import annotations

from autoheal.config.settings import AutoHealSettings
from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy


class HarnessController:
    """
    Safety controller that gates fix application.

    Checks confidence thresholds, risk levels, and prevents
    dangerous operations.
    """

    def __init__(self, settings: AutoHealSettings):
        self.settings = settings

    def should_auto_apply(self, diagnosis: DiagnosisResult) -> bool:
        """Determine if a fix should be auto-applied."""
        # Escalation → never auto-apply
        if diagnosis.fix_strategy == FixStrategy.ESCALATE:
            return False

        # Code patches → never auto-apply in MVP (suggest only)
        if diagnosis.fix_strategy == FixStrategy.CODE_PATCH:
            return False

        # Config patches → never auto-apply in MVP
        if diagnosis.fix_strategy == FixStrategy.CONFIG_PATCH:
            return False

        # Suggest-only mode
        if self.settings.general.mode == "suggest":
            return False

        # Manual mode
        if self.settings.general.mode == "manual":
            return False

        # Restart and dependency fixes → auto-apply if above threshold
        if diagnosis.confidence >= self.settings.resolution.confidence_threshold:
            return True

        return False

    def should_suggest(self, diagnosis: DiagnosisResult) -> bool:
        """Determine if a fix should be suggested to the user."""
        # Manual mode → no suggestions
        if self.settings.general.mode == "manual":
            return False

        if diagnosis.fix_strategy == FixStrategy.CODE_PATCH:
            return (
                diagnosis.confidence
                >= self.settings.resolution.code_patch_threshold
            )

        return (
            diagnosis.confidence
            >= self.settings.resolution.confidence_threshold
        )

    def assess_risk(self, diagnosis: DiagnosisResult) -> str:
        """Assess the risk level of a proposed fix."""
        risk_map = {
            FixStrategy.RESTART: "low",
            FixStrategy.DEPENDENCY_FIX: "medium",
            FixStrategy.CONFIG_PATCH: "medium",
            FixStrategy.CODE_PATCH: "high",
            FixStrategy.ROLLBACK: "medium",
            FixStrategy.ESCALATE: "none",
        }
        return risk_map.get(diagnosis.fix_strategy, "unknown")
