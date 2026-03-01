from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from magicspell.models import LLMProvider


@dataclass
class Config:
    """Application configuration loaded from environment."""

    provider: LLMProvider
    api_key: str

    @classmethod
    def load(cls) -> Config:
        """Load config from ~/.magicspell/.env and environment variables."""
        # Load from ~/.magicspell/.env if it exists
        env_path = Path.home() / ".magicspell" / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Also load from local .env
        load_dotenv()

        # Determine provider and API key
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if anthropic_key:
            return cls(provider=LLMProvider.ANTHROPIC, api_key=anthropic_key)
        elif openai_key:
            return cls(provider=LLMProvider.OPENAI, api_key=openai_key)
        else:
            raise ValueError(
                "No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY "
                "in ~/.magicspell/.env or environment."
            )

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("API key cannot be empty.")
