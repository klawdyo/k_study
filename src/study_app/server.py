"""HTTP API + static web UI. Standard library only.

Single source of truth:
  * CONTENT  = files inside the data folder, read only through this API.
  * PROGRESS = one JSON file (<data>/progress.json), changed only through this API.
The web UI keeps no state of its own.

Routes
  GET    /api/setup                                           {configured, dataDir, source, home, sep}
  GET    /api/fs?path=<folder>                                list sub-folders (to pick the data folder in the UI)
  PUT    /api/setup                                           {"path": "..."}  choose and save the data folder
  GET    /api/config                                          <data>/config.json            (409 until configured)
  GET    /api/content/<path>                                  any file inside the data folder
  GET    /api/progress                                        full state {items, answers, notes}
  PUT    /api/progress/items/<block>/<item>                   {"done": true|false}
  PUT    /api/progress/answers/<block>/<item>/<question>      {"chosen": ["a"], "correct": true}
  DELETE /api/progress/answers/<block>/<item>/<question>      removes the answer
  PUT    /api/progress/notes/<block>/<item>                   {"text": "..."}
Every progress write saves the file atomically and returns the full updated state.
Localhost only, single user, no authentication: /api/fs lists folder names of this computer.
"""
import json
import mimetypes
import os
import string
import tempfile
import threading
from datetime import datetime, timezone
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from . import paths, settings
from .paths import progress_file

WEB = Path(__file__).parent / "web"

mimetypes.add_type("text/markdown; charset=utf-8", ".md")
mimetypes.add_type("application/json; charset=utf-8", ".json")
mimetypes.add_type("text/javascript; charset=utf-8", ".js")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_state() -> dict:
    return {"items": {}, "answers": {}, "notes": {}}


