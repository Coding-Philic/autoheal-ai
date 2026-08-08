"""Tests for the Resolution Engine."""

from __future__ import annotations

from autoheal.resolution.engine import PatchInfo, ResolutionResult, ResolutionStatus
from autoheal.diagnostics.engine import FixStrategy


class TestResolutionModels:
    """Test resolution data models."""

    def test_patch_info(self):
        """Create PatchInfo."""
        patch = PatchInfo(
            file_path="app.py",
            original_content="x = None\nprint(x.name)\n",
            patched_content="x = None\nif x:\n    print(x.name)\n",
            diff="- print(x.name)\n+ if x:\n+     print(x.name)",
            description="Added null check",
        )
        assert patch.file_path == "app.py"
        assert "null check" in patch.description.lower()

    def test_resolution_result(self):
        """Create ResolutionResult."""
        result = ResolutionResult(
            error_id="test-001",
            strategy=FixStrategy.RESTART,
            status=ResolutionStatus.APPLIED,
            confidence=0.9,
            description="Process restarted.",
        )
        assert result.status == ResolutionStatus.APPLIED
        assert result.strategy == FixStrategy.RESTART
