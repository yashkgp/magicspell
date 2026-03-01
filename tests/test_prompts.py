"""Tests for the prompts module."""

from magicspell.models import Tone
from magicspell.prompts import build_user_prompt, get_system_prompt


def test_formal_and_casual_are_different() -> None:
    formal = get_system_prompt(Tone.FORMAL)
    casual = get_system_prompt(Tone.CASUAL)
    assert formal != casual


def test_formal_prompt_contains_key_words() -> None:
    prompt = get_system_prompt(Tone.FORMAL)
    assert "proofread" in prompt.lower()
    assert "grammar" in prompt.lower()
    assert "spelling" in prompt.lower()
    assert "punctuation" in prompt.lower()
    assert "formal" in prompt.lower()


def test_casual_prompt_contains_key_words() -> None:
    prompt = get_system_prompt(Tone.CASUAL)
    assert "proofread" in prompt.lower()
    assert "grammar" in prompt.lower()
    assert "spelling" in prompt.lower()
    assert "punctuation" in prompt.lower()
    assert "casual" in prompt.lower()


def test_build_user_prompt_includes_text() -> None:
    text = "This is my sample text."
    prompt = build_user_prompt(text)
    assert text in prompt
