"""LLM client abstractions for MagicSpell."""

from __future__ import annotations

from abc import ABC, abstractmethod

from magicspell.models import LLMProvider


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def correct(self, system_prompt: str, user_prompt: str) -> str:
        """Send a correction request to the LLM and return the corrected text."""


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI models."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        import openai  # lazy import

        self.model = model
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def correct(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic models."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        import anthropic  # lazy import

        self.model = model
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def correct(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.3,
            max_tokens=4096,
        )
        return response.content[0].text


def create_client(provider: LLMProvider, api_key: str) -> BaseLLMClient:
    """Factory function to create an LLM client for the given provider."""
    if provider == LLMProvider.OPENAI:
        return OpenAIClient(api_key=api_key)
    if provider == LLMProvider.ANTHROPIC:
        return AnthropicClient(api_key=api_key)
    msg = f"Unsupported provider: {provider}"
    raise ValueError(msg)
