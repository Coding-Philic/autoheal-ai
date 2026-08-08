"""Memory Store — SQLite-based error memory and pattern storage."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class MemoryStore:
    """
    SQLite-based memory store for error patterns and resolution history.

    Provides error history CRUD, pattern storage, text search,
    audit logging, and statistics.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        """Create database tables."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")

        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS error_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                file_path TEXT,
                line_number INTEGER,
                stack_trace TEXT DEFAULT '',
                severity TEXT DEFAULT 'P2',
                category TEXT DEFAULT 'unknown',
                root_cause TEXT DEFAULT '',
                fix_strategy TEXT DEFAULT '',
                fix_description TEXT DEFAULT '',
                confidence REAL DEFAULT 0.0,
                status TEXT DEFAULT 'detected',
                patch_diff TEXT DEFAULT '',
                rollback_ref TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS memory_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message_pattern TEXT NOT NULL,
                root_cause TEXT NOT NULL,
                fix_strategy TEXT NOT NULL,
                fix_description TEXT DEFAULT '',
                confidence REAL DEFAULT 0.0,
                occurrence_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 0,
                last_seen TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                error_id TEXT,
                action TEXT NOT NULL,
                details TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_error_history_type
                ON error_history(error_type);
            CREATE INDEX IF NOT EXISTS idx_error_history_status
                ON error_history(status);
            CREATE INDEX IF NOT EXISTS idx_memory_patterns_type
                ON memory_patterns(error_type);
            CREATE INDEX IF NOT EXISTS idx_audit_log_error_id
                ON audit_log(error_id);
        """
        )
        self.conn.commit()

    def _ensure_connected(self) -> None:
        """Ensure database connection exists."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row

    def record_error(self, error_data: dict) -> None:
        """Record a new error event."""
        self._ensure_connected()
        now = datetime.utcnow().isoformat()
        assert self.conn is not None
        self.conn.execute(
            """INSERT OR REPLACE INTO error_history
               (error_id, timestamp, error_type, error_message, file_path,
                line_number, stack_trace, severity, category, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'detected', ?)""",
            (
                error_data["error_id"],
                error_data.get("timestamp", now),
                error_data["error_type"],
                error_data["error_message"],
                error_data.get("file_path"),
                error_data.get("line_number"),
                error_data.get("stack_trace", ""),
                error_data.get("severity", "P2"),
                error_data.get("category", "unknown"),
                now,
            ),
        )
        self.conn.commit()
        self.log_audit(error_data["error_id"], "detected", "Error detected")

    def update_resolution(self, error_id: str, resolution_data: dict) -> None:
        """Update error record with resolution data."""
        self._ensure_connected()
        now = datetime.utcnow().isoformat()
        assert self.conn is not None
        self.conn.execute(
            """UPDATE error_history
               SET root_cause = ?, fix_strategy = ?, fix_description = ?,
                   confidence = ?, status = ?, patch_diff = ?,
                   rollback_ref = ?, resolved_at = ?
               WHERE error_id = ?""",
            (
                resolution_data.get("root_cause", ""),
                resolution_data.get("fix_strategy", ""),
                resolution_data.get("fix_description", ""),
                resolution_data.get("confidence", 0.0),
                resolution_data.get("status", "resolved"),
                resolution_data.get("patch_diff", ""),
                resolution_data.get("rollback_ref", ""),
                now,
                error_id,
            ),
        )
        self.conn.commit()

        # Update or create memory pattern on success
        if resolution_data.get("status") in ("resolved", "applied"):
            self._update_pattern(
                error_type=resolution_data.get("error_type", ""),
                error_message=resolution_data.get("error_message", ""),
                root_cause=resolution_data.get("root_cause", ""),
                fix_strategy=resolution_data.get("fix_strategy", ""),
                fix_description=resolution_data.get("fix_description", ""),
                confidence=resolution_data.get("confidence", 0.0),
                success=True,
            )

    def _update_pattern(
        self,
        error_type: str,
        error_message: str,
        root_cause: str,
        fix_strategy: str,
        fix_description: str,
        confidence: float,
        success: bool,
    ) -> None:
        """Update or create a memory pattern."""
        now = datetime.utcnow().isoformat()
        assert self.conn is not None

        existing = self.conn.execute(
            "SELECT id, occurrence_count, success_count FROM memory_patterns "
            "WHERE error_type = ? AND error_message_pattern = ?",
            (error_type, error_message[:200]),
        ).fetchone()

        if existing:
            success_inc = 1 if success else 0
            self.conn.execute(
                """UPDATE memory_patterns SET
                   occurrence_count = occurrence_count + 1,
                   success_count = success_count + ?,
                   confidence = ?, last_seen = ?
                   WHERE id = ?""",
                (success_inc, confidence, now, existing["id"]),
            )
        else:
            self.conn.execute(
                """INSERT INTO memory_patterns
                   (error_type, error_message_pattern, root_cause, fix_strategy,
                    fix_description, confidence, occurrence_count, success_count,
                    last_seen, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)""",
                (
                    error_type,
                    error_message[:200],
                    root_cause,
                    fix_strategy,
                    fix_description,
                    confidence,
                    1 if success else 0,
                    now,
                    now,
                ),
            )
        self.conn.commit()

    def search_similar(
        self, error_type: str, error_message: str, limit: int = 5
    ) -> list[dict]:
        """Search for similar errors in memory patterns."""
        self._ensure_connected()
        assert self.conn is not None

        # Try exact type match
        results = self.conn.execute(
            """SELECT * FROM memory_patterns
               WHERE error_type = ?
               ORDER BY success_count DESC, occurrence_count DESC
               LIMIT ?""",
            (error_type, limit),
        ).fetchall()

        if results:
            return [dict(r) for r in results]

        # Fallback: search by message keywords
        keywords = error_message.split()[:5]
        for keyword in keywords:
            if len(keyword) < 4:
                continue
            results = self.conn.execute(
                """SELECT * FROM memory_patterns
                   WHERE error_message_pattern LIKE ?
                   ORDER BY success_count DESC
                   LIMIT ?""",
                (f"%{keyword}%", limit),
            ).fetchall()
            if results:
                return [dict(r) for r in results]

        return []

    def get_history(self, limit: int = 20) -> list[dict]:
        """Get recent error history."""
        self._ensure_connected()
        assert self.conn is not None
        results = self.conn.execute(
            "SELECT * FROM error_history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in results]

    def get_statistics(self) -> dict:
        """Get aggregate statistics."""
        self._ensure_connected()
        assert self.conn is not None

        total = self.conn.execute(
            "SELECT COUNT(*) FROM error_history"
        ).fetchone()[0]
        resolved = self.conn.execute(
            "SELECT COUNT(*) FROM error_history "
            "WHERE status IN ('resolved', 'applied')"
        ).fetchone()[0]
        escalated = self.conn.execute(
            "SELECT COUNT(*) FROM error_history WHERE status = 'escalated'"
        ).fetchone()[0]
        patterns = self.conn.execute(
            "SELECT COUNT(*) FROM memory_patterns"
        ).fetchone()[0]

        return {
            "total_errors": total,
            "resolved": resolved,
            "escalated": escalated,
            "failed": total - resolved - escalated,
            "patterns": patterns,
        }

    def log_audit(
        self, error_id: str, action: str, details: str = ""
    ) -> None:
        """Log an audit event."""
        self._ensure_connected()
        assert self.conn is not None
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO audit_log "
            "(timestamp, error_id, action, details, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (now, error_id, action, details, now),
        )
        self.conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
