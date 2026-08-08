"""Sentinel Agent — Main error detection orchestrator."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable, Optional

from rich.console import Console

from autoheal.config.settings import AutoHealSettings
from autoheal.sentinel.classifier import ErrorClassifier
from autoheal.sentinel.patterns import ErrorMatch, detect_error_in_output
from autoheal.sentinel.process_manager import ProcessManager

console = Console()


class ErrorEvent:
    """Structured error event emitted by the sentinel."""

    def __init__(
        self,
        error_id: str,
        error_type: str,
        message: str,
        file_path: Optional[str],
        line_number: Optional[int],
        stack_trace: str,
        raw_output: str,
        exit_code: Optional[int],
        severity: str,
        category: str,
        language: str,
        timestamp: datetime,
    ):
        self.error_id = error_id
        self.error_type = error_type
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.stack_trace = stack_trace
        self.raw_output = raw_output
        self.exit_code = exit_code
        self.severity = severity
        self.category = category
        self.language = language
        self.timestamp = timestamp


# Type alias for error handler callback
ErrorHandler = Callable[[ErrorEvent], Awaitable[None]]


class SentinelAgent:
    """
    The Sentinel Agent monitors a child process for errors.

    It wraps the process, captures stdout/stderr in real-time,
    applies error detection patterns, classifies errors, and
    emits ErrorEvents to the orchestrator.
    """

    def __init__(
        self,
        command: str,
        project_dir: Path,
        settings: AutoHealSettings,
        language: str = "unknown",
        on_error: Optional[ErrorHandler] = None,
    ):
        self.command = command
        self.project_dir = project_dir
        self.settings = settings
        self.language = language
        self.on_error = on_error
        self.process_manager = ProcessManager(command, str(project_dir))
        self.classifier = ErrorClassifier()
        self._stderr_buffer: list[str] = []
        self._stdout_buffer: list[str] = []
        self._error_count = 0

    async def start(self) -> None:
        """Start monitoring the child process."""
        await self.process_manager.start()

        # Collect output
        async for output in self.process_manager.stream_output():
            if output.stream == "stdout":
                if self.settings.general.verbose:
                    console.print(f"[dim]{output.line}[/]")
                else:
                    console.print(output.line)
                self._stdout_buffer.append(output.line)
            else:
                console.print(f"[red]{output.line}[/]")
                self._stderr_buffer.append(output.line)

        # Process exited — check for errors in accumulated stderr
        if self._stderr_buffer:
            full_stderr = "\n".join(self._stderr_buffer)
            error_match = detect_error_in_output(full_stderr, self.language)

            if error_match:
                await self._emit_error(error_match, full_stderr)
            elif self.process_manager.exit_code and self.process_manager.exit_code != 0:
                # Non-zero exit with stderr but no pattern match
                await self._emit_generic_error(full_stderr)

        elif self.process_manager.exit_code and self.process_manager.exit_code != 0:
            # Non-zero exit, no stderr
            await self._emit_generic_error(
                f"Process exited with code {self.process_manager.exit_code}"
            )

    async def _emit_error(self, match: ErrorMatch, raw_output: str) -> None:
        """Create and emit an ErrorEvent from a pattern match."""
        severity = self.classifier.classify_severity(match)
        category = self.classifier.classify_category(match)

        error_event = ErrorEvent(
            error_id=str(uuid.uuid4()),
            error_type=match.error_type,
            message=match.message,
            file_path=match.file_path,
            line_number=match.line_number,
            stack_trace=raw_output,
            raw_output=raw_output,
            exit_code=self.process_manager.exit_code,
            severity=severity,
            category=category,
            language=match.language or self.language,
            timestamp=datetime.utcnow(),
        )

        self._error_count += 1

        if self.on_error:
            await self.on_error(error_event)

    async def _emit_generic_error(self, raw_output: str) -> None:
        """Emit a generic error when no specific pattern matches."""
        error_event = ErrorEvent(
            error_id=str(uuid.uuid4()),
            error_type="ProcessError",
            message=f"Process exited with code {self.process_manager.exit_code}",
            file_path=None,
            line_number=None,
            stack_trace=raw_output,
            raw_output=raw_output,
            exit_code=self.process_manager.exit_code,
            severity="P1",
            category="runtime",
            language=self.language,
            timestamp=datetime.utcnow(),
        )

        self._error_count += 1

        if self.on_error:
            await self.on_error(error_event)

    async def restart_process(self) -> None:
        """Restart the monitored process."""
        self._stderr_buffer.clear()
        self._stdout_buffer.clear()
        await self.process_manager.restart()
