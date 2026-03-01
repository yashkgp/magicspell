"""Clipboard utilities using pyperclip and pynput."""
from __future__ import annotations

import threading
import time
from collections.abc import Callable

import pyperclip
from pynput.keyboard import Controller, Key

_keyboard = Controller()


def copy_selected_text() -> str | None:
    """Copy the currently selected text and return it.

    Saves and restores the previous clipboard content so the user's
    clipboard is not clobbered.

    Returns:
        The selected text, or ``None`` if nothing was selected.
    """
    # Save whatever is on the clipboard right now
    original = pyperclip.paste()

    # Simulate Cmd+C to copy the current selection
    _keyboard.press(Key.cmd)
    _keyboard.tap("c")
    _keyboard.release(Key.cmd)

    # Give the system a moment to update the clipboard
    time.sleep(0.1)

    text = pyperclip.paste()

    # Restore the original clipboard content
    pyperclip.copy(original)

    if not text or text == original:
        return None
    return text


def paste_text(text: str) -> None:
    """Place *text* on the clipboard and simulate Cmd+V to paste it."""
    pyperclip.copy(text)
    time.sleep(0.05)

    _keyboard.press(Key.cmd)
    _keyboard.tap("v")
    _keyboard.release(Key.cmd)


class ClipboardMonitor:
    """Polls the clipboard for changes and invokes a callback on new content.

    Parameters:
        callback: Called with the new clipboard text whenever a change is
            detected.
        interval: Seconds between polls (default ``1.0``).
    """

    def __init__(self, callback: Callable[[str], None], interval: float = 1.0) -> None:
        self._callback = callback
        self._interval = interval
        self._last_content: str = ""
        self._running: bool = False
        self._lock: threading.Lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start polling the clipboard on a background daemon thread."""
        self._running = True
        self._last_content = pyperclip.paste()
        thread = threading.Thread(target=self._poll, daemon=True)
        thread.start()

    def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _poll(self) -> None:
        while self._running:
            with self._lock:
                current = pyperclip.paste()
                if current and current != self._last_content:
                    self._last_content = current
                    self._callback(current)
            time.sleep(self._interval)
