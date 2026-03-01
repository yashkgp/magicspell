"""Tests for magicspell.config module."""

from __future__ import annotations

import pytest

from magicspell.config import Config
from magicspell.models import LLMProvider


class TestConfigLoad:
    """Tests for Config.load() class method."""

    def test_raises_when_no_api_keys_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Config.load() should raise ValueError when no API keys are in the environment."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ValueError, match="No API key found"):
            Config.load()

    def test_openai_key_produces_openai_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setting OPENAI_API_KEY should produce a config with OpenAI provider."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")

        config = Config.load()

        assert config.provider == LLMProvider.OPENAI
        assert config.api_key == "sk-test-openai-key"

    def test_anthropic_key_produces_anthropic_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Setting ANTHROPIC_API_KEY should produce a config with Anthropic provider."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        config = Config.load()

        assert config.provider == LLMProvider.ANTHROPIC
        assert config.api_key == "sk-ant-test-key"

    def test_anthropic_takes_priority_when_both_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When both API keys are set, Anthropic should take priority."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        config = Config.load()

        assert config.provider == LLMProvider.ANTHROPIC
        assert config.api_key == "sk-ant-test-key"


class TestConfigValidate:
    """Tests for Config.validate() method."""

    def test_validate_raises_on_empty_api_key(self) -> None:
        """Config.validate() should raise ValueError when the API key is empty."""
        config = Config(provider=LLMProvider.OPENAI, api_key="")

        with pytest.raises(ValueError, match="API key cannot be empty"):
            config.validate()

    def test_validate_passes_with_valid_key(self) -> None:
        """Config.validate() should not raise when the API key is non-empty."""
        config = Config(provider=LLMProvider.OPENAI, api_key="sk-valid-key")

        # Should not raise
        config.validate()
