"""Where the data lives. The data folder is NOT part of this repository.

The data folder is chosen, in this order, by:
  1. --data-dir (command line)
  2. STUDY_DATA_DIR (environment variable)
  3. the folder saved for this computer (chosen in the web UI on first run, or with `study data-dir PATH`)
If none of them is set, `study serve` starts in setup mode and the web UI asks for the folder.

    STUDY_WORK_DIR   temporary folder for downloaded audio (default: system temp; never inside the data folder)
"""
import os
import tempfile
from pathlib import Path

from . import settings

ENV_DATA = "STUDY_DATA_DIR"
ENV_WORK = "STUDY_WORK_DIR"


class ConfigError(Exception):
    pass


def is_data_dir(path: Path) -> bool:
    return (path / "config.json").is_file()


def resolve(cli_value: str | None = None) -> tuple[Path | None, str]:
    """Returns (folder or None, source) where source is 'flag', 'env', 'saved' or 'none'."""
    for raw, source in ((cli_value, "flag"), (os.environ.get(ENV_DATA), "env"), (settings.saved_data_dir(), "saved")):
        if raw:
            path = Path(raw).expanduser().resolve()
            if is_data_dir(path):
                return path, source
            if source != "saved":
                raise ConfigError(f"{path} does not look like a data folder (config.json not found).")
    return None, "none"


def data_dir(cli_value: str | None = None) -> Path:
    path, _ = resolve(cli_value)
    if path is None:
        raise ConfigError("Data folder not set. Run `study serve` and choose it in the browser, or run "
                          f"`study data-dir PATH`, or set {ENV_DATA}, or pass --data-dir.")
    return path


def progress_file(data: Path) -> Path:
    return data / "progress.json"


def transcripts_dir(data: Path) -> Path:
    return data / "transcripts"


def work_dir() -> Path:
    return Path(os.environ.get(ENV_WORK) or Path(tempfile.gettempdir()) / "study_work")
