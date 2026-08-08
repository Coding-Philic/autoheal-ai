"""Error severity and category classification."""

from __future__ import annotations

from autoheal.sentinel.patterns import ErrorMatch

# Severity classification rules
SEVERITY_MAP: dict[str, str] = {
    "MemoryError": "P0", "OutOfMemoryError": "P0", "SegmentationFault": "P0",
    "SystemExit": "P0", "OOM": "P0",
    "ConnectionError": "P1", "TimeoutError": "P1", "PermissionError": "P1",
    "DatabaseError": "P1", "ECONNREFUSED": "P1",
    "TypeError": "P2", "ValueError": "P2", "KeyError": "P2",
    "IndexError": "P2", "AttributeError": "P2", "NameError": "P2",
    "ReferenceError": "P2", "NullPointerException": "P2",
    "ImportError": "P3", "ModuleNotFoundError": "P3",
    "FileNotFoundError": "P3", "SyntaxError": "P3",
    "DeprecationWarning": "P4", "Warning": "P4",
}

# Category classification rules
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "runtime": [
        "TypeError", "ValueError", "KeyError", "IndexError", "AttributeError",
        "NameError", "NullPointerException", "ReferenceError", "panic",
    ],
    "config": [
        "config", "configuration", "settings", "env", "environment variable",
        "YAML", "TOML", "JSON", "parse error",
    ],
    "dependency": [
        "ImportError", "ModuleNotFoundError", "Cannot find module",
        "MODULE_NOT_FOUND", "package", "dependency", "version",
    ],
    "resource": [
        "MemoryError", "OutOfMemory", "OOM", "disk", "space", "ENOSPC", "quota",
    ],
    "network": [
        "ConnectionError", "ECONNREFUSED", "ETIMEDOUT", "timeout",
        "connection refused", "ENOTFOUND", "DNS",
    ],
    "permission": [
        "PermissionError", "EACCES", "permission denied", "forbidden",
    ],
    "syntax": [
        "SyntaxError", "IndentationError", "ParseError", "parse error",
    ],
    "logic": [
        "AssertionError", "ZeroDivisionError", "RecursionError",
        "infinite loop", "deadlock",
    ],
}


class ErrorClassifier:
    """Classify error severity and category."""

    def classify_severity(self, error: ErrorMatch) -> str:
        """Return severity level (P0-P4)."""
        return SEVERITY_MAP.get(error.error_type, "P2")

    def classify_category(self, error: ErrorMatch) -> str:
        """Return error category."""
        combined = f"{error.error_type} {error.message}".lower()

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in combined:
                    return category

        return "unknown"
