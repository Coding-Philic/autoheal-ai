"""Diagnostics Engine — Multi-strategy root cause analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from autoheal.cece.engine import StructuredErrorContext
from autoheal.config.settings import AutoHealSettings
from autoheal.llm.client import LLMClient
from autoheal.memory.store import MemoryStore


class FixStrategy(str, Enum):
    RESTART = "restart"
    CONFIG_PATCH = "config_patch"
    CODE_PATCH = "code_patch"
    DEPENDENCY_FIX = "dependency_fix"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"


@dataclass
class DiagnosisResult:
    """Result from the diagnostics engine."""

    error_id: str
    root_cause: str
    category: str
    confidence: float
    fix_strategy: FixStrategy
    explanation: str
    suggested_fix: Optional[str] = None
    strategy_source: str = "llm"
    diagnosed_at: datetime = field(default_factory=datetime.utcnow)


class DiagnosticsEngine:
    """
    Multi-strategy diagnosis engine.

    Runs pattern matching (memory lookup) and LLM reasoning,
    then selects the result with highest confidence.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        memory_store: MemoryStore,
        settings: AutoHealSettings,
    ):
        self.llm_client = llm_client
        self.memory_store = memory_store
        self.settings = settings

    async def diagnose(self, context: StructuredErrorContext) -> DiagnosisResult:
        """Run all diagnosis strategies and return the best result."""
        from autoheal.diagnostics.strategies.llm_reasoning import LLMReasoningStrategy
        from autoheal.diagnostics.strategies.pattern_match import PatternMatchStrategy

        results: list[DiagnosisResult] = []

        # Strategy 1: Pattern Match (fast, from memory)
        pattern_strategy = PatternMatchStrategy(self.memory_store)
        pattern_result = await pattern_strategy.diagnose(context)
        if pattern_result:
            results.append(pattern_result)

        # Strategy 2: LLM Reasoning (slower, more powerful)
        if self.llm_client.api_key or self.settings.llm.provider == "ollama":
            try:
                llm_strategy = LLMReasoningStrategy(self.llm_client)
                llm_result = await llm_strategy.diagnose(context)
                if llm_result:
                    results.append(llm_result)
            except Exception:
                pass  # LLM failed — fall back to pattern match

        if not results:
            return DiagnosisResult(
                error_id=context.error_id,
                root_cause="Unable to determine root cause",
                category=context.category,
                confidence=0.0,
                fix_strategy=FixStrategy.ESCALATE,
                explanation=(
                    "Both pattern matching and LLM analysis failed. "
                    "Check your LLM API key configuration."
                ),
                strategy_source="none",
            )

        # Select best result by weighted confidence
        return self._select_best(results)

    async def diagnose_manual(self, error_description: str) -> DiagnosisResult:
        """Diagnose from a manual error description."""
        from autoheal.diagnostics.strategies.llm_reasoning import LLMReasoningStrategy

        llm_strategy = LLMReasoningStrategy(self.llm_client)
        return await llm_strategy.diagnose_manual(error_description)

    def _select_best(self, results: list[DiagnosisResult]) -> DiagnosisResult:
        """Select diagnosis with highest weighted confidence."""
        if len(results) == 1:
            return results[0]

        weights = {"pattern_match": 1.1, "llm": 1.0, "none": 0.0}

        scored = []
        for r in results:
            w = weights.get(r.strategy_source, 1.0)
            scored.append((r.confidence * w, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
