"""High-level correction orchestrator."""

from __future__ import annotations

from magicspell.llm_client import AnthropicClient, BaseLLMClient, OpenAIClient
from magicspell.models import CorrectionResult, LLMProvider, Tone
from magicspell.prompts import build_user_prompt, get_system_prompt


class Corrector:
    """Orchestrates proofreading via an LLM client."""

    def __init__(
        self, client: BaseLLMClient, default_tone: Tone = Tone.CASUAL
    ) -> None:
        self._client = client
        self._tone = default_tone

    @property
    def tone(self) -> Tone:
        """Return the current default tone."""
        return self._tone

    @tone.setter
    def tone(self, value: Tone) -> None:
        """Set the default tone."""
        self._tone = value

    async def correct(
        self, text: str, tone: Tone | None = None
    ) -> CorrectionResult:
        """Proofread *text* and return a CorrectionResult."""
        effective_tone = tone if tone is not None else self._tone

        system_prompt = get_system_prompt(effective_tone)
        user_prompt = build_user_prompt(text)

        corrected = await self._client.correct(system_prompt, user_prompt)
        corrected = corrected.strip()

        if isinstance(self._client, OpenAIClient):
            provider = LLMProvider.OPENAI
        elif isinstance(self._client, AnthropicClient):
            provider = LLMProvider.ANTHROPIC
        elif hasattr(self._client, "provider"):
            provider = self._client.provider
        else:
            msg = f"Unknown client type: {type(self._client)}"
            raise TypeError(msg)

        return CorrectionResult(
            original=text,
            corrected=corrected,
            provider=provider,
        )
