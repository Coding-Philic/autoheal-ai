"""Error detection patterns for multiple languages and frameworks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ErrorMatch:
    """Result of an error pattern match."""
    error_type: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    language: str = "unknown"
    full_match: str = ""


# ── Python Error Patterns ──────────────────────────────────────────
PYTHON_PATTERNS = [
    re.compile(
        r'File "(?P<file>[^"]+)", line (?P<line>\d+).*\n'
        r'(?:.*\n)*?'
        r'(?P<type>\w+Error): (?P<message>.+)',
        re.MULTILINE,
    ),
    re.compile(
        r'(?P<type>(?:Type|Name|Value|Key|Index|Attribute|Import|Module|File|'
        r'Permission|OS|Runtime|Syntax|Indentation|Memory|Overflow|Recursion|'
        r'StopIteration|Arithmetic|ZeroDivision|Assertion|EOF|Connection|'
        r'Timeout|Unicode|Lookup|Reference|NotImplemented)Error): (?P<message>.+)'
    ),
    re.compile(r'Traceback \(most recent call last\):'),
    re.compile(r'(?P<type>django\.[\w.]+Error): (?P<message>.+)'),
]

# ── Node.js Error Patterns ─────────────────────────────────────────
NODE_PATTERNS = [
    re.compile(
        r'(?P<file>[/\w.\-]+\.(?:js|ts|mjs|cjs)):(?P<line>\d+)\n'
        r'.*\n'
        r'\s*(?P<type>\w+Error): (?P<message>.+)',
        re.MULTILINE,
    ),
    re.compile(
        r'(?P<type>(?:Reference|Type|Syntax|Range|URI|Eval|Internal|'
        r'Assertion)Error): (?P<message>.+)'
    ),
    re.compile(r"Cannot find module '(?P<message>[^']+)'"),
    re.compile(r'UnhandledPromiseRejectionWarning: (?P<message>.+)'),
]

# ── Go Error Patterns ──────────────────────────────────────────────
GO_PATTERNS = [
    re.compile(r'panic: (?P<message>.+)'),
    re.compile(r'goroutine \d+ \[.+\]:\n(?P<file>.+\.go):(?P<line>\d+)'),
    re.compile(r'(?P<file>.+\.go):(?P<line>\d+):\d+: (?P<message>.+)'),
    re.compile(r'runtime error: (?P<message>.+)'),
]

# ── Rust Error Patterns ────────────────────────────────────────────
RUST_PATTERNS = [
    re.compile(r'error\[E\d+\]: (?P<message>.+)'),
    re.compile(
        r"thread '.*' panicked at '(?P<message>.+)', (?P<file>.+):(?P<line>\d+)"
    ),
    re.compile(r'error: (?P<message>.+)'),
]

# ── Java Error Patterns ────────────────────────────────────────────
JAVA_PATTERNS = [
    re.compile(
        r'(?P<type>(?:java\.\w+\.)*\w+Exception): (?P<message>.+)\n'
        r'\s+at (?P<file>[\w.$]+)\([\w.]+:(?P<line>\d+)\)',
        re.MULTILINE,
    ),
    re.compile(r'(?P<type>(?:java\.\w+\.)*\w+Error): (?P<message>.+)'),
]

# ── Ruby Error Patterns ────────────────────────────────────────────
RUBY_PATTERNS = [
    re.compile(
        r'(?P<file>.+\.rb):(?P<line>\d+):in .+: (?P<message>.+) \((?P<type>\w+Error)\)'
    ),
    re.compile(r'(?P<type>\w+Error): (?P<message>.+)'),
]

# ── PHP Error Patterns ─────────────────────────────────────────────
PHP_PATTERNS = [
    re.compile(
        r'(?P<type>Fatal error|Parse error|Warning): (?P<message>.+) in '
        r'(?P<file>.+\.php) on line (?P<line>\d+)'
    ),
]

# ── Generic Error Patterns ─────────────────────────────────────────
GENERIC_PATTERNS = [
    re.compile(r'(?i)\b(?:ERROR|FATAL|CRITICAL)\b[:\s]+(?P<message>.+)'),
    re.compile(r'Segmentation fault'),
    re.compile(r'Killed|Out of memory|OOM'),
    re.compile(r'(?i)(?:connection refused|ECONNREFUSED|ETIMEDOUT|ENOTFOUND)'),
    re.compile(r'(?i)permission denied'),
    re.compile(r'(?i)(?:no such file or directory|ENOENT|FileNotFoundError)'),
    re.compile(r'(?i)(?:address already in use|EADDRINUSE)'),
]

# All patterns grouped by language
ALL_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "python": PYTHON_PATTERNS,
    "javascript": NODE_PATTERNS,
    "typescript": NODE_PATTERNS,
    "go": GO_PATTERNS,
    "rust": RUST_PATTERNS,
    "java": JAVA_PATTERNS,
    "ruby": RUBY_PATTERNS,
    "php": PHP_PATTERNS,
    "generic": GENERIC_PATTERNS,
}


def detect_error_in_output(
    output: str, language: str = "unknown"
) -> Optional[ErrorMatch]:
    """
    Scan output text for error patterns.
    Returns ErrorMatch if an error is detected, None otherwise.
    """
    # Try language-specific patterns first
    if language in ALL_PATTERNS:
        result = _try_patterns(ALL_PATTERNS[language], output, language)
        if result:
            return result

    # Try all other language patterns
    for lang, patterns in ALL_PATTERNS.items():
        if lang == language or lang == "generic":
            continue
        result = _try_patterns(patterns, output, lang)
        if result:
            return result

    # Try generic patterns last
    result = _try_patterns(GENERIC_PATTERNS, output, "unknown")
    if result:
        return result

    return None


def _try_patterns(
    patterns: list[re.Pattern[str]], output: str, language: str
) -> Optional[ErrorMatch]:
    """Try a list of patterns against output text."""
    for pattern in patterns:
        match = pattern.search(output)
        if match:
            groups = match.groupdict()
            line_str = groups.get("line")
            return ErrorMatch(
                error_type=groups.get("type", "Error"),
                message=groups.get("message", output[:200]),
                file_path=groups.get("file"),
                line_number=int(line_str) if line_str else None,
                language=language,
                full_match=match.group(0),
            )
    return None
