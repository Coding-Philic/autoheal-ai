"""LLM client using LiteLLM for unified provider access."""

from __future__ import annotations

import json
from typing import Any

from autoheal.config.settings import AutoHealSettings
from autoheal.llm.redactor import SecretRedactor


class LLMError(Exception):
    """LLM-related error."""
    pass


class LLMClient:
    """Unified LLM client supporting OpenAI, Anthropic, Google, Ollama via LiteLLM."""

    def __init__(self, settings: AutoHealSettings):
        self.settings = settings
        self.model = settings.get_llm_model_string()
        self.api_key = settings.llm.api_key
        self.temperature = settings.llm.temperature
        self.max_tokens = settings.llm.max_tokens
        self.timeout = settings.llm.timeout
        self.redactor = SecretRedactor(settings.redaction)

    async def complete(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send a completion request to the LLM. Returns the text response."""
        import litellm

        # Redact secrets from prompt
        if self.settings.redaction.enabled:
            prompt = self.redactor.redact(prompt)

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                api_key=self.api_key if self.api_key else None,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            raise LLMError(f"LLM call failed: {e}") from e

    async def complete_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Send a completion request and parse the response as JSON."""
        response = await self.complete(prompt, system_prompt)
        return self._parse_json(response)

    def _parse_json(self, response: str) -> dict[str, Any]:
        """Extract and parse JSON from an LLM response."""
        # Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block in markdown code fence
        if "```json" in response:
            try:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                pass

        if "```" in response:
            try:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                pass

        # Try to extract JSON object
        if "{" in response and "}" in response:
            try:
                start = response.index("{")
                end = response.rindex("}") + 1
                return json.loads(response[start:end])
            except (json.JSONDecodeError, ValueError):
                pass

        raise LLMError(f"Could not parse JSON from LLM response: {response[:300]}")
