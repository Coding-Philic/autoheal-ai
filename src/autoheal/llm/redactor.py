"""Secret and PII redaction before sending to LLM."""

from __future__ import annotations

import re

from autoheal.config.settings import RedactionSettings


class SecretRedactor:
    """Redact secrets, API keys, passwords, PII from text."""

    DEFAULT_PATTERNS = [
        r"(?i)(api[_-]?key|secret|password|token|auth|credential)\s*[=:]\s*['\"]?\S+['\"]?",
        r"sk-[a-zA-Z0-9]{20,}",
        r"sk-ant-[a-zA-Z0-9\-_]{20,}",
        r"AIza[a-zA-Z0-9\-_]{35}",
        r"AKIA[A-Z0-9]{16}",
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        r"(?i)(DATABASE_URL|REDIS_URL|MONGO_URI|DB_PASSWORD)\s*=\s*\S+",
        r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        r"(?i)(mysql|postgres|mongodb|redis)://\S+",
    ]

    def __init__(self, settings: RedactionSettings):
        self.enabled = settings.enabled
        patterns = self.DEFAULT_PATTERNS + settings.patterns
        self.compiled_patterns = [re.compile(p) for p in patterns]

    def redact(self, text: str) -> str:
        """Redact all sensitive information from text."""
        if not self.enabled:
            return text

        for pattern in self.compiled_patterns:
            text = pattern.sub("[REDACTED]", text)

        return text
