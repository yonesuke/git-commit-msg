"""A self-contained CLI tool that automatically generates concise git commit messages."""

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Path to the configuration file using pathlib.Path
CONFIG_PATH = Path.home() / ".config" / "git-commit-msg" / "config.json"


def load_config() -> dict[str, str]:
    """Loads the API configuration from the local config directory.

    Returns:
        dict[str, str]: A dictionary containing 'base_url', 'api_key', and 'model'.
    """
    if not CONFIG_PATH.exists():
        print(f"Error: Config file not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    try:
        # Read the file content in a single line using pathlib
        config_data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return {
            "base_url": str(config_data["base_url"]),
            "api_key": str(config_data["api_key"]),
            "model": str(config_data["model"]),
        }
    except Exception as e:
        print(f"Error parsing config JSON: {str(e)}", file=sys.stderr)
        sys.exit(1)


def get_git_diff() -> str | None:
    """Retrieves the currently staged git changes (git diff --cached).

    Returns:
        str | None: The staged changes as a string, or None if no changes are staged.
    """
    try:
        diff = (
            subprocess.check_output(["git", "diff", "--cached"]).decode("utf-8").strip()
        )
        return diff if diff else None
    except subprocess.CalledProcessError:
        return None


def get_git_log() -> str:
    """Retrieves the recent 5 commit messages in a single line format.

    Returns:
        str: A summary of recent commit history, or a default message if no history exists.
    """
    try:
        history = (
            subprocess.check_output(["git", "log", "-n", "5", "--oneline"])
            .decode("utf-8")
            .strip()
        )
        return history if history else "No commit history yet."
    except subprocess.CalledProcessError:
        return "No commit history yet."


def get_response_api_res(config: dict[str, str], prompt: str) -> dict | None:
    """Sends a request to the OpenRouter Responses API and returns the raw JSON response.

    Args:
        config (dict[str, str]): Configuration dict containing API credentials.
        prompt (str): The structured prompt containing diff, log, and convention.

    Returns:
        dict | None: The parsed JSON response object from OpenRouter, or None if failed.
    """
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
        "User-Agent": "urllib-client",
    }

    payload = {
        "model": config["model"],
        "input": prompt,
        "reasoning": {"effort": "none"},
    }

    try:
        url = config["base_url"] + "/responses"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=60) as response:
            res_body = response.read().decode("utf-8")
            result: dict = json.loads(res_body)
            return result

    except urllib.error.HTTPError as e:
        print(
            f"HTTP Error ({e.code}): {e.read().decode('utf-8', errors='ignore')}",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"API Error: {str(e)}", file=sys.stderr)

    return None


def get_commit_message(response_json: dict) -> str | None:
    """Extracts and cleans the commit message text from the raw API response JSON.

    Args:
        response_json (dict): The raw JSON response from the Responses API.

    Returns:
        str | None: The extracted, cleaned single-line commit message, or None if parsing fails.
    """
    msg: str = ""

    # Dig into the specific nested structure of /v1/responses (output[0].content[0].text)
    output = response_json.get("output")
    if output and isinstance(output, list) and len(output) > 0:
        content = output[0].get("content")
        if content and isinstance(content, list) and len(content) > 0:
            msg = content[0].get("text", "")

    # Fallback to output_text if the nested layout is missing
    if not msg:
        msg = response_json.get("output_text", "")

    if msg:
        # Remove quotes, grab the first line, and strip wrapping spaces
        cleaned_msg = msg.replace('"', "").replace("'", "").split("\n")[0].strip()
        return cleaned_msg

    return None


def main() -> None:
    """Main execution block.

    Integrates configuration loading, context gathering, API interaction, and final message
    output for Bash/Agent integration.
    """
    # 1. Load configuration details
    config = load_config()

    # 2. Gather git context data
    diff = get_git_diff()
    if not diff:
        print("No staged changes detected.", file=sys.stderr)
        sys.exit(0)

    history = get_git_log()

    # 3. Formulate the specific engineering guidelines
    convention = (
        "- Use conventional commits format (e.g., feat:, fix:, chore:, docs:).\n"
        "- Use imperative mood in the description (e.g., 'add' not 'added').\n"
        "- Keep it under 50 characters."
    )

    prompt = f"""You are an expert developer. Generate a concise, one-line commit message in English based on the following git diff, history, and convention.
Do not wrap the response in quotes, and do not provide any explanations—output ONLY the commit message string.
### Convention
{convention}
### Recent History
{history}
### Git Diff
{diff}"""

    # 4. Fetch and handle the response from LLM
    response_json = get_response_api_res(config, prompt)
    if not response_json:
        sys.exit(1)

    commit_message = get_commit_message(response_json)

    # 5. Output the result cleanly
    if commit_message:
        print(commit_message, end="")
    else:
        print(
            "Failed to parse a valid commit message from the API response.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
