"""Servidor do painel do admin (porta 8766). Biblioteca padrão apenas; lê o banco SOMENTE LEITURA.

Rotas (JSON UTF-8, erros no formato {"error": codigo, "message": texto em português})
  GET  /api/admin/session          {"required": bool, "authenticated": bool}  (sempre liberada, usada pela tela de login)
  POST /api/admin/login            {"password"} -> define o cookie kstudy_admin_sid (só com --lan)
  POST /api/admin/logout           apaga a sessão do painel
  GET  /api/admin/overview | students | students/<id> | trails | trails/<slug>   (formatos em queries.py)
  GET  /, /app.js, /style.css      a interface (web/)

Segurança: por padrão escuta só em 127.0.0.1. Com lan=True escuta em 0.0.0.0, exige senha, aceita só clientes de rede
privada e confere o cabeçalho Host (proteção contra DNS rebinding), como o servidor dos alunos.
"""
import hmac
import ipaddress
import json
import mimetypes
import secrets
import socket
import sqlite3
import threading
import time
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from . import queries

WEB = Path(__file__).parent / "web"
COOKIE = "kstudy_admin_sid"
SESSION_SECONDS = 8 * 3600
MAX_FAILURES = 5            # tentativas de senha erradas por janela
FAILURE_WINDOW = 60.0

mimetypes.add_type("text/javascript; charset=utf-8", ".js")
mimetypes.add_type("text/css; charset=utf-8", ".css")


