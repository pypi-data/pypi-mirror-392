"""
Authentication and token management for Databricks AI.

Handles secure storage and retrieval of Databricks Personal Access Tokens (PAT)
and workspace configuration.
"""

import json
import keyring
from pathlib import Path
from typing import Optional, Dict
import click


SERVICE_NAME = "aiagent-cli"
TOKEN_KEY = "databricks-token"
CONFIG_DIR = Path.home() / ".config" / "aiagent"
CONFIG_FILE = CONFIG_DIR / "config.json"


def setup_auth() -> None:
    """
    Interactive setup for Databricks authentication.

    Prompts the user for:
    1. Databricks Personal Access Token (PAT)
    2. Databricks workspace URL (serving endpoints base URL)

    Stores the token securely in the OS keyring and saves workspace config.
    """
    click.echo("\n" + "=" * 60)
    click.echo("  Databricks Authentication Setup")
    click.echo("=" * 60)
    click.echo("\nTo use AI Agent CLI, you need:")
    click.echo("1. A Databricks Personal Access Token (PAT)")
    click.echo("2. Your Databricks workspace serving endpoints URL")
    click.echo("\nHow to get your Databricks token:")
    click.echo("👉 https://docs.databricks.com/en/dev-tools/auth/pat.html")
    click.echo()

    # Prompt for token
    token = click.prompt(
        "Enter your Databricks token",
        hide_input=True,
        type=str,
    ).strip()

    if not token:
        raise click.ClickException("Token cannot be empty")

    # Prompt for workspace URL
    click.echo("\nYour workspace URL should look like:")
    click.echo("https://your-workspace.cloud.databricks.com/serving-endpoints")
    click.echo()

    workspace_url = click.prompt(
        "Enter your Databricks workspace serving endpoints URL",
        type=str,
    ).strip()

    if not workspace_url:
        raise click.ClickException("Workspace URL cannot be empty")

    # Validate URL format
    if not workspace_url.startswith("https://"):
        raise click.ClickException("Workspace URL must start with https://")

    if not workspace_url.endswith("/serving-endpoints"):
        if workspace_url.endswith("/"):
            workspace_url = workspace_url + "serving-endpoints"
        else:
            workspace_url = workspace_url + "/serving-endpoints"

    # Store token in keyring
    try:
        keyring.set_password(SERVICE_NAME, TOKEN_KEY, token)
    except Exception as e:
        raise click.ClickException(f"Failed to store token securely: {str(e)}")

    # Save workspace config
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = {
            "workspace_url": workspace_url,
            "default_model": "databricks-claude-sonnet-4-5",
        }
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
    except Exception as e:
        raise click.ClickException(f"Failed to save workspace configuration: {str(e)}")

    click.echo("\n" + "=" * 60)
    click.secho("✓ Authentication configured successfully!", fg="green", bold=True)
    click.echo("=" * 60 + "\n")


def get_auth() -> Optional[Dict[str, str]]:
    """
    Retrieve stored authentication credentials.

    Returns:
        Dict with 'token' and 'workspace_url' keys, or None if not configured
    """
    # Get token from keyring
    token = keyring.get_password(SERVICE_NAME, TOKEN_KEY)
    if not token:
        return None

    # Get workspace config
    if not CONFIG_FILE.exists():
        return None

    try:
        config = json.loads(CONFIG_FILE.read_text())
        workspace_url = config.get("workspace_url")
        if not workspace_url:
            return None

        return {
            "token": token,
            "workspace_url": workspace_url,
        }
    except Exception:
        return None


def check_auth() -> bool:
    """
    Check if authentication is configured.

    Returns:
        True if auth is configured, False otherwise
    """
    auth = get_auth()
    return auth is not None


def clear_auth() -> None:
    """
    Clear stored authentication credentials.

    Removes token from keyring and deletes config file.
    """
    try:
        keyring.delete_password(SERVICE_NAME, TOKEN_KEY)
    except keyring.errors.PasswordDeleteError:
        pass  # Token wasn't stored

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def update_token(new_token: str) -> None:
    """
    Update the stored Databricks token.

    Args:
        new_token: New Databricks Personal Access Token
    """
    try:
        keyring.set_password(SERVICE_NAME, TOKEN_KEY, new_token)
    except Exception as e:
        raise click.ClickException(f"Failed to update token: {str(e)}")


# Model configuration
AVAILABLE_MODELS = [
    "databricks-claude-sonnet-4-5",
    "databricks-gpt-5",
    "databricks-gemini-2-5-pro"
]

DEFAULT_MODEL = "databricks-claude-sonnet-4-5"

# User-friendly model names mapping
MODEL_DISPLAY_NAMES = {
    "databricks-claude-sonnet-4-5": "Advanced Model",
    "databricks-gpt-5": "Creative Model",
    "databricks-gemini-2-5-pro": "Analytics Model",
}


def get_model_display_name(technical_name: str) -> str:
    """
    Convert technical model name to user-friendly display name.

    Args:
        technical_name: Technical model identifier (e.g., 'databricks-claude-sonnet-4-5')

    Returns:
        User-friendly name (e.g., 'Advanced Model')
    """
    return MODEL_DISPLAY_NAMES.get(technical_name, technical_name)


def get_default_model() -> str:
    """
    Get the default model from config, or return DEFAULT_MODEL.

    Returns:
        The default model name
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_MODEL

    try:
        config = json.loads(CONFIG_FILE.read_text())
        return config.get("default_model", DEFAULT_MODEL)
    except Exception:
        return DEFAULT_MODEL


def set_default_model(model: str) -> None:
    """
    Save the default model to config.

    Args:
        model: Model name to set as default

    Raises:
        click.ClickException: If model is not in AVAILABLE_MODELS
    """
    if model not in AVAILABLE_MODELS:
        raise click.ClickException(f"Invalid model. Choose from: {', '.join(AVAILABLE_MODELS)}")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass

    config["default_model"] = model
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def select_model_interactive() -> None:
    """
    Interactive model selection interface.

    Displays available models and allows user to select a new default.
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()
    current = get_default_model()

    console.print()
    console.print(Panel.fit(
        "[bold cyan]Select Default AI Model[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("Option", style="cyan", justify="center")
    table.add_column("Model", style="white")
    table.add_column("Status", style="green")

    for i, model in enumerate(AVAILABLE_MODELS, 1):
        status = "✓ Current" if model == current else ""
        friendly_name = get_model_display_name(model)
        table.add_row(str(i), friendly_name, status)

    console.print(table)
    console.print()

    try:
        choice = click.prompt("Select model (1-3)", type=int)
        if 1 <= choice <= len(AVAILABLE_MODELS):
            selected = AVAILABLE_MODELS[choice - 1]
            set_default_model(selected)
            friendly_name = get_model_display_name(selected)
            console.print(f"\n[green]✓ Default model set to: {friendly_name}[/green]\n")
        else:
            console.print("\n[red]✗ Invalid choice[/red]\n")
    except (KeyboardInterrupt, click.Abort):
        console.print("\n[yellow]Model selection cancelled[/yellow]\n")
