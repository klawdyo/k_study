"""HTTP API + static web UI. Standard library only.

Single source of truth:
  * CONTENT  = files inside the data folder, read only through this API.
  * PROGRESS = one JSON file (<data>/progress.json), changed only through this API.
The web UI keeps no state of its own.

Routes
  GET    /api/config                                          <data>/config.json
  GET    /api/content/<path>                                  any file inside the data folder
  GET    /api/progress                                        full state {items, answers, notes}
  PUT    /api/progress/items/<block>/<item>                   {"done": true|false}
  PUT    /api/progress/answers/<block>/<item>/<question>      {"chosen": ["a"], "correct": true}
  DELETE /api/progress/answers/<block>/<item>/<question>      removes the answer
  PUT    /api/progress/notes/<block>/<item>                   {"text": "..."}
Every write route saves the file atomically and returns the full updated state.
"""
import json
import mimetypes
import os
import tempfile
import threading
from datetime import datetime, timezone
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

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


def inside(root: Path, relative: str) -> Path | None:
    """Resolves `relative` under `root`; None if it tries to escape the folder."""
    root = root.resolve()
    target = (root / relative).resolve()
    return target if target == root or root in target.parents else None


class Handler(BaseHTTPRequestHandler):
    server_version = "StudyApp/0.2"

    def __init__(self, data: Path, store: Store, *args, **kwargs):
        self.data, self.store = data, store
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

    # ---- reads ----
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/config":
            return self._file(inside(self.data, "config.json"))
        if path.startswith("/api/content/"):
            return self._file(inside(self.data, path[len("/api/content/"):]))
        if path == "/api/progress":
            with self.store.lock:
                return self._json(200, self.store.read())
        if path.startswith("/api/"):
            return self._json(404, {"error": "unknown route"})
        return self._file(inside(WEB, "index.html" if path in ("", "/") else path.lstrip("/")))

    do_HEAD = do_GET

    # ---- writes ----
    def _mutate(self, method: str):
        parts = [p for p in unquote(urlparse(self.path).path).split("/") if p]    # ['api', 'progress', kind, ...]
        if len(parts) < 4 or parts[:2] != ["api", "progress"]:
            return self._json(404, {"error": "unknown route"})
        body = self._body()
        if body is None:
            return self._json(400, {"error": "invalid JSON"})
        state = self.store.mutate(parts[2], method, parts[3:], body)
        return self._json(404, {"error": "unknown route"}) if state is None else self._json(200, state)

    def do_PUT(self):
        self._mutate("PUT")

    def do_DELETE(self):
        self._mutate("DELETE")

    def log_message(self, fmt, *args):
        pass


def make_server(data: Path, port: int = 8765, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    store = Store(progress_file(data))
    return ThreadingHTTPServer((host, port), partial(Handler, data, store))


def serve(data: Path, port: int = 8765) -> None:
    server = make_server(data, port)
    print(f"Data     : {data}\nProgress : {progress_file(data)}\nOpen     : http://localhost:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
