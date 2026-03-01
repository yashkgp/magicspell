"""Main MagicSpell application — the integration hub."""
from __future__ import annotations

import asyncio
import threading

import pyperclip
import rumps

from magicspell.models import Tone, LLMProvider
from magicspell.config import Config
from magicspell.llm_client import create_client
from magicspell.corrector import Corrector
from magicspell.clipboard import copy_selected_text, paste_text, ClipboardMonitor
from magicspell.hotkey import HotkeyListener
from magicspell.feedback import FeedbackManager


class MagicSpellApp(rumps.App):
    """Menu-bar application that proofreads selected text via an LLM."""

    def __init__(self) -> None:
        super().__init__("MagicSpell", icon="assets/icon.png", quit_button=None)

        # Core services ------------------------------------------------
        self._config = Config.load()
        self._client = create_client(self._config.provider, self._config.api_key)
        self._corrector = Corrector(self._client)
        self._feedback = FeedbackManager(self)
        self._hotkey_listener = HotkeyListener(self._on_hotkey)

        # Auto-correct state -------------------------------------------
        self._auto_correct: bool = False
        self._clipboard_monitor: ClipboardMonitor | None = None

        # Menu items ---------------------------------------------------
        casual_item = rumps.MenuItem("Casual", callback=self._on_casual)
        casual_item.state = True  # checked by default
        formal_item = rumps.MenuItem("Formal", callback=self._on_formal)

        auto_correct_item = rumps.MenuItem(
            "Auto-Correct Mode", callback=self._on_auto_correct
        )

        provider_item = rumps.MenuItem(
            f"Provider: {self._config.provider.value}"
        )

        quit_item = rumps.MenuItem("Quit", callback=self._on_quit)

        self.menu = [
            casual_item,
            formal_item,
            None,  # separator
            auto_correct_item,
            None,  # separator
            provider_item,
            None,  # separator
            quit_item,
        ]

    # ------------------------------------------------------------------
    # Hotkey handler
    # ------------------------------------------------------------------

    def _on_hotkey(self) -> None:
        """Handle the global Cmd+Shift+G hotkey."""
        threading.Thread(target=self._run_correction, daemon=True).start()

    # ------------------------------------------------------------------
    # Correction flow
    # ------------------------------------------------------------------

    def _run_correction(self) -> None:
        """Execute the correction pipeline in a background thread."""
        loop = asyncio.new_event_loop()
        try:
            self._feedback.show_active()

            text = copy_selected_text()
            if not text:
                self._feedback.notify("MagicSpell", "No text selected")
                self._feedback.show_default()
                return

            result = loop.run_until_complete(self._corrector.correct(text))

            paste_text(result.corrected)
            self._feedback.show_success()
            self._feedback.notify("MagicSpell", "Text corrected!")
        except Exception as exc:  # noqa: BLE001
            self._feedback.show_default()
            self._feedback.notify("MagicSpell Error", str(exc))
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # Tone selection
    # ------------------------------------------------------------------

    def _on_casual(self, sender: rumps.MenuItem) -> None:
        """Set the corrector tone to CASUAL."""
        self._corrector.tone = Tone.CASUAL
        self.menu["Casual"].state = True
        self.menu["Formal"].state = False

    def _on_formal(self, sender: rumps.MenuItem) -> None:
        """Set the corrector tone to FORMAL."""
        self._corrector.tone = Tone.FORMAL
        self.menu["Formal"].state = True
        self.menu["Casual"].state = False

    # ------------------------------------------------------------------
    # Auto-correct mode
    # ------------------------------------------------------------------

    def _on_auto_correct(self, sender: rumps.MenuItem) -> None:
        """Toggle clipboard-based auto-correct mode."""
        self._auto_correct = not self._auto_correct
        sender.state = self._auto_correct

        if self._auto_correct:
            self._clipboard_monitor = ClipboardMonitor(
                callback=self._on_clipboard_change
            )
            self._clipboard_monitor.start()
            self._feedback.notify("MagicSpell", "Auto-Correct Mode enabled")
        else:
            if self._clipboard_monitor is not None:
                self._clipboard_monitor.stop()
                self._clipboard_monitor = None
            self._feedback.notify("MagicSpell", "Auto-Correct Mode disabled")

    def _on_clipboard_change(self, text: str) -> None:
        """Correct clipboard text and write the result back (no paste sim)."""
        loop = asyncio.new_event_loop()
        try:
            self._feedback.show_active()
            result = loop.run_until_complete(self._corrector.correct(text))
            pyperclip.copy(result.corrected)
            self._feedback.show_success()
            self._feedback.notify("MagicSpell", "Clipboard text corrected!")
        except Exception as exc:  # noqa: BLE001
            self._feedback.show_default()
            self._feedback.notify("MagicSpell Error", str(exc))
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # Quit
    # ------------------------------------------------------------------

    def _on_quit(self, sender: rumps.MenuItem) -> None:
        """Clean up resources and quit the application."""
        self._hotkey_listener.stop()
        if self._clipboard_monitor is not None:
            self._clipboard_monitor.stop()
        rumps.quit_application()

    # ------------------------------------------------------------------
    # Run override
    # ------------------------------------------------------------------

    def run(self, **kwargs) -> None:  # type: ignore[override]
        """Start the hotkey listener, then enter the rumps event loop."""
        self._hotkey_listener.start()
        super().run(**kwargs)