class Store:
    """Reads and writes the progress file. One lock: the app has a single user."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()

    def read(self) -> dict:
        state = empty_state()
        if self.path.exists():
            try:
                saved = json.loads(self.path.read_text(encoding="utf-8"))
            except ValueError:
                saved = {}
            state.update({k: v for k, v in saved.items() if k in state})
        return state

    def write(self, state: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")   # atomic: never a half-written file
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def mutate(self, kind: str, method: str, parts: list[str], body: dict):
        """Applies one change. Returns the new state, or None if the route is unknown."""
        with self.lock:
            state = self.read()
            if kind == "items" and method == "PUT" and len(parts) == 2:
                state["items"]["/".join(parts)] = {"done": bool(body.get("done")), "at": now()}
            elif kind == "notes" and method == "PUT" and len(parts) == 2:
                text, key = str(body.get("text", "")), "/".join(parts)
                if text.strip():
                    state["notes"][key] = text
                else:
                    state["notes"].pop(key, None)
            elif kind == "answers" and len(parts) == 3:
                key = "/".join(parts[:2])
                if method == "PUT":
                    state["answers"].setdefault(key, {})[parts[2]] = {
                        "chosen": list(body.get("chosen", [])), "correct": bool(body.get("correct")), "at": now()}
                elif method == "DELETE":
                    state["answers"].get(key, {}).pop(parts[2], None)
                else:
                    return None
            else:
                return None
            self.write(state)
            return state


class Context:
    """The data folder in use (None until configured) and its progress store."""

    def __init__(self, data: Path | None, source: str):
        self.data, self.source, self.store = None, "none", None
        self.lock = threading.Lock()
        if data:
            self.use(data, source)

    def use(self, data: Path, source: str) -> None:
        with self.lock:
            self.data, self.source = data, source
            self.store = Store(progress_file(data))


def inside(root: Path, relative: str) -> Path | None:
    """Resolves `relative` under `root`; None if it tries to escape the folder."""
    root = root.resolve()
    target = (root / relative).resolve()
    return target if target == root or root in target.parents else None


def list_folder(raw: str | None, data: Path | None) -> dict:
    """Sub-folders of `raw` (default: the home folder), to browse to the data folder in the UI."""
    start = Path(raw).expanduser() if raw else (data.parent if data else Path.home())
    path = start.resolve() if start.exists() else Path.home()
    if not path.is_dir():
        path = path.parent
    try:
        dirs = sorted((p.name for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")), key=str.lower)
    except OSError:
        dirs = []
    roots = ([f"{c}:\\" for c in string.ascii_uppercase if os.path.exists(f"{c}:\\")] if os.name == "nt" else ["/"])
    parent = str(path.parent) if path.parent != path else None
    return {"path": str(path), "parent": parent, "dirs": dirs, "roots": roots, "sep": os.sep,
            "isDataDir": paths.is_data_dir(path)}


class Handler(BaseHTTPRequestHandler):
    server_version = "StudyApp/0.3"

    def __init__(self, ctx: Context, *args, **kwargs):
        self.ctx = ctx
        super().__init__(*args, **kwargs)

    # ---- responses ----
    def _send(self, status: int, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _file(self, path: Path | None):
        if path is None or not path.is_file():
            return self._json(404, {"error": "file not found"})
        self._send(200, path.read_bytes(), mimetypes.guess_type(str(path))[0] or "application/octet-stream")

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except ValueError:
            return None

    def _setup_info(self) -> dict:
        return {"configured": self.ctx.data is not None, "dataDir": str(self.ctx.data) if self.ctx.data else None,
                "source": self.ctx.source, "home": str(Path.home()), "sep": os.sep,
                "savedDir": settings.saved_data_dir()}

    def _need_data(self) -> bool:
        if self.ctx.data is None:
            self._json(409, {"error": "setup_required"})
            return False
        return True

    # ---- reads ----
    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        if path == "/api/setup":
            return self._json(200, self._setup_info())
        if path == "/api/fs":
            return self._json(200, list_folder((parse_qs(url.query).get("path") or [None])[0], self.ctx.data))
        if path == "/api/config":
            return self._file(inside(self.ctx.data, "config.json")) if self._need_data() else None
        if path.startswith("/api/content/"):
            return self._file(inside(self.ctx.data, path[len("/api/content/"):])) if self._need_data() else None
        if path == "/api/progress":
            if not self._need_data():
                return None
            with self.ctx.store.lock:
                return self._json(200, self.ctx.store.read())
        if path.startswith("/api/"):
            return self._json(404, {"error": "unknown route"})
        return self._file(inside(WEB, "index.html" if path in ("", "/") else path.lstrip("/")))

    do_HEAD = do_GET

    # ---- writes ----
    def _choose_folder(self, body: dict):
        if self.ctx.source in ("flag", "env"):
            return self._json(409, {"error": "locked", "message": "The data folder was fixed by --data-dir or STUDY_DATA_DIR."})
        path = Path(str(body.get("path", ""))).expanduser().resolve()
        if not paths.is_data_dir(path):
            return self._json(400, {"error": "not_a_data_folder", "message": f"{path} has no config.json."})
        settings.save_data_dir(path)
        self.ctx.use(path, "saved")
        return self._json(200, self._setup_info())

    def _mutate(self, method: str):
        parts = [p for p in unquote(urlparse(self.path).path).split("/") if p]
        body = self._body()
        if body is None:
            return self._json(400, {"error": "invalid JSON"})
        if parts == ["api", "setup"] and method == "PUT":
            return self._choose_folder(body)
        if len(parts) < 4 or parts[:2] != ["api", "progress"]:
            return self._json(404, {"error": "unknown route"})
        if not self._need_data():
            return None
        state = self.ctx.store.mutate(parts[2], method, parts[3:], body)
        return self._json(404, {"error": "unknown route"}) if state is None else self._json(200, state)

    def do_PUT(self):
        self._mutate("PUT")

    def do_DELETE(self):
        self._mutate("DELETE")

    def log_message(self, fmt, *args):
        pass


def make_server(data: Path | None, port: int = 8765, host: str = "127.0.0.1", source: str = "flag") -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), partial(Handler, Context(data, source)))


def serve(data: Path | None, port: int = 8765, source: str = "none") -> None:
    server = make_server(data, port, source=source)
    where = f"{data}  (source: {source})" if data else "not set: the browser will ask for it"
    print(f"Data folder : {where}\nOpen        : http://localhost:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
