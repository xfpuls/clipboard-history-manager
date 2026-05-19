"""Configuration management - persists settings to a JSON file."""
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.clipboard_manager')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'settings.json')

# Hard version — not affected by user config
APP_VERSION = '1.1.0'


@dataclass
class AppConfig:
    storage_days: int = 3
    max_items: int = 500
    hotkey: str = 'Ctrl+Shift+V'
    auto_start: bool = True
    last_version: str = APP_VERSION
    skip_version: Optional[str] = None


def load_config() -> AppConfig:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AppConfig(**{k: v for k, v in data.items() if k in AppConfig.__dataclass_fields__})
        except Exception:
            pass
    return AppConfig()


def save_config(config: AppConfig):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(asdict(config), f, indent=2, ensure_ascii=False)
