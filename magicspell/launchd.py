"""Launch Agent helper for macOS login-item management."""
from __future__ import annotations

import plistlib
import subprocess
from pathlib import Path

LABEL = "com.magicspell.app"
PLIST_NAME = f"{LABEL}.plist"


def _launch_agents_dir() -> Path:
    """Return ~/Library/LaunchAgents, creating it if needed."""
    path = Path.home() / "Library" / "LaunchAgents"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _plist_path() -> Path:
    """Return the full path to the MagicSpell Launch Agent plist."""
    return _launch_agents_dir() / PLIST_NAME


def _default_app_path() -> Path:
    """Return the default installed .app path."""
    return Path("/Applications/MagicSpell.app")


def _build_plist(app_path: Path) -> dict:
    """Build the Launch Agent plist dictionary."""
    executable = app_path / "Contents" / "MacOS" / "MagicSpell"

    return {
        "Label": LABEL,
        "ProgramArguments": [str(executable)],
        "RunAtLoad": True,
        "KeepAlive": False,
        "ProcessType": "Interactive",
    }


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


def is_installed() -> bool:
    """Return True if the Launch Agent plist exists."""
    return _plist_path().exists()


def install(app_path: Path | None = None) -> None:
    """Write the Launch Agent plist and load it via launchctl.

    Parameters:
        app_path: Path to MagicSpell.app.  Defaults to /Applications/MagicSpell.app.
    """
    if app_path is None:
        app_path = _default_app_path()

    plist_data = _build_plist(app_path)
    plist_file = _plist_path()

    with plist_file.open("wb") as f:
        plistlib.dump(plist_data, f)

    # Load the agent so it starts immediately (and on next login)
    subprocess.run(
        ["launchctl", "load", str(plist_file)],
        check=False,
        capture_output=True,
    )


def uninstall() -> None:
    """Unload and remove the Launch Agent plist."""
    plist_file = _plist_path()

    if plist_file.exists():
        subprocess.run(
            ["launchctl", "unload", str(plist_file)],
            check=False,
            capture_output=True,
        )
        plist_file.unlink()
