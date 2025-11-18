import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".gitsnap"
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_config_dir() -> Path:
    """Returns the config directory path."""
    return CONFIG_DIR

def get_config_file() -> Path:
    """Returns the config file path."""
    return CONFIG_FILE

def save_config(data: dict):
    """Saves the configuration data to the config file."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_config() -> dict:
    """Loads the configuration data from the config file."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
