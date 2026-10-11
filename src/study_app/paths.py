"""Where the data lives. The data folder is NOT part of this repository.

    STUDY_DATA_DIR   folder with config.json, progress.json, transcripts/, figures/ and one folder per block
    STUDY_WORK_DIR   temporary folder for downloaded audio (default: system temp; never inside the data folder)
"""
import os
import tempfile
from pathlib import Path

ENV_DATA = "STUDY_DATA_DIR"
ENV_WORK = "STUDY_WORK_DIR"


class ConfigError(Exception):
    pass


def data_dir(cli_value: str | None = None) -> Path:
    raw = cli_value or os.environ.get(ENV_DATA)
    if not raw:
        raise ConfigError(f"Data folder not set. Set the {ENV_DATA} environment variable or pass --data-dir.")
    path = Path(raw).expanduser().resolve()
    if not (path / "config.json").is_file():
        raise ConfigError(f"{path} does not look like a data folder (config.json not found).")
    return path


def progress_file(data: Path) -> Path:
    return data / "progress.json"


def transcripts_dir(data: Path) -> Path:
    return data / "transcripts"


def work_dir() -> Path:
    return Path(os.environ.get(ENV_WORK) or Path(tempfile.gettempdir()) / "study_work")
