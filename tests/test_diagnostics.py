"""Tests for the diagnostics engine."""

from __future__ import annotations

from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy
from autoheal.harness.controller import HarnessController
from autoheal.config.settings import AutoHealSettings


class TestHarnessController:
    """Test safety gates."""

    def test_auto_apply_restart(self):
        """Restart with high confidence → auto-apply."""
        settings = AutoHealSettings()
        harness = HarnessController(settings)

        diagnosis = DiagnosisResult(
            error_id="test",
            root_cause="Process crashed",
            category="runtime",
            confidence=0.85,
            fix_strategy=FixStrategy.RESTART,
            explanation="test",
        )

        assert harness.should_auto_apply(diagnosis) is True

    def test_no_auto_apply_code_patch(self):
        """Code patches → never auto-apply."""
        settings = AutoHealSettings()
        harness = HarnessController(settings)

        diagnosis = DiagnosisResult(
            error_id="test",
            root_cause="Bug in code",
            category="logic",
            confidence=0.99,
            fix_strategy=FixStrategy.CODE_PATCH,
            explanation="test",
        )

        assert harness.should_auto_apply(diagnosis) is False

    def test_no_auto_apply_low_confidence(self):
        """Low confidence → no auto-apply."""
        settings = AutoHealSettings()
        harness = HarnessController(settings)

        diagnosis = DiagnosisResult(
            error_id="test",
            root_cause="unknown",
            category="unknown",
            confidence=0.3,
            fix_strategy=FixStrategy.RESTART,
            explanation="test",
        )

        assert harness.should_auto_apply(diagnosis) is False

    def test_suggest_code_patch_high_confidence(self):
        """Code patch with high confidence → suggest."""
        settings = AutoHealSettings()
        harness = HarnessController(settings)

        diagnosis = DiagnosisResult(
            error_id="test",
            root_cause="Null check missing",
            category="logic",
            confidence=0.95,
            fix_strategy=FixStrategy.CODE_PATCH,
            explanation="test",
        )

        assert harness.should_suggest(diagnosis) is True

    def test_no_suggest_code_patch_low_confidence(self):
        """Code patch below threshold → no suggest."""
        settings = AutoHealSettings()
        harness = HarnessController(settings)

        diagnosis = DiagnosisResult(
            error_id="test",
            root_cause="Maybe a bug",
            category="logic",
            confidence=0.5,
            fix_strategy=FixStrategy.CODE_PATCH,
            explanation="test",
        )

        assert harness.should_suggest(diagnosis) is False

    def test_risk_assessment(self):
        """Assess risk levels."""
        settings = AutoHealSettings()
        harness = HarnessController(settings)

        low = DiagnosisResult(
            error_id="t", root_cause="", category="",
            confidence=0.9, fix_strategy=FixStrategy.RESTART, explanation="",
        )
        high = DiagnosisResult(
            error_id="t", root_cause="", category="",
            confidence=0.9, fix_strategy=FixStrategy.CODE_PATCH, explanation="",
        )

        assert harness.assess_risk(low) == "low"
        assert harness.assess_risk(high) == "high"
