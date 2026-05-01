"""Global hotkey listener using NSEvent global monitor.

Hooks into the existing NSApplication run loop (shared with rumps)
instead of creating a separate CFRunLoop thread, avoiding segfaults.
"""
from __future__ import annotations

from collections.abc import Callable

from AppKit import NSEvent, NSKeyDownMask

# macOS virtual keycode for 'G'
_KEYCODE_G = 5
# NSEvent modifier flags
_FLAG_CMD = 1 << 20
_FLAG_SHIFT = 1 << 17


class HotkeyListener:
    """Listens for a global Cmd+Shift+G hotkey and fires *callback*.

    Uses NSEvent.addGlobalMonitorForEventsMatchingMask_handler_ which
    runs on the main thread's event loop — safe to combine with rumps.

    Parameters:
        callback: A no-argument callable invoked when the hotkey is pressed.
    """

    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._monitor: object | None = None
        # Store the handler as a strong instance reference so PyObjC's
        # ObjC block bridge cannot be garbage-collected while the
        # monitor is alive (bare segfault after long uptime otherwise).
        self._handler: Callable | None = None

    def _handle(self, event: object) -> None:
        try:
            flags = event.modifierFlags()
            if (
                event.keyCode() == _KEYCODE_G
                and (flags & _FLAG_CMD)
                and (flags & _FLAG_SHIFT)
            ):
                self._callback()
        except Exception:
            pass

    def start(self) -> None:
        """Register a global event monitor for key-down events."""
        self._handler = self._handle
        self._monitor = (
            NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                NSKeyDownMask, self._handler
            )
        )

    def stop(self) -> None:
        """Remove the global event monitor."""
        if self._monitor is not None:
            NSEvent.removeMonitor_(self._monitor)
            self._monitor = None
