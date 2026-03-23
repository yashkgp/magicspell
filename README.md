<p align="center">
  <img src="assets/icon.png" width="80" alt="MagicSpell icon" />
</p>

<h1 align="center">MagicSpell</h1>

<p align="center">
  <strong>LLM-powered proofreading that lives in your macOS menu bar.</strong><br/>
  Select text anywhere, hit a hotkey, and get it corrected in place — powered by Claude or GPT.
</p>

<p align="center">
  <a href="#installation">Installation</a> &bull;
  <a href="#usage">Usage</a> &bull;
  <a href="#slack-bot">Slack Bot</a> &bull;
  <a href="#configuration">Configuration</a> &bull;
  <a href="#development">Development</a> &bull;
  <a href="#architecture">Architecture</a>
</p>

---

## What it does

MagicSpell sits quietly in your menu bar and proofreads text on demand:

1. **Select** any text in any app
2. Press **Cmd+Shift+G**
3. The corrected text **replaces your selection** instantly

It also ships with a **Slack bot** that adds a `/proofread` slash command to your workspace — it reads the channel's recent messages to match its tone automatically.

### Features

- **Instant correction** — global hotkey works in any macOS app
- **Tone switching** — toggle between Casual and Formal from the menu bar
- **Auto-Correct mode** — monitors your clipboard and corrects text as you copy
- **Multi-provider** — supports both Anthropic (Claude) and OpenAI (GPT)
- **Slack integration** — `/proofread` slash command with channel-aware tone matching
- **Start at Login** — optional Launch Agent for automatic startup
- **Standalone .app** — build a native macOS app bundle with py2app

---

## Installation

### Prerequisites

- macOS 12+ (Monterey or later)
- Python 3.11+
- An API key from [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

### Quick start

```bash
# Clone the repo
git clone https://github.com/yashkgp/magicspell.git
cd magicspell

# Install in a virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Add your API key
mkdir -p ~/.magicspell
cp .env.example ~/.magicspell/.env
# Edit ~/.magicspell/.env and add your API key

# Run
magicspell
```

> **macOS permissions:** On first launch, macOS will ask for **Accessibility** access (needed to simulate Cmd+C / Cmd+V). Grant it in System Settings > Privacy & Security > Accessibility.

### Build as a standalone .app

```bash
pip install -e ".[dev]"
make app
make install   # copies MagicSpell.app to /Applications
```

---

## Usage

### Menu bar

Click the menu bar icon to access:

| Menu item | Description |
|-----------|-------------|
| **Casual** / **Formal** | Switch proofreading tone |
| **Auto-Correct Mode** | Automatically correct text when you copy it |
| **Start at Login** | Install/remove the macOS Launch Agent |
| **About MagicSpell** | Version and provider info |

### Hotkey

| Shortcut | Action |
|----------|--------|
| **Cmd+Shift+G** | Proofread and replace selected text |

### How it works

```
Select text  →  Cmd+Shift+G  →  Cmd+C (copy)  →  LLM corrects  →  Cmd+V (paste)
```

The entire flow happens in ~1-2 seconds. Your original clipboard content is preserved.

---

## Slack Bot

MagicSpell includes a Slack bot that adds a `/proofread` slash command. It reads recent channel messages to match the channel's tone automatically.

### Setup

1. **Create a Slack app** at [api.slack.com/apps](https://api.slack.com/apps)
2. Enable **Socket Mode** and generate an App-Level Token (`connections:write` scope)
3. Add **Bot Token Scopes**: `commands`, `channels:history`, `chat:write`
4. Create a **Slash Command**: `/proofread`
5. **Install** the app to your workspace

Add the credentials to `~/.magicspell/.env`:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-level-token
```

### Run

```bash
magicspell-slack
```

The bot connects via **Socket Mode** (WebSocket) — no public URL or ngrok needed.

### Example

```
/proofread i think we shoud deploy the new verion today, its ben tested thorughly
```

> I think we should deploy the new version today, it's been tested thoroughly.

---

## Configuration

All configuration lives in `~/.magicspell/.env` (or environment variables). See [`.env.example`](.env.example) for the full template.

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | One of these | Anthropic API key (uses Claude Sonnet) |
| `OPENAI_API_KEY` | One of these | OpenAI API key (uses GPT-4o Mini) |
| `SLACK_BOT_TOKEN` | For Slack | Bot user OAuth token (`xoxb-...`) |
| `SLACK_SIGNING_SECRET` | For Slack | App signing secret |
| `SLACK_APP_TOKEN` | For Slack | App-level token for Socket Mode (`xapp-...`) |

> If both API keys are set, Anthropic takes priority.

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Type check
mypy magicspell
```

### Project structure

```
magicspell/
├── magicspell/
│   ├── __init__.py          # Package version
│   ├── __main__.py          # CLI entry point
│   ├── app.py               # Menu bar app (rumps)
│   ├── clipboard.py         # Copy/paste simulation
│   ├── config.py            # Environment-based config
│   ├── corrector.py         # Correction orchestrator
│   ├── feedback.py          # Menu bar icon states & notifications
│   ├── hotkey.py            # Global hotkey listener (pynput)
│   ├── launchd.py           # macOS Launch Agent management
│   ├── llm_client.py        # OpenAI & Anthropic API clients
│   ├── models.py            # Data models (Tone, Provider, etc.)
│   ├── prompts.py           # LLM prompt templates
│   ├── slack_bot.py         # Slack Bolt app (/proofread command)
│   └── slack_prompts.py     # Slack-specific prompt engineering
├── tests/
├── assets/                  # Menu bar icons
├── pyproject.toml
├── setup_mac.py             # py2app build config
└── Makefile
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Menu Bar (rumps)                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐ │
│  │ Hotkey   │  │ Clipboard │  │ Feedback Manager │ │
│  │ Listener │  │ Monitor   │  │ (icon + notifs)  │ │
│  └────┬─────┘  └─────┬─────┘  └────────┬─────────┘ │
│       │              │                  │           │
│       └──────┬───────┘                  │           │
│              ▼                          │           │
│         ┌─────────┐                     │           │
│         │Corrector│◄────────────────────┘           │
│         └────┬────┘                                 │
│              ▼                                      │
│     ┌────────────────┐                              │
│     │   LLM Client   │   (OpenAI / Anthropic)      │
│     └────────────────┘                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│               Slack Bot (Bolt + Socket Mode)        │
│  ┌────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ /proofread │─▶│ Channel  │─▶│  LLM Client    │  │
│  │  command   │  │ Context  │  │  (correction)  │  │
│  └────────────┘  └──────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────┘
```

The menu bar app and Slack bot are **independent processes** sharing the same `Corrector` and `LLM Client` code. Each can run standalone.

---

## License

MIT

---

<p align="center">
  Built with Claude Code
</p>
