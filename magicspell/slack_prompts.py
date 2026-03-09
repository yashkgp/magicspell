"""Slack-specific prompt enhancements for channel-aware proofreading."""

from __future__ import annotations


def build_channel_context(messages: list[dict]) -> str:
    """Format recent channel messages into a context block.

    Parameters
    ----------
    messages:
        A list of Slack message dicts, each expected to have at least a
        ``"text"`` key.  Messages should be in chronological order
        (oldest first).

    Returns
    -------
    str
        A formatted string summarising recent channel conversation.
    """
    if not messages:
        return ""

    lines: list[str] = []
    for msg in messages:
        text = msg.get("text", "").strip()
        if text:
            lines.append(f"- {text}")

    if not lines:
        return ""

    return "Recent messages in this channel:\n" + "\n".join(lines)


def build_slack_system_prompt(channel_context: str) -> str:
    """Return a system prompt tailored for Slack proofreading.

    The prompt instructs the LLM to fix errors while matching the
    channel's communication style derived from *channel_context*.
    """
    base = (
        "You are a proofreading assistant for Slack messages. "
        "Fix grammar, spelling, and punctuation errors in the user's text. "
        "Preserve technical terms, names, @mentions, #channels, URLs, and emoji. "
        "Output only the corrected text with no extra commentary."
    )

    if channel_context:
        return (
            f"{base}\n\n"
            "Use the following recent channel messages to match the channel's "
            "communication style, tone, and terminology:\n\n"
            f"{channel_context}"
        )

    return base


def build_slack_user_prompt(text: str) -> str:
    """Wrap the user's Slack message in a proofreading instruction."""
    return f"Proofread and correct the following Slack message:\n\n{text}"
