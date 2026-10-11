"""Opens the operating system's own file dialog so the user can point to the data folder's config.json.

The dialog runs on the local desktop in a separate process (tkinter ships with Python on Windows/macOS; on Linux it may
need the `python3-tk` package). The app never lists the disk: it only learns the path the user picked. If tkinter is
missing the UI falls back to pasting the path.
"""
import subprocess
import sys
from pathlib import Path

from . import paths

_SCRIPT = r"""
import sys
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    sys.exit(3)
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)
chosen = filedialog.askopenfilename(
    title="Escolha o arquivo config.json da pasta de dados do curso",
    initialdir=sys.argv[1] or None,
    filetypes=[("config.json", "config.json"), ("Arquivos JSON", "*.json")])
print(chosen)
"""


def pick_config_file(initial: str | None = None) -> dict:
    """Returns {"available": bool, "cancelled": bool, "folder": str|None, "isDataDir": bool}."""
    try:
        result = subprocess.run([sys.executable, "-c", _SCRIPT, initial or ""], capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.SubprocessError):
        return {"available": False, "cancelled": False, "folder": None, "isDataDir": False}
    if result.returncode == 3:
        return {"available": False, "cancelled": False, "folder": None, "isDataDir": False}
    chosen = result.stdout.strip()
    if not chosen:
        return {"available": True, "cancelled": True, "folder": None, "isDataDir": False}
    folder = Path(chosen).parent
    return {"available": True, "cancelled": False, "folder": str(folder), "isDataDir": paths.is_data_dir(folder)}
