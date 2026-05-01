"""py2app setup script for building MagicSpell.app."""

from setuptools import setup
from setuptools.dist import Distribution

import magicspell


class _NoInstallRequires(Distribution):
    """py2app refuses if `install_requires` is set, but modern setuptools
    auto-populates it from `pyproject.toml`'s `[project] dependencies`.
    Clear it at every plausible hook so py2app's truthiness check passes;
    runtime deps are already resolved in the build venv via `pip install -e .`.
    """

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.install_requires = None

    def parse_config_files(self, filenames=None):  # type: ignore[override]
        super().parse_config_files(filenames)
        self.install_requires = None

    def finalize_options(self):  # type: ignore[override]
        super().finalize_options()
        self.install_requires = None


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
    # Anaconda Python's C extensions link many @rpath dylibs that py2app's
    # walker doesn't find under /opt/homebrew/anaconda3/lib/ — bundle them
    # explicitly so Contents/Frameworks/ has them. Discovered via:
    #   find Contents/Resources/lib/python3.13/lib-dynload -name '*.so' \
    #     -exec otool -L {} \; | grep '@rpath' | sort -u
    "frameworks": [
        "/opt/homebrew/anaconda3/lib/libbz2.dylib",
        "/opt/homebrew/anaconda3/lib/libcrypto.3.dylib",
        "/opt/homebrew/anaconda3/lib/libexpat.1.dylib",
        "/opt/homebrew/anaconda3/lib/libffi.8.dylib",
        "/opt/homebrew/anaconda3/lib/liblzma.5.dylib",
        "/opt/homebrew/anaconda3/lib/libmpdec.4.dylib",
        "/opt/homebrew/anaconda3/lib/libsqlite3.0.dylib",
        "/opt/homebrew/anaconda3/lib/libssl.3.dylib",
        "/opt/homebrew/anaconda3/lib/libtcl8.6.dylib",
        "/opt/homebrew/anaconda3/lib/libtk8.6.dylib",
        "/opt/homebrew/anaconda3/lib/libz.1.dylib",
    ],
}

setup(
    app=APP,
    name="MagicSpell",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app>=0.28.0"],
    distclass=_NoInstallRequires,
)
