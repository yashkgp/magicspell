"""Tests for the MagicSpell Slack bot and prompt helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from magicspell.slack_prompts import (
    build_channel_context,
    build_slack_system_prompt,
    build_slack_user_prompt,
)

# ---------------------------------------------------------------------------
# slack_prompts tests
# ---------------------------------------------------------------------------


class TestBuildChannelContext:
    """Tests for ``build_channel_context``."""

    def test_empty_list_returns_empty_string(self) -> None:
        assert build_channel_context([]) == ""

    def test_filters_empty_text(self) -> None:
        messages = [{"text": ""}, {"text": "   "}, {"text": "hello"}]
        result = build_channel_context(messages)
        assert "hello" in result
        # Only one bullet line expected
        assert result.count("- ") == 1

    def test_formats_messages_as_bullet_list(self) -> None:
        messages = [
            {"text": "first message"},
            {"text": "second message"},
        ]
        result = build_channel_context(messages)
        assert result.startswith("Recent messages in this channel:")
        assert "- first message" in result
        assert "- second message" in result

    def test_returns_empty_for_all_blank_messages(self) -> None:
        messages = [{"text": ""}, {"text": "  "}]
        assert build_channel_context(messages) == ""


class TestBuildSlackSystemPrompt:
    """Tests for ``build_slack_system_prompt``."""

    def test_without_context(self) -> None:
        prompt = build_slack_system_prompt("")
        assert "proofreading assistant" in prompt
        assert "recent channel messages" not in prompt.lower()

    def test_with_context(self) -> None:
        context = "Recent messages in this channel:\n- hey team\n- ship it"
        prompt = build_slack_system_prompt(context)
        assert "proofreading assistant" in prompt
        assert "hey team" in prompt
        assert "ship it" in prompt
        assert "communication style" in prompt


class TestBuildSlackUserPrompt:
    """Tests for ``build_slack_user_prompt``."""

    def test_contains_user_text(self) -> None:
        prompt = build_slack_user_prompt("hello wrold")
        assert "hello wrold" in prompt
        assert "Proofread" in prompt


# ---------------------------------------------------------------------------
# slack_bot tests
# ---------------------------------------------------------------------------


class TestFetchChannelContext:
    """Tests for ``_fetch_channel_context``."""

    def test_returns_messages_in_chronological_order(self) -> None:
        from magicspell.slack_bot import _fetch_channel_context

        mock_client = MagicMock()
        mock_client.conversations_history.return_value = {
            "messages": [
                {"text": "newest", "ts": "3"},
                {"text": "middle", "ts": "2"},
                {"text": "oldest", "ts": "1"},
            ],
        }

        result = _fetch_channel_context(mock_client, "C123")
        assert len(result) == 3
        # Should be reversed to chronological (oldest first)
        assert result[0]["text"] == "oldest"
        assert result[-1]["text"] == "newest"

    def test_filters_bot_messages(self) -> None:
        from magicspell.slack_bot import _fetch_channel_context

        mock_client = MagicMock()
        mock_client.conversations_history.return_value = {
            "messages": [
                {"text": "human msg", "ts": "2"},
                {"text": "bot msg", "ts": "1", "bot_id": "B123"},
            ],
        }

        result = _fetch_channel_context(mock_client, "C123")
        assert len(result) == 1
        assert result[0]["text"] == "human msg"

    def test_returns_empty_on_api_error(self) -> None:
        from magicspell.slack_bot import _fetch_channel_context

        mock_client = MagicMock()
        mock_client.conversations_history.side_effect = Exception("API error")

        result = _fetch_channel_context(mock_client, "C123")
        assert result == []


class TestHandleProofread:
    """Tests for the ``/proofread`` slash command handler."""

    def _make_config(self) -> MagicMock:
        config = MagicMock()
        config.provider = "openai"
        config.api_key = "test-key"
        config.slack_bot_token = "xoxb-test"
        config.slack_signing_secret = "test-secret"
        config.slack_app_token = "xapp-test"
        return config

    @patch("magicspell.slack_bot.create_client")
    @patch("magicspell.slack_bot.App")
    def test_empty_text_returns_usage(
        self, mock_app_cls: MagicMock, mock_create: MagicMock,
    ) -> None:
        """``/proofread`` with no text should reply with usage instructions."""
        from magicspell.slack_bot import USAGE_TEXT, create_app

        # Set up the mock App so we can capture the registered handler
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        handlers: dict[str, object] = {}

        def capture_command(cmd: str):
            def decorator(fn):
                handlers[cmd] = fn
                return fn
            return decorator

        mock_app.command = capture_command

        create_app(self._make_config())

        handler = handlers["/proofread"]
        ack = MagicMock()
        respond = MagicMock()
        command = {"text": "", "channel_id": "C123"}

        handler(ack=ack, command=command, client=MagicMock(), respond=respond)

        ack.assert_called_once()
        respond.assert_called_once()
        call_kwargs = respond.call_args
        assert call_kwargs.kwargs["text"] == USAGE_TEXT
        assert call_kwargs.kwargs["response_type"] == "ephemeral"

    @patch("magicspell.slack_bot._run_correction", return_value="hello world")
    @patch("magicspell.slack_bot._fetch_channel_context", return_value=[])
    @patch("magicspell.slack_bot.create_client")
    @patch("magicspell.slack_bot.App")
    def test_corrects_text_and_posts(
        self,
        mock_app_cls: MagicMock,
        mock_create: MagicMock,
        mock_fetch: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """``/proofread hello wrold`` should return corrected text."""
        from magicspell.slack_bot import create_app

        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        handlers: dict[str, object] = {}

        def capture_command(cmd: str):
            def decorator(fn):
                handlers[cmd] = fn
                return fn
            return decorator

        mock_app.command = capture_command

        create_app(self._make_config())

        handler = handlers["/proofread"]
        ack = MagicMock()
        respond = MagicMock()
        command = {"text": "hello wrold", "channel_id": "C123"}

        handler(ack=ack, command=command, client=MagicMock(), respond=respond)

        ack.assert_called_once()
        respond.assert_called_once()
        call_kwargs = respond.call_args
        assert call_kwargs.kwargs["response_type"] == "in_channel"
        assert call_kwargs.kwargs["text"] == "hello world"
        # Verify blocks contain original text
        blocks = call_kwargs.kwargs["blocks"]
        assert any("hello wrold" in str(b) for b in blocks)

    @patch("magicspell.slack_bot._run_correction", side_effect=Exception("LLM down"))
    @patch("magicspell.slack_bot._fetch_channel_context", return_value=[])
    @patch("magicspell.slack_bot.create_client")
    @patch("magicspell.slack_bot.App")
    def test_llm_error_returns_ephemeral_error(
        self,
        mock_app_cls: MagicMock,
        mock_create: MagicMock,
        mock_fetch: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """LLM failure should produce a user-friendly ephemeral error."""
        from magicspell.slack_bot import create_app

        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        handlers: dict[str, object] = {}

        def capture_command(cmd: str):
            def decorator(fn):
                handlers[cmd] = fn
                return fn
            return decorator

        mock_app.command = capture_command

        create_app(self._make_config())

        handler = handlers["/proofread"]
        ack = MagicMock()
        respond = MagicMock()
        command = {"text": "fix this", "channel_id": "C123"}

        handler(ack=ack, command=command, client=MagicMock(), respond=respond)

        ack.assert_called_once()
        respond.assert_called_once()
        call_kwargs = respond.call_args
        assert call_kwargs.kwargs["response_type"] == "ephemeral"
        assert "went wrong" in call_kwargs.kwargs["text"]

    @patch("magicspell.slack_bot._run_correction", return_value="hi team, how are you?")
    @patch("magicspell.slack_bot.create_client")
    @patch("magicspell.slack_bot.App")
    def test_channel_context_is_fetched_and_used(
        self,
        mock_app_cls: MagicMock,
        mock_create: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """The handler should fetch channel context and pass it through prompts."""
        from magicspell.slack_bot import create_app

        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        handlers: dict[str, object] = {}

        def capture_command(cmd: str):
            def decorator(fn):
                handlers[cmd] = fn
                return fn
            return decorator

        mock_app.command = capture_command

        create_app(self._make_config())

        handler = handlers["/proofread"]
        ack = MagicMock()
        respond = MagicMock()
        mock_client = MagicMock()
        mock_client.conversations_history.return_value = {
            "messages": [
                {"text": "yo whats up", "ts": "2"},
                {"text": "hey all", "ts": "1"},
            ],
        }
        command = {"text": "hi teem, how r you?", "channel_id": "C456"}

        handler(ack=ack, command=command, client=mock_client, respond=respond)

        # Verify conversations_history was called for context
        mock_client.conversations_history.assert_called_once_with(
            channel="C456", limit=10,
        )
        # Verify correction was called
        mock_run.assert_called_once()
        # The system prompt passed to _run_correction should contain channel context
        call_args = mock_run.call_args
        system_prompt = call_args[1].get("system_prompt") or call_args[0][1]
        assert "hey all" in system_prompt or "yo whats up" in system_prompt
