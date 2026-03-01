"""Shared test fixtures for MagicSpell tests."""

from __future__ import annotations

import pytest

from magicspell.models import Tone


@pytest.fixture
def formal_tone() -> Tone:
    return Tone.FORMAL


@pytest.fixture
def casual_tone() -> Tone:
    return Tone.CASUAL
