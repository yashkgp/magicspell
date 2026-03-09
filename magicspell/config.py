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

    # Slack integration (optional – only required for the Slack bot)
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_app_token: str = ""

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
            provider = LLMProvider.ANTHROPIC
            api_key = anthropic_key
        elif openai_key:
            provider = LLMProvider.OPENAI
            api_key = openai_key
        else:
            raise ValueError(
                "No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY "
                "in ~/.magicspell/.env or environment."
            )

        return cls(
            provider=provider,
            api_key=api_key,
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET", ""),
            slack_app_token=os.getenv("SLACK_APP_TOKEN", ""),
        )

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("API key cannot be empty.")

    def validate_slack(self) -> None:
        """Validate that Slack-specific configuration is present."""
        missing: list[str] = []
        if not self.slack_bot_token:
            missing.append("SLACK_BOT_TOKEN")
        if not self.slack_signing_secret:
            missing.append("SLACK_SIGNING_SECRET")
        if not self.slack_app_token:
            missing.append("SLACK_APP_TOKEN")
        if missing:
            raise ValueError(
                f"Missing Slack config: {', '.join(missing)}. "
                "Set them in ~/.magicspell/.env or environment."
            )
