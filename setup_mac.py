"""py2app setup script for building MagicSpell.app."""

from setuptools import setup

import magicspell

APP = ["magicspell/__main__.py"]

DATA_FILES = [
    ("assets", ["assets/icon.png", "assets/icon_active.png", "assets/icon_success.png"]),
]

OPTIONS = {
    "argv_emulation": False,
    "iconfile": None,  # No custom .icns yet — uses default Python icon
    "plist": {
        "CFBundleName": "MagicSpell",
        "CFBundleDisplayName": "MagicSpell",
        "CFBundleIdentifier": "com.magicspell.app",
        "CFBundleVersion": magicspell.__version__,
        "CFBundleShortVersionString": magicspell.__version__,
        "LSUIElement": True,  # Background app — no Dock icon
        "NSHumanReadableCopyright": "MIT License",
        "NSAppleEventsUsageDescription": (
            "MagicSpell needs Accessibility access to read selected text "
            "and simulate keyboard shortcuts."
        ),
    },
    "includes": [
        "rumps",
        "pynput",
        "pyperclip",
        "openai",
        "anthropic",
        "dotenv",
    ],
    "packages": [
        "magicspell",
        "openai",
        "anthropic",
        "pynput",
        "httpx",
        "httpcore",
        "certifi",
        "anyio",
        "sniffio",
        "distro",
        "h11",
        "idna",
    ],
    "resources": ["assets"],
}

setup(
    app=APP,
    name="MagicSpell",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app>=0.28.0"],
)
