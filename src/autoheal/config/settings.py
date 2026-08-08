"""AutoHeal AI configuration settings using Pydantic."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore[assignment]

try:
    import tomli_w
except ImportError:
    tomli_w = None  # type: ignore[assignment]


class GeneralSettings(BaseModel):
    mode: str = "auto"
    verbose: bool = False
    log_level: str = "info"


class SentinelSettings(BaseModel):
    watch_stdout: bool = True
    watch_stderr: bool = True
    watch_exit_code: bool = True
    health_check_interval: int = 30


class DiagnosticsSettings(BaseModel):
    timeout: int = 30
    strategies: list[str] = Field(default_factory=lambda: ["pattern_match", "llm_reasoning"])


class ResolutionSettings(BaseModel):
    confidence_threshold: float = 0.75
    code_patch_threshold: float = 0.90
    create_backup: bool = True
    max_patch_lines: int = 50


class MemorySettings(BaseModel):
    enabled: bool = True
    max_patterns: int = 10000


class LLMSettings(BaseModel):
    provider: str = "openai"
    model: str = ""
    api_key: str = ""
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout: int = 60


class RedactionSettings(BaseModel):
    enabled: bool = True
    patterns: list[str] = Field(default_factory=list)


class AutoHealSettings(BaseModel):
    """Root settings model. Loaded from .autoheal/config.toml"""

    general: GeneralSettings = Field(default_factory=GeneralSettings)
    sentinel: SentinelSettings = Field(default_factory=SentinelSettings)
    diagnostics: DiagnosticsSettings = Field(default_factory=DiagnosticsSettings)
    resolution: ResolutionSettings = Field(default_factory=ResolutionSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    redaction: RedactionSettings = Field(default_factory=RedactionSettings)

    @classmethod
    def load(cls, project_dir: Path) -> "AutoHealSettings":
        """Load settings with precedence: defaults → config file → env vars."""
        config_path = project_dir / ".autoheal" / "config.toml"
        if config_path.exists() and tomllib is not None:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            return cls(**data)
        return cls()

    def save(self, project_dir: Path) -> None:
        """Save current settings to config file."""
        if tomli_w is None:
            # Fallback: write TOML manually
            self._save_manual(project_dir)
            return

        config_path = project_dir / ".autoheal" / "config.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "wb") as f:
            tomli_w.dump(self.model_dump(), f)

    def _save_manual(self, project_dir: Path) -> None:
        """Manual TOML writer fallback."""
        config_path = project_dir / ".autoheal" / "config.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = ["# AutoHeal AI Configuration\n"]
        data = self.model_dump()

        for section_name, section in data.items():
            if isinstance(section, dict):
                lines.append(f"\n[{section_name}]")
                for key, value in section.items():
                    if isinstance(value, str):
                        lines.append(f'{key} = "{value}"')
                    elif isinstance(value, bool):
                        lines.append(f"{key} = {'true' if value else 'false'}")
                    elif isinstance(value, list):
                        items = ", ".join(f'"{v}"' for v in value)
                        lines.append(f"{key} = [{items}]")
                    else:
                        lines.append(f"{key} = {value}")

        config_path.write_text("\n".join(lines) + "\n")

    def get_nested(self, key: str) -> Any:
        """Get a nested config value like 'llm.provider'."""
        parts = key.split(".")
        obj: Any = self
        for part in parts:
            if isinstance(obj, BaseModel):
                obj = getattr(obj, part, None)
            elif isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return None
        return obj

    def set_nested(self, key: str, value: str) -> None:
        """Set a nested config value like 'llm.api_key' = 'sk-...'."""
        parts = key.split(".")
        if len(parts) == 2:
            section_name, field = parts
            section_obj = getattr(self, section_name, None)
            if section_obj is not None and hasattr(section_obj, field):
                current = getattr(section_obj, field)
                coerced: Any = value
                if isinstance(current, bool):
                    coerced = value.lower() in ("true", "1", "yes")
                elif isinstance(current, int):
                    coerced = int(value)
                elif isinstance(current, float):
                    coerced = float(value)
                setattr(section_obj, field, coerced)

    def get_llm_model_string(self) -> str:
        """Get the LiteLLM model string like 'openai/gpt-4o'."""
        provider = self.llm.provider
        model = self.llm.model

        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "google": "gemini-2.0-flash",
            "ollama": "llama3.1",
        }

        if not model:
            model = defaults.get(provider, "gpt-4o")

        provider_prefixes = {
            "ollama": "ollama",
            "anthropic": "anthropic",
            "google": "gemini",
            "openai": "openai",
        }

        prefix = provider_prefixes.get(provider, "openai")
        return f"{prefix}/{model}"
