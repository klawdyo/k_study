"""Per-machine settings (where the data folder is on THIS computer). Stored outside the data folder and outside
any synced folder, because the path differs from one computer to another (Windows drive letters, Linux mount points).

    Windows : %APPDATA%\\study-app\\settings.json
    Linux/macOS : $XDG_CONFIG_HOME/study-app/settings.json  (default ~/.config/study-app/settings.json)
    override for tests: STUDY_SETTINGS_FILE
"""
import json
import os
import sys
from pathlib import Path


def settings_file() -> Path:
    override = os.environ.get("STUDY_SETTINGS_FILE")
    if override:
        return Path(override)
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "study-app" / "settings.json"


def load() -> dict:
    try:
        return json.loads(settings_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_data_dir(path: Path) -> None:
    target = settings_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    settings = load()
    settings["data_dir"] = str(path)
    target.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def saved_data_dir() -> str | None:
    return load().get("data_dir")
