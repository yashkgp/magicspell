# Contributing to MagicSpell

Thanks for your interest in MagicSpell! This guide covers everything you need to set up a development environment, run the app from source, and submit changes.

## Quick start

```bash
git clone https://github.com/yashkgp/magicspell.git
cd magicspell

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

Then create your config:

```bash
mkdir -p ~/.magicspell
cp .env.example ~/.magicspell/.env
# Edit ~/.magicspell/.env and fill in at least OPENAI_API_KEY or ANTHROPIC_API_KEY.
```

If both API keys are set, Anthropic takes priority (see `magicspell/config.py`).

## Run from source

Menu bar app:

```bash
python -m magicspell
```

Slack `/proofread` bot (separate process):

```bash
python -m magicspell.slack_bot
```

The Slack bot also requires `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and `SLACK_APP_TOKEN` in your `~/.magicspell/.env`. See `.env.example` and the README's "Slack bot" section for setup details.

## Build the macOS `.app`

```bash
make app          # build dist/MagicSpell.app via py2app
make install      # copy MagicSpell.app to /Applications
make launch-agent # install ~/Library/LaunchAgents/com.magicspell.app.plist
```

> **Note:** `setup_mac.py` currently hard-codes Anaconda dylib paths (`/opt/homebrew/anaconda3/lib/...`). If you build with a different Python distribution, you'll need to adjust those paths. Making this auto-detect is a tracked follow-up.

## Quality checks

```bash
pytest                          # run the test suite
ruff check magicspell tests     # lint
```

CI runs `ruff` and `pytest` on every push and PR (see `.github/workflows/ci.yml`).

> **Note:** `magicspell/config.py` reads `~/.magicspell/.env` whenever `Config.load()` is called. If you have that file populated locally, two tests in `tests/test_config.py` may fail because the file overrides the test's `monkeypatch.delenv` calls. This is a known issue — tests pass cleanly in CI where no such file exists. Workaround locally: `HOME=/tmp pytest`.

`mypy` is configured in `pyproject.toml` but the codebase currently has pre-existing type errors and is not run in CI yet. Type-cleanup PRs are welcome.

## Code layout

Top-level package at `magicspell/`:

| Module | Responsibility |
|--------|----------------|
| `app.py` | `rumps.App` subclass — menu bar UI, command dispatch |
| `hotkey.py` | Global Cmd+Shift+G hotkey via `NSEvent` global monitor |
| `clipboard.py` | Copy/paste simulation, clipboard polling |
| `config.py` | Env + dotenv-based config loading |
| `corrector.py` | Tone-aware proofreading orchestrator |
| `feedback.py` | Menu bar icon states, notifications |
| `launchd.py` | macOS Launch Agent install/uninstall |
| `llm_client.py` | OpenAI + Anthropic API wrappers |
| `models.py` | `Tone`, `LLMProvider` enums and dataclasses |
| `prompts.py` | System + user prompt templates |
| `slack_bot.py` | Slack Bolt app exposing `/proofread` |
| `slack_prompts.py` | Slack-specific prompt variants |

Tests live in `tests/` and mirror the module names.

## Pull requests

- Keep PRs small and focused on a single concern. Mixed-purpose PRs are hard to review and revert.
- Match the existing commit-message style: title-case, imperative subject (`Add X`, `Fix Y`, `Refactor Z`). Include a body when the why isn't obvious from the subject.
- Run `pytest` and `ruff check magicspell tests` locally before pushing — saves a CI round-trip.
- If you're adding a feature, include tests in the matching `tests/` file.

## Reporting bugs

Open an issue with:
- macOS version
- Python version (`python --version`)
- Steps to reproduce
- Whether you're running from source (`python -m magicspell`) or the bundled `.app`
- Any log output

Thanks for contributing!
