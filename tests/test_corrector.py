"""Tests for the corrector module."""

from __future__ import annotations

import pytest

from magicspell.corrector import Corrector
from magicspell.llm_client import BaseLLMClient
from magicspell.models import CorrectionResult, LLMProvider, Tone


class MockLLMClient(BaseLLMClient):
    """A mock LLM client that returns a fixed response."""

    provider = LLMProvider.OPENAI  # default provider for testing

    def __init__(self, response: str = "Corrected text.") -> None:
        self.response = response

    async def correct(self, system_prompt: str, user_prompt: str) -> str:
        return self.response


@pytest.mark.asyncio
async def test_correct_returns_correction_result() -> None:
    client = MockLLMClient(response="Hello, world!")
    corrector = Corrector(client=client)

    result = await corrector.correct("hello world")

    assert isinstance(result, CorrectionResult)
    assert result.original == "hello world"
    assert result.corrected == "Hello, world!"


@pytest.mark.asyncio
async def test_correct_uses_provided_tone() -> None:
    client = MockLLMClient()
    corrector = Corrector(client=client, default_tone=Tone.CASUAL)

    # Override with FORMAL for this call — the mock doesn't change output,
    # but we verify that the corrector accepts the tone parameter without error.
    result = await corrector.correct("some text", tone=Tone.FORMAL)
    assert isinstance(result, CorrectionResult)


@pytest.mark.asyncio
async def test_tone_switching() -> None:
    client = MockLLMClient()
    corrector = Corrector(client=client, default_tone=Tone.CASUAL)

    assert corrector.tone == Tone.CASUAL
    corrector.tone = Tone.FORMAL
    assert corrector.tone == Tone.FORMAL


@pytest.mark.asyncio
async def test_corrector_strips_whitespace() -> None:
    client = MockLLMClient(response="  trimmed response  \n")
    corrector = Corrector(client=client)

    result = await corrector.correct("input text")
    assert result.corrected == "trimmed response"


@pytest.mark.asyncio
async def test_unknown_client_raises_type_error() -> None:
    """A client that is not OpenAI or Anthropic should raise TypeError."""

    class UnknownClient(BaseLLMClient):
        async def correct(self, system_prompt: str, user_prompt: str) -> str:
            return "ok"

    corrector = Corrector(client=UnknownClient())
    with pytest.raises(TypeError):
        await corrector.correct("text")
