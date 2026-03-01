"""Visual feedback via the macOS menu bar (rumps)."""
from __future__ import annotations

import threading

import rumps


class FeedbackManager:
    """Manages menu-bar icon transitions and system notifications.

    Parameters:
        app: The :class:`rumps.App` instance whose icon will be manipulated.
    """

    ICON_DEFAULT: str = "assets/icon.png"
    ICON_ACTIVE: str = "assets/icon_active.png"
    ICON_SUCCESS: str = "assets/icon_success.png"

    def __init__(self, app: rumps.App) -> None:
        self._app = app

    # ------------------------------------------------------------------
    # Icon helpers
    # ------------------------------------------------------------------

    def show_active(self) -> None:
        """Switch the menu-bar icon to the *active* (processing) state."""
        self._app.icon = self.ICON_ACTIVE

    def show_success(self) -> None:
        """Show the *success* icon, then revert to default after 1.5 s."""
        self._app.icon = self.ICON_SUCCESS
        timer = threading.Timer(1.5, self.show_default)
        timer.daemon = True
        timer.start()

    def show_default(self) -> None:
        """Revert the menu-bar icon to its default state."""
        self._app.icon = self.ICON_DEFAULT

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    @staticmethod
    def notify(title: str, message: str) -> None:
        """Display a macOS notification via rumps."""
        rumps.notification(title, "", message)
