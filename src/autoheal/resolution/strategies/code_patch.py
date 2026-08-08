"""Code patch strategy — generate LLM-powered code fixes."""

from __future__ import annotations

import difflib
from pathlib import Path

from autoheal.cece.code_reader import read_full_file
from autoheal.cece.engine import StructuredErrorContext
from autoheal.diagnostics.engine import DiagnosisResult, FixStrategy
from autoheal.llm.client import LLMClient, LLMError
from autoheal.llm.prompts.patch_gen import PATCH_GEN_PROMPT
from autoheal.llm.prompts.patch_gen import SYSTEM_PROMPT
from autoheal.resolution.engine import PatchInfo, ResolutionResult, ResolutionStatus


class CodePatchStrategy:
    """Generate code patches using LLM."""

    def __init__(self, llm_client: LLMClient, project_dir: Path):
        self.llm_client = llm_client
        self.project_dir = project_dir

    async def generate_patch(
        self, diagnosis: DiagnosisResult, context: StructuredErrorContext
    ) -> ResolutionResult:
        """Generate a code patch using the LLM."""
        original_content = read_full_file(
            context.file_path, str(self.project_dir)  # type: ignore[arg-type]
        )

        if not original_content:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.CODE_PATCH,
                status=ResolutionStatus.ESCALATED,
                confidence=diagnosis.confidence,
                description=f"Could not read file: {context.file_path}",
            )

        prompt = PATCH_GEN_PROMPT.format(
            error_type=context.error_type,
            error_message=context.error_message,
            root_cause=diagnosis.root_cause,
            file_path=context.file_path,
            language=context.language,
            file_content=original_content[:8000],
            line_number=context.line_number or "unknown",
            error_context=context.code_context or "N/A",
            explanation=diagnosis.explanation,
        )

        try:
            response = await self.llm_client.complete_json(prompt, SYSTEM_PROMPT)

            patched_content = response.get("patched_content", "")
            description = response.get("description", "LLM-generated code fix")

            if not patched_content:
                return ResolutionResult(
                    error_id=diagnosis.error_id,
                    strategy=FixStrategy.CODE_PATCH,
                    status=ResolutionStatus.FAILED,
                    confidence=diagnosis.confidence,
                    description="LLM did not generate a valid patch.",
                )

            diff = self._generate_diff(
                original_content,
                patched_content,
                context.file_path or "unknown",
            )

            patch = PatchInfo(
                file_path=context.file_path or "",
                original_content=original_content,
                patched_content=patched_content,
                diff=diff,
                description=description,
            )

            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.CODE_PATCH,
                status=ResolutionStatus.SUGGESTED,
                confidence=diagnosis.confidence,
                description=description,
                patch=patch,
            )

        except (LLMError, Exception) as e:
            return ResolutionResult(
                error_id=diagnosis.error_id,
                strategy=FixStrategy.CODE_PATCH,
                status=ResolutionStatus.FAILED,
                confidence=diagnosis.confidence,
                description=f"Patch generation failed: {e}",
            )

    def _generate_diff(
        self, original: str, patched: str, file_path: str
    ) -> str:
        """Generate a unified diff between original and patched content."""
        original_lines = original.splitlines(keepends=True)
        patched_lines = patched.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            patched_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        )

        return "".join(diff)
