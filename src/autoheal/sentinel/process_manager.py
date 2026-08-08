"""Process manager — spawn and manage monitored child processes."""

from __future__ import annotations

import asyncio
import os
import signal
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator, Optional


@dataclass
class ProcessOutput:
    """A line of output from the monitored process."""
    stream: str         # "stdout" or "stderr"
    line: str           # The output line
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ProcessManager:
    """Manages the monitored child process."""

    def __init__(self, command: str, cwd: str = "."):
        self.command = command
        self.cwd = cwd
        self.process: Optional[asyncio.subprocess.Process] = None
        self.start_time: Optional[datetime] = None
        self.exit_code: Optional[int] = None
        self._running = False

    async def start(self) -> None:
        """Start the child process."""
        self.process = await asyncio.create_subprocess_shell(
            self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        self.start_time = datetime.utcnow()
        self._running = True

    async def stream_output(self) -> AsyncIterator[ProcessOutput]:
        """Stream stdout and stderr lines as they arrive."""
        if not self.process or not self.process.stdout or not self.process.stderr:
            return

        async def _read_stream(
            stream: asyncio.StreamReader, name: str
        ) -> list[ProcessOutput]:
            lines: list[ProcessOutput] = []
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").rstrip()
                lines.append(ProcessOutput(stream=name, line=decoded))
            return lines

        stdout_task = asyncio.create_task(
            _read_stream(self.process.stdout, "stdout")
        )
        stderr_task = asyncio.create_task(
            _read_stream(self.process.stderr, "stderr")
        )

        done, _ = await asyncio.wait(
            {stdout_task, stderr_task},
            return_when=asyncio.ALL_COMPLETED,
        )

        all_output: list[ProcessOutput] = []
        for task in done:
            all_output.extend(task.result())

        all_output.sort(key=lambda x: x.timestamp)

        for output in all_output:
            yield output

        await self.process.wait()
        self.exit_code = self.process.returncode
        self._running = False

    async def restart(self) -> None:
        """Restart the child process."""
        await self.stop()
        await self.start()

    async def stop(self) -> None:
        """Stop the child process."""
        if self.process and self._running:
            try:
                if os.name != "nt":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except (ProcessLookupError, asyncio.TimeoutError, OSError):
                if self.process:
                    try:
                        self.process.kill()
                    except (ProcessLookupError, OSError):
                        pass
            self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def uptime_seconds(self) -> float:
        if self.start_time:
            return (datetime.utcnow() - self.start_time).total_seconds()
        return 0
