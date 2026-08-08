"""Tests for the Memory Store."""

from __future__ import annotations

from pathlib import Path

from autoheal.memory.store import MemoryStore


class TestMemoryStore:
    """Test SQLite memory store operations."""

    def test_initialize(self, tmp_path: Path):
        """Initialize database creates tables."""
        store = MemoryStore(tmp_path / "test.db")
        store.initialize()
        store.close()

        assert (tmp_path / "test.db").exists()

    def test_record_and_get_history(self, tmp_path: Path):
        """Record error and retrieve history."""
        store = MemoryStore(tmp_path / "test.db")
        store.initialize()

        store.record_error({
            "error_id": "test-001",
            "error_type": "TypeError",
            "error_message": "cannot subscript None",
            "file_path": "app.py",
            "line_number": 10,
            "severity": "P2",
            "category": "runtime",
        })

        history = store.get_history(limit=10)
        assert len(history) == 1
        assert history[0]["error_id"] == "test-001"
        assert history[0]["error_type"] == "TypeError"

        store.close()

    def test_update_resolution(self, tmp_path: Path):
        """Update error with resolution data."""
        store = MemoryStore(tmp_path / "test.db")
        store.initialize()

        store.record_error({
            "error_id": "test-002",
            "error_type": "ImportError",
            "error_message": "No module named 'flask'",
        })

        store.update_resolution("test-002", {
            "error_type": "ImportError",
            "error_message": "No module named 'flask'",
            "root_cause": "Missing dependency: flask",
            "fix_strategy": "dependency_fix",
            "fix_description": "pip install flask",
            "confidence": 0.95,
            "status": "resolved",
        })

        history = store.get_history()
        assert history[0]["status"] == "resolved"
        assert history[0]["root_cause"] == "Missing dependency: flask"

        store.close()

    def test_search_similar(self, tmp_path: Path):
        """Search for similar error patterns."""
        store = MemoryStore(tmp_path / "test.db")
        store.initialize()

        store.record_error({
            "error_id": "test-003",
            "error_type": "ImportError",
            "error_message": "No module named 'requests'",
        })
        store.update_resolution("test-003", {
            "error_type": "ImportError",
            "error_message": "No module named 'requests'",
            "root_cause": "Missing package",
            "fix_strategy": "dependency_fix",
            "confidence": 0.9,
            "status": "resolved",
        })

        matches = store.search_similar("ImportError", "No module named 'flask'")
        assert len(matches) >= 1
        assert matches[0]["error_type"] == "ImportError"

        store.close()

    def test_get_statistics(self, tmp_path: Path):
        """Get aggregate statistics."""
        store = MemoryStore(tmp_path / "test.db")
        store.initialize()

        store.record_error({
            "error_id": "s1",
            "error_type": "TypeError",
            "error_message": "test error",
        })
        store.record_error({
            "error_id": "s2",
            "error_type": "ImportError",
            "error_message": "test error 2",
        })
        store.update_resolution("s1", {
            "error_type": "TypeError",
            "error_message": "test error",
            "root_cause": "bug",
            "fix_strategy": "code_patch",
            "confidence": 0.8,
            "status": "resolved",
        })

        stats = store.get_statistics()
        assert stats["total_errors"] == 2
        assert stats["resolved"] == 1

        store.close()

    def test_audit_log(self, tmp_path: Path):
        """Audit log records actions."""
        store = MemoryStore(tmp_path / "test.db")
        store.initialize()

        store.log_audit("test-001", "detected", "Error detected in app.py")

        assert store.conn is not None
        rows = store.conn.execute(
            "SELECT * FROM audit_log WHERE error_id = 'test-001'"
        ).fetchall()
        assert len(rows) == 1
        assert rows[0]["action"] == "detected"

        store.close()
