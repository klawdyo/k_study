"""Servidor dos alunos: API JSON + arquivos estáticos da interface (src/k_study/web/). Apenas biblioteca padrão.

Rotas (contrato em docs/arquitetura.md, seção 6). Erros: {"error": "<codigo>", "message": "<texto em português>"}.
  GET    /api/me                                                    {student: {email} | null}
  POST   /api/login          {email}                                {student, created} + Set-Cookie kstudy_sid
  POST   /api/logout                                                {ok: true}
  GET    /api/trails                                                lista de trilhas (+ progresso do aluno logado)
  GET    /api/trails/<slug>                                         o trail.json
  GET    /api/trails/<slug>/files/<caminho>                         qualquer arquivo dentro da pasta da trilha
  GET    /api/trails/<slug>/progress                                {items, answers, notes} do aluno
  PUT    /api/trails/<slug>/progress/items/<bloco>/<item>           {done}
  PUT    /api/trails/<slug>/progress/answers/<bloco>/<item>/<q>     {chosen, correct}
  DELETE /api/trails/<slug>/progress/answers/<bloco>/<item>/<q>
  PUT    /api/trails/<slug>/progress/notes/<bloco>/<item>           {text}   (vazio apaga)
  POST   /api/track          {event: open|beat|leave, ...}          rastreio de tempo
Toda escrita de progresso devolve o estado completo atualizado da trilha.

Segurança: confere o cabeçalho Host (proteção contra DNS rebinding) e, quando há Origin, que seja o mesmo host;
com --lan só aceita clientes de redes privadas e escuta em todas as interfaces; protege contra caminho fora da pasta.
"""
import ipaddress
import json
import mimetypes
import re
import secrets
import socket
from functools import partial
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from . import indexer
from .db import Database, normalize_email

WEB = Path(__file__).parent / "web"
COOKIE = "kstudy_sid"
COOKIE_MAX_AGE = 31536000
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID = re.compile(r"^[\w.\-]{1,100}$")
MAX_BODY = 1_000_000
MAX_NOTE = 50_000

mimetypes.add_type("text/markdown; charset=utf-8", ".md")
mimetypes.add_type("application/json; charset=utf-8", ".json")
mimetypes.add_type("text/javascript; charset=utf-8", ".js")


def inside(root: Path, relative: str) -> Path | None:
    """Resolve `relative` sob `root`; None se tentar sair da pasta."""
    try:
        root = root.resolve()
        target = (root / relative).resolve()
    except (OSError, ValueError):
        return None
    return target if target == root or root in target.parents else None


class App:
    """Estado compartilhado pelas requisições."""

    def __init__(self, content_dir: Path, db: Database, lan: bool = False):
        self.content_dir, self.db, self.lan = Path(content_dir), db, lan


