"""Confidence scoring for diagnosis results."""

from __future__ import annotations


class ConfidenceScorer:
    """Score and adjust confidence levels based on multiple signals."""

    @staticmethod
    def score(
        base_confidence: float,
        has_stack_trace: bool = False,
        has_code_context: bool = False,
        has_memory_match: bool = False,
        memory_success_rate: float = 0.0,
    ) -> float:
        """Calculate adjusted confidence from multiple signals."""
        score = base_confidence

        # Boost for having stack trace
        if has_stack_trace:
            score = min(score + 0.05, 1.0)

        # Boost for having code context
        if has_code_context:
            score = min(score + 0.05, 1.0)

        # Boost for memory match
        if has_memory_match:
            boost = 0.1 * memory_success_rate
            score = min(score + boost, 1.0)

        return round(score, 3)
