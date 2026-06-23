# git-commit-msg

A self-contained CLI tool that automatically generates concise, single-line git commit messages. It analyzes your staged changes (`git diff --cached`) and recent repository history (`git log`) using any OpenAI-compatible API (including OpenAI, Ollama, and OpenRouter), perfectly aligning output with your custom engineering guidelines.

Designed to be ultra-lightweight, portable, and fully compatible with **AI Coding Agents** (e.g., `pi-subagent`) and local shell environments.

## Features

- **No Installation Required**: Run directly from URL without downloading anything
- **Flexible Execution**: Works with Python 3.10+ or isolated `uv run --no-project`
- **Agent Friendly**: Clean stdout interface for AI tools and shell workflows
- **Zero Hardcoded Keys**: API credentials stored securely in `~/.config`
- **Pure Python**: Uses only the standard library (`urllib`, `json`, `pathlib`)


## Quick Start

### Zero Setup (URL-based)

Just run it straight from the repository—no installation needed:

```bash
# Using uv (recommended, isolated with Python 3.10+)
git commit -m "$(uv run --no-project --python ">=3.10" "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py")"

# Or pipe directly into Python 3.10+
git commit -m "$(curl -s "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py" | python)"
```

That's it! If you have a config file at `~/.config/git-commit-msg/config.json` (see Configuration below), it'll just work.


## Configuration

The script loads API endpoint and model parameters from your XDG-compliant home directory. Create this file:

**Path:** `~/.config/git-commit-msg/config.json`

### Example Configuration

1. OpenAI
```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "YOUR_OPENAI_API_KEY_HERE",
  "model": "YOUR_FAVORITE_OPENAI_MODEL_HERE"
}
```

2. OpenRouter
```json
{
  "base_url": "https://openrouter.ai/api/v1",
  "api_key": "YOUR_OPENROUTER_API_KEY_HERE",
  "model": "YOUR_FAVORITE_OPENROUTER_MODEL_HERE"
}
```
By the way, I am using [OpenRouter with the DeepSeek model](https://openrouter.ai/deepseek/deepseek-v4-flash) for my own workflow, and it works great with very cheap API costs.

3. Ollama (Local LLM)
```json
{
  "base_url": "http://localhost:11434/v1",
  "api_key": "dummy",
  "model": "YOUR_FAVORITE_OLLAMA_MODEL_HERE"
}
```


## Usage Patterns

Pick whatever fits your workflow best.

### 1. Simple Command Substitutions (On-the-fly)

```bash
# 1. uv + remote URL (simplest, always fresh with Python 3.10+)
git commit -m "$(uv run --no-project --python ">=3.10" "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py")"

# 2. Python + curl pipe (no dependencies, requires Python 3.10+)
git commit -m "$(curl -s "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py" | python)"

# 3. uv + local file (faster if you cache it, with Python 3.10+)
uv run --no-project --python ">=3.10" ./git-commit-msg.py

# 4. Pure Python (requires Python 3.10+)
python ./git-commit-msg.py
```

### 2. Git Alias (Recommended for Global Integration)

You can register the remote execution straight into your ~/.gitconfig as a native git subcommand (e.g., git cm). Run the following command to set it up:

```bash
# If you prefer to use uv (isolated environment with Python 3.10+)
git config --global alias.cm '!f() { msg=$(uv run --no-project --python ">=3.10" "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py" 2>/dev/null); if [ -n "$msg" ]; then git commit -m "$msg"; else echo "Failed to generate commit message." >&2; return 1; fi; }; f'
# If you prefer to use Python directly
git config --global alias.cm '!f() { msg=$(curl -sSL "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py" | python 2>/dev/null); if [ -n "$msg" ]; then git commit -m "$msg"; else echo "Failed to generate commit message." >&2; return 1; fi; }; f'
```

Once set, you can simply run:

```bash
git add .  # Stage your changes
git cm     # Commit with AI-generated message
```

## Optional: Local Installation

If you prefer to download and reuse locally:

```bash
# Download
mkdir -p ~/.local/bin
curl -sSL "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py" -o ~/.local/bin/git-commit-msg.py
chmod +x ~/.local/bin/git-commit-msg.py

# Then use it like any installed command
git commit -m "$(python ~/.local/bin/git-commit-msg.py)"

# Or via uv with Python 3.10+
git commit -m "$(uv run --no-project --python ">=3.10" ~/.local/bin/git-commit-msg.py)"
```


## Engineering Guidelines (Prompts)

The tool instructs the LLM with strict default preferences embedded directly into the payload core:

* Output **ONLY** the commit message string.
* Follow conventional commit definitions (`feat:`, `fix:`, `chore:`, `docs:`).
* Execute descriptions in the imperative mood ("add", not "added").
* Enforce strict size constraints under 50 characters.
