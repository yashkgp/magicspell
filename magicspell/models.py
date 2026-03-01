"""Data models for MagicSpell."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Tone(StrEnum):
    """Desired tone for proofreading output."""

    FORMAL = "formal"
    CASUAL = "casual"


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class CorrectionRequest:
    """A request to correct text."""

    text: str
    tone: Tone


@dataclass
class CorrectionResult:
    """The result of a correction."""

    original: str
    corrected: str
    provider: LLMProvider
