"""Restart strategy — restart the monitored process."""

from __future__ import annotations


class RestartStrategy:
    """Simple process restart strategy."""

    async def execute(self, restart_callback) -> bool:
        """Execute restart. Returns True if successful."""
        if restart_callback:
            await restart_callback()
            return True
        return False
