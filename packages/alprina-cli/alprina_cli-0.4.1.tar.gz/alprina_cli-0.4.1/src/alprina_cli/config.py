"""
Configuration management for Alprina CLI.
"""

import yaml
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

ALPRINA_DIR = Path.home() / ".alprina"
CONFIG_FILE = ALPRINA_DIR / "config.json"

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "backend_url": "https://api.alprina.ai",
    "timeout": 30,
    "max_retries": 3,
    "log_level": "INFO",
    "theme": "dark",
    "memory": {
        "enabled": True,
        "api_key": "",  # Set via environment variable MEM0_API_KEY
        "user_id": "default"
    }
}


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            import json
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save configuration to file."""
    ALPRINA_DIR.mkdir(exist_ok=True)

    import json
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def is_admin_mode() -> bool:
    """
    Check if running in admin/development mode (bypasses authentication).

    SECURITY: Requires ALPRINA_ADMIN_KEY environment variable with correct secret.
    This prevents unauthorized users from bypassing authentication even if they
    know about admin mode.

    Usage (for Malte only):
        export ALPRINA_ADMIN_KEY="your-secure-secret-key"

    To generate a new admin key:
        python3 -c "import secrets; print(secrets.token_hex(32))"

    Returns:
        True if admin mode enabled with correct key, False otherwise
    """
    import hashlib

    # Get admin key from environment
    admin_key = os.getenv("ALPRINA_ADMIN_KEY", "")

    if not admin_key:
        return False

    # Valid admin keys (SHA256 hashed for security)
    # To add your key: python3 -c "import hashlib; print(hashlib.sha256(b'YOUR_SECRET').hexdigest())"
    VALID_ADMIN_KEYS = {
        # Malte's secure admin key (generated 2025-01-14)
        "05356d75c4be81c8f528c0c6999aad0d0a3db801036b65ac0801b9137a35a763",
    }

    # Hash the provided key
    key_hash = hashlib.sha256(admin_key.encode()).hexdigest()

    # Check if valid
    return key_hash in VALID_ADMIN_KEYS


def get_api_key() -> str:
    """
    Get API key from environment variable or auth file.

    Returns:
        API key string or None if not found
    """
    # Admin mode - bypass authentication
    if is_admin_mode():
        return "admin_bypass_key"

    # Check environment variable first
    api_key = os.getenv("ALPRINA_API_KEY")
    if api_key:
        return api_key

    # Check auth file
    auth_file = ALPRINA_DIR / "auth.json"
    if auth_file.exists():
        try:
            import json
            with open(auth_file, "r") as f:
                auth_data = json.load(f)
            return auth_data.get("api_key")
        except Exception:
            pass

    return None


def init_config_command():
    """Initialize default configuration."""
    if CONFIG_FILE.exists():
        from rich.prompt import Confirm
        if not Confirm.ask("Config file already exists. Overwrite?", default=False):
            return

    save_config(DEFAULT_CONFIG)

    console.print(Panel(
        f"[green]✓ Configuration initialized[/green]\n\n"
        f"Location: {CONFIG_FILE}\n\n"
        f"Edit this file to customize Alprina settings.",
        title="Config Initialized"
    ))