class DatabaseUnavailable(Exception):
    """Banco ausente ou ainda sem as tabelas do k_study."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


class Context:
    """Estado compartilhado entre as requisições: caminho do banco, senha e sessões do painel."""

    def __init__(self, db_path: Path, lan: bool, password: str | None):
        self.db_path = Path(db_path)
        self.lan = lan
        self.password = password
        self.sessions: dict[str, float] = {}      # token -> expiração (monotonic)
        self.failures: list[float] = []
        self.lock = threading.Lock()

    # --- banco -----------------------------------------------------------------------------------------------
    def connect(self) -> sqlite3.Connection:
        if not self.db_path.is_file():
            raise DatabaseUnavailable(
                "database_missing",
                f"O banco de dados ainda não existe ({self.db_path}). Rode `kstudy serve` uma vez e deixe um aluno entrar.")
        try:
            conn = sqlite3.connect(self.db_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
            conn.row_factory = sqlite3.Row
            conn.execute("SELECT 1 FROM students LIMIT 1")
            return conn
        except sqlite3.Error as exc:
            raise DatabaseUnavailable("database_error", f"Não foi possível ler o banco de dados: {exc}") from exc

    # --- sessões do painel -----------------------------------------------------------------------------------
    def new_session(self) -> str:
        token = secrets.token_urlsafe(32)
        with self.lock:
            now = time.monotonic()
            self.sessions = {t: e for t, e in self.sessions.items() if e > now}
            self.sessions[token] = now + SESSION_SECONDS
        return token

    def valid_session(self, token: str | None) -> bool:
        if not token:
            return False
        with self.lock:
            exp = self.sessions.get(token)
            return exp is not None and exp > time.monotonic()

    def drop_session(self, token: str | None) -> None:
        with self.lock:
            self.sessions.pop(token or "", None)

    def blocked(self) -> bool:
        with self.lock:
            now = time.monotonic()
            self.failures = [t for t in self.failures if now - t < FAILURE_WINDOW]
            return len(self.failures) >= MAX_FAILURES

    def fail(self) -> None:
        with self.lock:
            self.failures.append(time.monotonic())

    def check_password(self, given: str) -> bool:
        return bool(self.password) and hmac.compare_digest(given.encode("utf-8"), self.password.encode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    server_version = "kstudy-admin"

    def __init__(self, ctx: Context, *args, **kwargs):
        self.ctx = ctx
        super().__init__(*args, **kwargs)

    # --- respostas -------------------------------------------------------------------------------------------
    def _send(self, status: int, body: bytes, content_type: str, headers: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Connection", "close")
        self.close_connection = True
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, obj, headers: dict | None = None):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", headers)

    def _error(self, status: int, code: str, message: str):
        self._json(status, {"error": code, "message": message})

    # --- verificações ----------------------------------------------------------------------------------------
    def _client_ip(self):
        try:
            ip = ipaddress.ip_address(self.client_address[0].split("%")[0])
        except ValueError:
            return None
        return getattr(ip, "ipv4_mapped", None) or ip

    def _client_ok(self) -> bool:
        ip = self._client_ip()
        if ip is None:
            return False
        if not self.ctx.lan:
            return ip.is_loopback
        return ip.is_private or ip.is_loopback or ip.is_link_local

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").strip().lower()
        host = host[1:host.index("]")] if host.startswith("[") and "]" in host else host.rsplit(":", 1)[0] if host.count(":") == 1 else host
        if host in ("localhost", "127.0.0.1", "::1"):
            return True
        if self.ctx.lan:
            try:
                ipaddress.ip_address(host.split("%")[0])
                return True
            except ValueError:
                name = socket.gethostname().lower()
                return host in (name, name + ".local", name + ".lan")
        return False

    def _guard(self) -> bool:
        if not self._client_ok():
            self._error(403, "forbidden_client", "Este painel só aceita acessos da rede local.")
            return False
        if not self._host_ok():
            self._error(403, "forbidden_host", "Endereço de acesso não permitido para este painel.")
            return False
        return True

    def _cookie(self) -> str | None:
        for part in (self.headers.get("Cookie") or "").split(";"):
            name, _, value = part.strip().partition("=")
            if name == COOKIE:
                return value
        return None

    def _authenticated(self) -> bool:
        return not self.ctx.lan or self.ctx.valid_session(self._cookie())

    def _body(self) -> dict:
        try:
            data = json.loads(self._raw.decode("utf-8"))
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    # --- rotas -----------------------------------------------------------------------------------------------
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self._guard():
            return
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/"):
            return self._api(path)
        self._static(path)

    def _read_body(self) -> bytes:
        """Lê o corpo (limitado) antes de responder, para o cliente não receber a conexão cortada."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return b""
        return self.rfile.read(length) if 0 < length <= 4096 else b""

    def do_POST(self):
        self._raw = self._read_body()
        if not self._guard():
            return
        path = unquote(urlparse(self.path).path)
        if path == "/api/admin/login":
            return self._login()
        if path == "/api/admin/logout":
            self.ctx.drop_session(self._cookie())
            return self._json(200, {"ok": True}, {"Set-Cookie": f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict"})
        self._error(404, "not_found", "Rota não encontrada.")

    def _not_allowed(self):
        self._read_body()
        self._error(405, "method_not_allowed", "Método não permitido.")

    do_PUT = do_DELETE = do_PATCH = _not_allowed

    def _login(self):
        if not self.ctx.lan:
            return self._json(200, {"ok": True})
        if self.ctx.blocked():
            return self._error(429, "too_many_attempts", "Muitas tentativas erradas. Aguarde um minuto.")
        given = self._body().get("password")
        if not isinstance(given, str) or not self.ctx.check_password(given):
            self.ctx.fail()
            return self._error(401, "invalid_password", "Senha incorreta.")
        token = self.ctx.new_session()
        self._json(200, {"ok": True}, {
            "Set-Cookie": f"{COOKIE}={token}; Path=/; Max-Age={SESSION_SECONDS}; HttpOnly; SameSite=Strict"})

    def _api(self, path: str):
        parts = [p for p in path.split("/") if p]          # ["api", "admin", ...]
        if parts[:2] != ["api", "admin"]:
            return self._error(404, "not_found", "Rota não encontrada.")
        route = parts[2:]
        if route == ["session"]:
            return self._json(200, {"required": self.ctx.lan, "authenticated": self._authenticated()})
        if not self._authenticated():
            return self._error(401, "login_required", "Informe a senha do painel.")
        try:
            conn = self.ctx.connect()
        except DatabaseUnavailable as exc:
            return self._error(503, exc.code, exc.message)
        try:
            data = self._dispatch(conn, route)
        except sqlite3.Error as exc:
            return self._error(503, "database_error", f"Erro ao consultar o banco de dados: {exc}")
        finally:
            conn.close()
        if data is None:
            return self._error(404, "not_found", "Recurso não encontrado.")
        self._json(200, data)

    @staticmethod
    def _dispatch(conn, route: list):
        if route == ["overview"]:
            return queries.overview(conn)
        if route == ["students"]:
            return queries.students(conn)
        if route == ["trails"]:
            return queries.trails(conn)
        if len(route) == 2 and route[0] == "students":
            return queries.student(conn, int(route[1])) if route[1].isdigit() else None
        if len(route) == 2 and route[0] == "trails":
            return queries.trail(conn, route[1])
        return None

    def _static(self, path: str):
        name = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (WEB / name).resolve()
        if WEB.resolve() not in target.parents or not target.is_file():
            return self._error(404, "not_found", "Arquivo não encontrado.")
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") and "charset" not in ctype:
            ctype += "; charset=utf-8"
        self._send(200, target.read_bytes(), ctype)

    def log_message(self, fmt, *args):
        pass


def make_server(db_path, port: int = 8766, lan: bool = False, password: str | None = None) -> ThreadingHTTPServer:
    """Cria o servidor sem iniciá-lo (usado pelos testes). Com lan=True a senha é obrigatória."""
    if lan and not password:
        raise ValueError("O modo --lan do painel exige uma senha (--password ou K_STUDY_ADMIN_PASSWORD).")
    ctx = Context(Path(db_path), lan, password)
    server = ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", port), partial(Handler, ctx))
    server.daemon_threads = True
    server.ctx = ctx
    return server


def lan_address() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return None


def run(db_path, port: int = 8766, lan: bool = False, password: str | None = None) -> None:
    """Sobe o painel e bloqueia até Ctrl+C. Levanta ValueError (mensagem em português) se lan=True sem senha."""
    server = make_server(db_path, port, lan, password)
    print(f"Painel do admin: http://127.0.0.1:{server.server_address[1]}/")
    if lan:
        print(f"Rede local: http://{lan_address() or '<ip-deste-computador>'}:{server.server_address[1]}/"
              "   (só redes privadas; exige a senha informada)")
    if not Path(db_path).is_file():
        print(f"Aviso: o banco {db_path} ainda não existe; o painel mostrará um aviso até ele ser criado.")
    print("Pressione Ctrl+C para parar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPainel encerrado.")
    finally:
        server.server_close()
