"""LLM reasoning strategy — AI-powered root cause analysis."""

from __future__ import annotations

from autoheal.cece.engine import StructuredErrorContext
from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy
from autoheal.llm.client import LLMClient, LLMError
from autoheal.llm.prompts.diagnosis import (
    DIAGNOSIS_PROMPT,
    MANUAL_DIAGNOSIS_PROMPT,
    SYSTEM_PROMPT,
)


class LLMReasoningStrategy:
    """Use LLM for deep root cause analysis."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def diagnose(
        self, context: StructuredErrorContext
    ) -> DiagnosisResult | None:
        """Analyze error using LLM reasoning."""
        deps_str = ", ".join(
            f"{k}=={v}" for k, v in list(context.dependencies.items())[:20]
        )

        prompt = DIAGNOSIS_PROMPT.format(
            error_type=context.error_type,
            error_message=context.error_message,
            file_path=context.file_path or "unknown",
            line_number=context.line_number or "unknown",
            stack_trace=context.stack_trace[:3000],
            language=context.language,
            code_context=context.code_context or "N/A",
            project_language=context.language,
            project_framework=context.framework or "None",
            dependencies=deps_str or "N/A",
            os_name=context.environment.get("os_name", "unknown"),
            os_version=context.environment.get("os_version", "unknown"),
            runtime_version=context.runtime_version or "unknown",
            cpu_percent=context.environment.get("cpu_percent", 0),
            memory_percent=context.environment.get("memory_percent", 0),
        )

        try:
            response = await self.llm_client.complete_json(prompt, SYSTEM_PROMPT)

            try:
                strategy = FixStrategy(response.get("fix_strategy", "escalate"))
            except ValueError:
                strategy = FixStrategy.ESCALATE

            confidence = min(
                max(float(response.get("confidence", 0.5)), 0.0), 1.0
            )

            return DiagnosisResult(
                error_id=context.error_id,
                root_cause=response.get("root_cause", "Unknown"),
                category=response.get("category", context.category),
                confidence=confidence,
                fix_strategy=strategy,
                explanation=response.get("explanation", ""),
                suggested_fix=response.get("suggested_fix", ""),
                strategy_source="llm",
            )
        except (LLMError, KeyError, TypeError):
            return None

    async def diagnose_manual(self, error_description: str) -> DiagnosisResult:
        """Diagnose from a text description."""
        prompt = MANUAL_DIAGNOSIS_PROMPT.format(
            error_description=error_description
        )

        try:
            response = await self.llm_client.complete_json(prompt, SYSTEM_PROMPT)

            try:
                strategy = FixStrategy(response.get("fix_strategy", "escalate"))
            except ValueError:
                strategy = FixStrategy.ESCALATE

            confidence = min(
                max(float(response.get("confidence", 0.5)), 0.0), 1.0
            )

            return DiagnosisResult(
                error_id="manual",
                root_cause=response.get("root_cause", "Unknown"),
                category=response.get("category", "unknown"),
                confidence=confidence,
                fix_strategy=strategy,
                explanation=response.get("explanation", ""),
                suggested_fix=response.get("suggested_fix", ""),
                strategy_source="llm",
            )
        except Exception:
            return DiagnosisResult(
                error_id="manual",
                root_cause="LLM analysis failed",
                category="unknown",
                confidence=0.0,
                fix_strategy=FixStrategy.ESCALATE,
                explanation=(
                    "Could not analyze the error. "
                    "Check your LLM API key and try again."
                ),
                strategy_source="none",
            )
