"""Configuration management - persists settings to a JSON file."""
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.clipboard_manager')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'settings.json')


@dataclass
class AppConfig:
    storage_days: int = 3       # 1, 3, or 5
    max_items: int = 500        # 200, 500, or 1000
    hotkey: str = 'Ctrl+Shift+V'
    auto_start: bool = True
    last_version: str = '1.2.0'
    skip_version: Optional[str] = None  # version user chose "remind later"


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
