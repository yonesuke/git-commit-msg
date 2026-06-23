# git-commit-msg

A self-contained CLI tool that automatically generates concise, single-line git commit messages. It analyzes your staged changes (`git diff --cached`) and recent repository history (`git log`) using any OpenAI-compatible API (including OpenAI, Ollama, and OpenRouter), perfectly aligning output with your custom engineering guidelines.

Designed to be ultra-lightweight, portable, and fully compatible with **AI Coding Agents** (e.g., `pi-subagent`) and local shell environments.

## Features

- **No Project Dependencies**: Runs via `uv run --no-project` to keep your workspace clean.
- **Agent Friendly**: Exposes a clean stdout interface making it effortless for AI tools to call.
- **Zero Hardcoded Keys**: Keeps credentials entirely separated in your `~/.config` directory.
- **Pure Python**: Utilizes only the Python standard library (`urllib`, `json`, `pathlib`) under the hood—no complex SDK layers.


## Installation

You can pull the script directly from your repository and place it in your local binary path.

```bash
# Create the local bin directory if it doesn't exist
mkdir -p ~/.local/bin
# Download the script
curl -sSL "https://raw.githubusercontent.com/yonesuke/git-commit-msg/main/git-commit-msg.py" -o "$HOME/.local/bin/git-commit-msg.py"
```


## Configuration

The script safely loads API endpoint and model parameters from your XDG-compliant home directory. Create the following configuration file:

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


## Direct Execution

### Standard Usage

To run the script smoothly without locking onto or polluting your current workspace environment:

```bash
uv run --no-project ~/.local/bin/git-commit-msg.py
```


## Engineering Guidelines (Prompts)

The tool instructs the LLM with strict default preferences embedded directly into the payload core:

* Output **ONLY** the commit message string.
* Follow conventional commit definitions (`feat:`, `fix:`, `chore:`, `docs:`).
* Execute descriptions in the imperative mood ("add", not "added").
* Enforce strict size constraints under 50 characters.
