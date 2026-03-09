"""Slack bot for MagicSpell – exposes a /proofread slash command."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from magicspell.config import Config
from magicspell.corrector import Corrector
from magicspell.llm_client import create_client
from magicspell.slack_prompts import (
    build_channel_context,
    build_slack_system_prompt,
    build_slack_user_prompt,
)

if TYPE_CHECKING:
    from slack_bolt import Ack, Respond
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)

USAGE_TEXT = (
    "Usage: `/proofread <your message>`\n"
    "I'll fix grammar, spelling, and punctuation while "
    "matching the channel's tone."
)

MAX_CONTEXT_MESSAGES = 10


def _fetch_channel_context(client: WebClient, channel_id: str) -> list[dict]:
    """Fetch recent messages from *channel_id* for context.

    Returns up to ``MAX_CONTEXT_MESSAGES`` messages in chronological order
    (oldest first).  Bot messages and empty messages are filtered out.
    """
    try:
        result = client.conversations_history(
            channel=channel_id,
            limit=MAX_CONTEXT_MESSAGES,
        )
        messages: list[dict] = result.get("messages", [])
        # Filter out bot messages and empty text
        messages = [
            m for m in messages
            if m.get("text") and not m.get("bot_id")
        ]
        # Slack returns newest-first; reverse to chronological order
        messages.reverse()
        return messages
    except Exception:
        logger.exception("Failed to fetch channel history for %s", channel_id)
        return []


def _run_correction(corrector: Corrector, system_prompt: str, user_prompt: str) -> str:
    """Run the async corrector from a synchronous context."""
    loop = asyncio.new_event_loop()
    try:
        corrected = loop.run_until_complete(
            corrector._client.correct(system_prompt, user_prompt)
        )
        return corrected.strip()
    finally:
        loop.close()


def create_app(config: Config | None = None) -> App:
    """Create and configure the Slack Bolt application.

    Parameters
    ----------
    config:
        Optional ``Config`` instance.  When *None* a fresh config is
        loaded via ``Config.load()``.
    """
    if config is None:
        config = Config.load()

    app = App(
        token=config.slack_bot_token,
        signing_secret=config.slack_signing_secret,
    )

    llm_client = create_client(config.provider, config.api_key)
    corrector = Corrector(llm_client)

    @app.command("/proofread")
    def handle_proofread(ack: Ack, command: dict, client: WebClient, respond: Respond) -> None:
        """Handle the ``/proofread`` slash command."""
        ack()  # Acknowledge within 3 s

        text: str = command.get("text", "").strip()
        if not text:
            respond(text=USAGE_TEXT, response_type="ephemeral")
            return

        channel_id: str = command.get("channel_id", "")

        # Fetch channel context for tone matching
        context_messages = _fetch_channel_context(client, channel_id)
        channel_context = build_channel_context(context_messages)
        system_prompt = build_slack_system_prompt(channel_context)
        user_prompt = build_slack_user_prompt(text)

        try:
            corrected = _run_correction(corrector, system_prompt, user_prompt)
        except Exception:
            logger.exception("LLM correction failed")
            respond(
                text=":warning: Sorry, something went wrong while proofreading. Please try again.",
                response_type="ephemeral",
            )
            return

        # Post the corrected message to the channel
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": corrected},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_Original:_ {text}",
                    },
                ],
            },
        ]

        respond(
            text=corrected,
            blocks=blocks,
            response_type="in_channel",
        )

    return app


def main() -> None:
    """Entry point for the ``magicspell-slack`` console script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    config = Config.load()
    app = create_app(config)

    logger.info("Starting MagicSpell Slack bot in Socket Mode")
    handler = SocketModeHandler(app, config.slack_app_token)
    handler.start()


if __name__ == "__main__":
    main()
