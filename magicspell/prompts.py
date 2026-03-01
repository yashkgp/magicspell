"""Prompt templates for LLM-based proofreading."""

from __future__ import annotations

from magicspell.models import Tone

SYSTEM_PROMPTS: dict[Tone, str] = {
    Tone.FORMAL: (
        "You are a professional proofreader. Proofread and correct the user's text "
        "for grammar, spelling, and punctuation errors. Output only the corrected text. "
        "Use a formal, professional tone. Do not add new content or change the meaning."
    ),
    Tone.CASUAL: (
        "You are a friendly proofreader. Proofread and correct the user's text "
        "for grammar, spelling, and punctuation errors. Output only the corrected text. "
        "Preserve the casual, conversational tone. Keep contractions and informal style."
    ),
}


def get_system_prompt(tone: Tone) -> str:
    """Return the system prompt for the given tone."""
    return SYSTEM_PROMPTS[tone]


def build_user_prompt(text: str) -> str:
    """Wrap user text in a clear proofreading instruction."""
    return f"Proofread and correct the following text:\n\n{text}"
