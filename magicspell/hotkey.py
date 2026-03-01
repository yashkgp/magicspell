"""Global hotkey listener using pynput."""
from __future__ import annotations

from typing import Callable

from pynput.keyboard import GlobalHotKeys


class HotkeyListener:
    """Listens for a global Cmd+Shift+G hotkey and fires *callback*.

    Parameters:
        callback: A no-argument callable invoked when the hotkey is pressed.
    """

    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._listener: GlobalHotKeys | None = None

    def start(self) -> None:
        """Create and start the hotkey listener as a daemon thread."""
        self._listener = GlobalHotKeys({"<cmd>+<shift>+g": self._callback})
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