class Handler(BaseHTTPRequestHandler):
    server_version = "KStudy/0.3"

    def __init__(self, app: App, *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            super().handle()
        except (ConnectionError, TimeoutError):      # o navegador fechou a aba no meio da resposta
            pass

    # ---- respostas ----
    def _send(self, status: int, body: bytes, content_type: str, headers: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, obj, headers: dict | None = None):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", headers)

    def _error(self, status: int, code: str, message: str):
        return self._json(status, {"error": code, "message": message})

    def _file(self, path: Path | None):
        if path is None or not path.is_file():
            return self._error(404, "not_found", "Arquivo não encontrado.")
        self._send(200, path.read_bytes(), mimetypes.guess_type(str(path))[0] or "application/octet-stream")

    def _read_raw(self) -> bytes | None:
        """Lê o corpo da requisição (sempre, para o cliente conseguir receber qualquer resposta de erro).
        None se for grande demais (a resposta 413 já foi enviada)."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            remaining = min(max(length, 0), 20 * MAX_BODY)       # descarta o excesso para o cliente receber o 413
            while remaining > 0:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
            self._error(413, "body_too_large", "Corpo da requisição grande demais.")
            return None
        return self.rfile.read(length) if length else b""

    def _parse(self, raw: bytes):
        """Corpo JSON como dict ({} se vazio); None se inválido (a resposta de erro já foi enviada)."""
        if not raw:
            return {}
        try:
            body = json.loads(raw.decode("utf-8"))
        except ValueError:
            self._error(400, "invalid_json", "JSON inválido.")
            return None
        if not isinstance(body, dict):
            self._error(400, "invalid_json", "O corpo deve ser um objeto JSON.")
            return None
        return body

    # ---- segurança ----
    @staticmethod
    def _is_ip(text: str) -> bool:
        try:
            ipaddress.ip_address(text.split("%")[0])
            return True
        except ValueError:
            return False

    @staticmethod
    def _own_names() -> set:
        name = socket.gethostname().lower()
        return {name, name + ".local", name + ".lan"}

    def _client_ok(self) -> bool:
        """Modo --lan: só clientes de rede privada ou loopback (nunca a internet aberta)."""
        try:
            ip = ipaddress.ip_address(self.client_address[0].split("%")[0])
        except ValueError:
            return False
        if getattr(ip, "ipv4_mapped", None):
            ip = ip.ipv4_mapped
        return ip.is_private or ip.is_loopback or ip.is_link_local

    def _host_ok(self) -> bool:
        """Recusa clientes de fora (com --lan) e cabeçalhos Host que não sejam deste computador."""
        if self.app.lan and not self._client_ok():
            self._error(403, "forbidden_client", "Só computadores da rede local podem acessar.")
            return False
        raw = self.headers.get("Host") or ""
        host = raw.strip("[]").lower() if raw.endswith("]") else raw.rsplit(":", 1)[0].strip("[]").lower()
        if host in ("localhost", "127.0.0.1", "::1"):
            return True
        if self.app.lan and (self._is_ip(host) or host in self._own_names()):
            return True
        self._error(403, "forbidden_host", "Endereço de acesso não permitido.")
        return False

    def _origin_ok(self) -> bool:
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).netloc.lower() != (self.headers.get("Host") or "").lower():
            self._error(403, "forbidden_origin", "Origem da requisição não permitida.")
            return False
        return True

    # ---- identidade ----
    def _token(self) -> str | None:
        header = self.headers.get("Cookie")
        if not header:
            return None
        try:
            jar = SimpleCookie(header)
        except Exception:
            return None
        morsel = jar.get(COOKIE)
        return morsel.value if morsel else None

    def _student(self, required: bool = True):
        student = self.app.db.student_for_token(self._token())
        if student is None and required:
            self._error(401, "login_required", "Informe seu e-mail para continuar.")
        return student

    # ---- utilidades de trilha ----
    def _sync(self):
        indexer.sync(self.app.content_dir, self.app.db)

    def _trail_dir(self, slug: str) -> Path | None:
        if not SLUG.match(slug):
            return None
        folder = self.app.content_dir / slug
        return folder if (folder / "trail.json").is_file() else None

    def _need_trail(self, slug: str) -> bool:
        if not SLUG.match(slug) or not self.app.db.trail_exists(slug):
            self._sync()
            if not SLUG.match(slug) or not self.app.db.trail_exists(slug):
                self._error(404, "trail_not_found", "Trilha não encontrada.")
                return False
        return True

    def _need_item(self, slug: str, block: str, item: str) -> bool:
        """A trilha e o item precisam existir no índice (reindexa uma vez se faltar)."""
        if not (ID.match(block) and ID.match(item)):
            self._error(400, "invalid_id", "Identificador de bloco ou item inválido.")
            return False
        if not self._need_trail(slug):
            return False
        if not self.app.db.has_item(slug, block, item):
            self._sync()
            if not self.app.db.has_item(slug, block, item):
                self._error(404, "item_not_found", "Item não encontrado nesta trilha.")
                return False
        return True

    # ---- GET ----
    def do_GET(self):
        if not self._host_ok():
            return None
        path = unquote(urlparse(self.path).path)
        if "\x00" in path:
            return self._error(400, "invalid_path", "Caminho inválido.")
        if path.startswith("/api/"):
            return self._api_get(path.split("/")[2:])
        return self._file(inside(WEB, "index.html" if path in ("", "/") else path.lstrip("/")))

    do_HEAD = do_GET

    def _api_get(self, parts: list[str]):
        db = self.app.db
        if parts == ["me"]:
            student = self._student(required=False)
            return self._json(200, {"student": {"email": student["email"]} if student else None})
        if parts == ["trails"]:
            self._sync()
            student = self._student(required=False)
            return self._json(200, db.list_trails(student["id"] if student else None))
        if len(parts) >= 2 and parts[0] == "trails":
            slug, rest = parts[1], parts[2:]
            folder = self._trail_dir(slug)
            if folder is None:
                self._sync()
                return self._error(404, "trail_not_found", "Trilha não encontrada.")
            if not rest:
                return self._file(folder / "trail.json")
            if rest[0] == "files" and len(rest) > 1:
                return self._file(inside(folder, "/".join(rest[1:])))
            if rest == ["progress"]:
                student = self._student()
                if student is None:
                    return None
                return self._json(200, db.progress_state(student["id"], slug))
        return self._error(404, "not_found", "Rota desconhecida.")

    # ---- escritas ----
    def do_POST(self):
        self._write("POST")

    def do_PUT(self):
        self._write("PUT")

    def do_DELETE(self):
        self._write("DELETE")

    def _write(self, method: str):
        raw = self._read_raw()
        if raw is None or not self._host_ok() or not self._origin_ok():
            return None
        body = self._parse(raw)
        if body is None:
            return None
        parts = [p for p in unquote(urlparse(self.path).path).split("/") if p]
        if parts[:1] != ["api"]:
            return self._error(404, "not_found", "Rota desconhecida.")
        parts = parts[1:]
        if method == "POST":
            if parts == ["login"]:
                return self._login(body)
            if parts == ["logout"]:
                self.app.db.logout(self._token())
                return self._json(200, {"ok": True}, {"Set-Cookie": self._cookie("", 0)})
            if parts == ["track"]:
                return self._track(body)
        elif len(parts) >= 4 and parts[0] == "trails" and parts[2] == "progress":
            return self._progress(method, parts[1], parts[3], parts[4:], body)
        return self._error(404, "not_found", "Rota desconhecida.")

    @staticmethod
    def _cookie(token: str, max_age: int = COOKIE_MAX_AGE) -> str:
        return f"{COOKIE}={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age={max_age}"

    def _login(self, body: dict):
        email = normalize_email(body.get("email"))
        if email is None:
            return self._error(400, "invalid_email", "Informe um e-mail válido.")
        token = secrets.token_urlsafe(32)
        student, created = self.app.db.login(email, token, self.headers.get("User-Agent", ""),
                                             replace_token=self._token())
        return self._json(200, {"student": {"email": student["email"]}, "created": created},
                          {"Set-Cookie": self._cookie(token)})

    def _progress(self, method: str, slug: str, kind: str, rest: list[str], body: dict):
        student = self._student()
        if student is None:
            return None
        db, sid = self.app.db, student["id"]
        if kind in ("items", "notes") and len(rest) == 2 and method == "PUT":
            if not self._need_item(slug, rest[0], rest[1]):
                return None
            if kind == "items":
                db.set_done(sid, slug, rest[0], rest[1], bool(body.get("done")))
            else:
                text = body.get("text", "")
                if not isinstance(text, str):
                    return self._error(400, "invalid_text", "O texto da anotação deve ser uma string.")
                if len(text) > MAX_NOTE:
                    return self._error(413, "note_too_long", "Anotação grande demais.")
                db.set_note(sid, slug, rest[0], rest[1], text)
        elif kind == "answers" and len(rest) == 3 and method in ("PUT", "DELETE"):
            block, item, question = rest
            if not ID.match(question):
                return self._error(400, "invalid_id", "Identificador de questão inválido.")
            if method == "PUT":
                if not self._need_item(slug, block, item):
                    return None
                chosen = body.get("chosen", [])
                if (not isinstance(chosen, list) or len(chosen) > 20
                        or not all(isinstance(c, str) and len(c) <= 100 for c in chosen)):
                    return self._error(400, "invalid_chosen", "O campo chosen deve ser uma lista curta de textos.")
                db.set_answer(sid, slug, block, item, question, chosen, bool(body.get("correct")))
            else:
                if not self._need_trail(slug):
                    return None
                db.delete_answer(sid, slug, block, item, question)
        else:
            return self._error(404, "not_found", "Rota desconhecida.")
        return self._json(200, db.progress_state(sid, slug))

    def _track(self, body: dict):
        student = self._student()
        if student is None:
            return None
        event = body.get("event")
        if event == "open":
            trail, block, item = (str(body.get(k, "")) for k in ("trail", "block", "item"))
            if not self._need_item(trail, block, item):
                return None
            return self._json(200, {"visit": self.app.db.open_visit(student["id"], trail, block, item)})
        if event in ("beat", "leave"):
            visit, seconds = body.get("visit"), body.get("seconds")
            if (isinstance(visit, bool) or not isinstance(visit, int) or isinstance(seconds, bool)
                    or not isinstance(seconds, (int, float))):
                return self._error(400, "invalid_track", "Informe visit e seconds numéricos.")
            total = self.app.db.add_seconds(student["id"], visit, int(seconds))
            if total is None:
                return self._error(404, "visit_not_found", "Visita não encontrada.")
            return self._json(200, {"ok": True, "seconds": total})
        return self._error(400, "invalid_track", "Evento de rastreio desconhecido.")

    def log_message(self, fmt, *args):
        pass


def make_server(content_dir, db, port: int = 8765, host: str = "127.0.0.1", lan: bool = False) -> ThreadingHTTPServer:
    """Cria o servidor (sem iniciá-lo). `db` é um Database ou o caminho do arquivo; indexa o conteúdo antes."""
    if not isinstance(db, Database):
        db = Database(db)
    app = App(Path(content_dir), db, lan)
    indexer.sync(app.content_dir, db)
    server = ThreadingHTTPServer(("0.0.0.0" if lan else host, port), partial(Handler, app))
    server.app = app
    return server


def lan_address() -> str | None:
    """Melhor palpite do endereço deste computador na rede local (nenhum pacote é enviado)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("10.255.255.255", 1))
            return probe.getsockname()[0]
    except OSError:
        return None


def serve(content_dir, db_path, port: int = 8765, lan: bool = False) -> None:
    """Sobe o servidor dos alunos e imprime os endereços (em português)."""
    server = make_server(content_dir, db_path, port, lan=lan)
    trails = server.app.db.query("SELECT slug FROM trails ORDER BY slug")
    print(f"Conteúdo : {Path(content_dir).resolve()}  ({len(trails)} trilha(s))\n"
          f"Banco    : {Path(db_path).resolve()}\n"
          f"Abra     : http://localhost:{port}/")
    if lan:
        address = lan_address()
        print(f"Rede local: http://{address or '<ip-deste-computador>'}:{port}/   (só redes privadas; o acesso é "
              "identificado apenas pelo e-mail informado, sem senha)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()
