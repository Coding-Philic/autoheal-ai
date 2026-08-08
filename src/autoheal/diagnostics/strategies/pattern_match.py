"""Pattern match strategy — lookup known errors in memory store."""

from __future__ import annotations

from typing import Optional

from autoheal.cece.engine import StructuredErrorContext
from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy
from autoheal.memory.store import MemoryStore


class PatternMatchStrategy:
    """Check memory store for previously seen errors."""

    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    async def diagnose(
        self, context: StructuredErrorContext
    ) -> Optional[DiagnosisResult]:
        """Search memory for matching error patterns."""
        matches = self.memory_store.search_similar(
            error_type=context.error_type,
            error_message=context.error_message,
        )

        if not matches:
            return None

        best_match = matches[0]

        # Boost confidence based on past success rate
        base_confidence = best_match.get("confidence", 0.5)
        occ = max(best_match.get("occurrence_count", 1), 1)
        success_rate = best_match.get("success_count", 0) / occ
        adjusted_confidence = min(base_confidence * (1 + success_rate * 0.2), 1.0)

        try:
            strategy = FixStrategy(best_match.get("fix_strategy", "escalate"))
        except ValueError:
            strategy = FixStrategy.ESCALATE

        return DiagnosisResult(
            error_id=context.error_id,
            root_cause=best_match.get("root_cause", "Previously seen error"),
            category=best_match.get("category", context.category),
            confidence=adjusted_confidence,
            fix_strategy=strategy,
            explanation=(
                f"This error matches a previously resolved pattern "
                f"(seen {occ} times, success rate: {success_rate:.0%})."
            ),
            suggested_fix=best_match.get("fix_description", ""),
            strategy_source="pattern_match",
        )
