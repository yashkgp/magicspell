"""Entry point for MagicSpell."""
from magicspell.app import MagicSpellApp


def main() -> None:
    app = MagicSpellApp()
    app.run()


if __name__ == "__main__":
    main()
