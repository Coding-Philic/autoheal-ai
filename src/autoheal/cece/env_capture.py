"""Capture system environment information."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from typing import Optional


def capture_environment() -> dict:
    """Capture full system environment snapshot."""
    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        memory_total_gb = round(mem.total / (1024**3), 2)
        memory_percent = mem.percent

        if os.name != "nt":
            disk_percent = psutil.disk_usage("/").percent
        else:
            disk_percent = psutil.disk_usage("C:\\").percent
    except ImportError:
        cpu_percent = 0.0
        memory_total_gb = 0.0
        memory_percent = 0.0
        disk_percent = 0.0

    return {
        "os_name": platform.system(),
        "os_version": platform.release(),
        "python_version": (
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f".{sys.version_info.micro}"
        ),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count() or 0,
        "cpu_percent": cpu_percent,
        "memory_total_gb": memory_total_gb,
        "memory_percent": memory_percent,
        "disk_percent": disk_percent,
    }


def detect_runtime_version(language: str) -> Optional[str]:
    """Detect the version of the runtime for a given language."""
    commands: dict[str, list[str]] = {
        "python": [sys.executable, "--version"],
        "javascript": ["node", "--version"],
        "typescript": ["node", "--version"],
        "go": ["go", "version"],
        "rust": ["rustc", "--version"],
        "java": ["java", "--version"],
        "ruby": ["ruby", "--version"],
        "php": ["php", "--version"],
    }

    if language == "python":
        return f"Python {sys.version}"

    cmd = commands.get(language)
    if not cmd:
        return None

    binary = cmd[0]
    if not shutil.which(binary):
        return None

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output.split("\n")[0] if output else None
    except Exception:
        return None
