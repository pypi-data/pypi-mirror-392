import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".sqlthought"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_MODEL = "openai/gpt-oss-20b"


def ensure_config_dir():
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_config(api_key: str, model: str = DEFAULT_MODEL):
    ensure_config_dir()
    data = {"groq_api_key": api_key, "model": model}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def config_exists() -> bool:
    return CONFIG_FILE.exists()
