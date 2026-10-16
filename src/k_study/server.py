"""Servidor do k_study: API JSON + interface do aluno (/) + área administrativa (/admin/). Apenas biblioteca padrão.

O contrato é docs/arquitetura.md (seções 5 a 7). Erros: {"error": "<codigo>", "message": "<texto em português>"}.
NÃO existe rota que sirva arquivo por caminho: o conteúdo é pedido por ids e traduzido por consulta ao índice
(items.path, items.transcript, assets); só arquivos da lista permitida saem daqui.

Segurança: confere o cabeçalho Host (DNS rebinding) e a Origin; CSRF em toda escrita; sessão por cookie HttpOnly;
limite de tentativas de login; cabeçalhos de segurança em todas as respostas; sem traceback para o cliente;
com --lan só aceita clientes de redes privadas e escuta em todas as interfaces.
"""
import ipaddress
import json
import mimetypes
import os
import re
import secrets
import signal
import socket
import sqlite3
import sys
from functools import partial
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from . import indexer, oauth, security
from .db import Database

WEB = Path(__file__).parent / "web"
ADMIN_WEB = Path(__file__).parent / "admin" / "web"
COOKIE = "kstudy_sid"
COOKIE_MAX_AGE = 30 * 24 * 3600
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID = re.compile(r"^[\w.\-]{1,100}$")
FIGURE = re.compile(r"^[A-Za-z0-9._-]{1,200}$")
MAX_BODY = security.MAX_BODY
MAX_ZIP = 100 * 1024 * 1024
MAX_NOTE = 50_000

CONTENT_TYPES = {".md": "text/markdown; charset=utf-8", ".json": "application/json; charset=utf-8",
                 ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".webp": "image/webp", ".gif": "image/gif"}
mimetypes.add_type("text/javascript; charset=utf-8", ".js")
mimetypes.add_type("text/css; charset=utf-8", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


def inside(root: Path, relative: str) -> Path | None:
    """Resolve `relative` sob `root`; None se tentar sair da pasta."""
    try:
        root = root.resolve()
        target = (root / relative).resolve()
    except (OSError, ValueError):
        return None
    return target if target == root or root in target.parents else None


def specs_root() -> Path:
    return Path(os.environ.get("K_STUDY_SPECS_ROOT") or Path(__file__).resolve().parents[2])


class App:
    """Estado compartilhado pelas requisições."""

    def __init__(self, content_dir: Path, db: Database, lan: bool = False, secret: str = "", https: bool = False,
                 specs: Path | None = None):
        self.content_dir, self.db, self.lan = Path(content_dir), db, lan
        self.secret, self.https = secret, https
        self.specs = Path(specs) if specs else specs_root()
        self.allowed_hosts = {h.strip().lower() for h in (os.environ.get("K_STUDY_ALLOWED_HOSTS") or "").split(",") if h.strip()}

    @property
    def google(self) -> dict | None:
        """Configuração do Google (None = sem botão). Lida do ambiente a cada uso: o .env é carregado ao subir o servidor."""
        return oauth.google_config()


class Handler(BaseHTTPRequestHandler):
    server_version = "KStudy"
    sys_version = ""
    protocol_version = "HTTP/1.0"
    timeout = 60              # segundos sem receber bytes: derruba conexões paradas (slowloris)

    def __init__(self, app: App, *args, **kwargs):
        self.app = app
        self._session = False
        self._set_cookies: list[str] = []
        super().__init__(*args, **kwargs)

    def version_string(self):
        return "KStudy"

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
        for key, value in security.SECURITY_HEADERS.items():
            self.send_header(key, value)
        if self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        elif not content_type.startswith("image/"):
            self.send_header("Cache-Control", "no-store")
        for cookie in self._set_cookies:
            self.send_header("Set-Cookie", cookie)
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, obj, headers: dict | None = None):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", headers)

    def _error(self, status: int, code: str, message: str, headers: dict | None = None, **extra):
        return self._json(status, {"error": code, "message": message, **extra}, headers)

    def _file(self, path: Path | None, content_type: str | None = None, headers: dict | None = None):
        if path is None or not path.is_file():
            return self._error(404, "not_found", "Arquivo não encontrado.")
        try:
            data = path.read_bytes()
        except OSError:
            return self._error(404, "not_found", "Arquivo não encontrado.")
        kind = content_type or CONTENT_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(str(path))[0] \
            or "application/octet-stream"
        self._send(200, data, kind, headers)

    def _read_raw(self, limit: int = MAX_BODY) -> bytes | None:
        """Lê o corpo da requisição. None se for grande demais (a resposta 413 já foi enviada)."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > limit:
            self._discard(min(max(length, 0), 20 * MAX_BODY))     # descarta o excesso para o cliente receber o 413
            self._error(413, "body_too_large", "Corpo da requisição grande demais.")
            return None
        return self.rfile.read(length) if length else b""

    def _discard(self, remaining: int) -> None:
        """Lê e joga fora até `remaining` bytes, esperando no máximo 2 s sem dados (cliente que mente no tamanho)."""
        self.connection.settimeout(2)
        try:
            while remaining > 0:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
        except OSError:
            pass
        finally:
            self.connection.settimeout(self.timeout)

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

    # ---- segurança de rede ----
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
        if self.app.lan and not self._client_ok():
            self._error(403, "forbidden_client", "Só computadores da rede local podem acessar.")
            return False
        raw = self.headers.get("Host") or ""
        host = raw.strip("[]").lower() if raw.endswith("]") else raw.rsplit(":", 1)[0].strip("[]").lower()
        if host in ("localhost", "127.0.0.1", "::1") or host in self.app.allowed_hosts:
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

    # ---- identidade, cookies e CSRF ----
    def _cookie_value(self, name: str) -> str | None:
        header = self.headers.get("Cookie")
        if not header:
            return None
        try:
            morsel = SimpleCookie(header).get(name)
        except Exception:
            return None
        return morsel.value if morsel else None

    def _token(self) -> str | None:
        return self._cookie_value(COOKIE)

    def _ip(self) -> str:
        return self.client_address[0]

    def _secure_flag(self) -> str:
        return "; Secure" if self.app.https else ""

    def _session_cookie(self, token: str, max_age: int = COOKIE_MAX_AGE) -> str:
        return f"{COOKIE}={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={max_age}{self._secure_flag()}"

    def _student(self, required: bool = True):
        if self._session is False:
            self._session = self.app.db.student_for_token(self._token())
        if self._session is None and required:
            self._error(401, "login_required", "Entre com seu e-mail e senha para continuar.")
        return self._session

    def _admin(self):
        """Aluno administrador, ou None (a resposta 401/403 já foi enviada)."""
        student = self._student()
        if student is None:
            return None
        if not student["is_admin"]:
            self._error(403, "forbidden", "Apenas administradores podem acessar.")
            return None
        return student

    def _pre_value(self) -> str | None:
        value = self._cookie_value(security.PRE_COOKIE)
        return value if value and re.fullmatch(r"[A-Za-z0-9_-]{20,100}", value) else None

    def _ensure_pre(self) -> str:
        """Token CSRF de pré-login; define o cookie `kstudy_pre` se o navegador ainda não tem."""
        value = self._pre_value()
        if value is None:
            value = secrets.token_urlsafe(24)
            self._set_cookies.append(f"{security.PRE_COOKIE}=%s; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400%s"
                                     % (value, self._secure_flag()))
        return security.pre_token(self.app.secret, value)

    def _csrf_token(self, student) -> str:
        return student["csrf_token"] if student else self._ensure_pre()

    def _csrf_ok(self, body: dict, beacon: bool) -> bool:
        sent = self.headers.get("X-CSRF-Token")
        if sent is None and beacon:
            sent = body.get("csrf")
        student = self._student(required=False)
        if student and security.tokens_equal(sent, student["csrf_token"]):
            return True
        pre = self._pre_value()
        if pre and security.tokens_equal(sent, security.pre_token(self.app.secret, pre)):
            return True
        self._error(403, "csrf_failed", "Falha na verificação de segurança (CSRF). Recarregue a página.")
        return False

    def _person(self, student) -> dict:
        return {"email": student["email"], "name": student["name"], "isAdmin": bool(student["is_admin"])}

    # ---- utilidades de trilha ----
    def _sync(self):
        indexer.sync(self.app.content_dir, self.app.db)

    def _need_trail(self, slug: str) -> bool:
        """A trilha precisa existir (e estar ativa, exceto para admin). Reindexa uma vez se faltar."""
        db = self.app.db
        if not SLUG.match(slug):
            self._error(404, "trail_not_found", "Trilha não encontrada.")
            return False
        if not db.trail_exists(slug):
            self._sync()
        if not db.trail_exists(slug):
            self._error(404, "trail_not_found", "Trilha não encontrada.")
            return False
        student = self._student(required=False)
        if not db.trail_active(slug) and not (student and student["is_admin"]):
            self._error(404, "trail_not_found", "Trilha não encontrada.")
            return False
        return True

    def _need_item(self, slug: str, block: str, item: str) -> bool:
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

    def _serve_asset(self, slug: str, relative: str | None, kinds: tuple):
        """Entrega um arquivo SOMENTE se ele estiver na lista permitida (assets) com um dos tipos esperados."""
        row = self.app.db.asset(slug, relative) if relative else None
        if row is None or row["kind"] not in kinds:
            return self._error(404, "not_found", "Arquivo não encontrado.")
        return self._file(inside(self.app.content_dir / slug, relative))

    # ---- despacho ----
    def _path_parts(self) -> list[str]:
        raw = urlparse(self.path).path
        return [unquote(part) for part in raw.split("/") if part]

    def _guard(self, method: str, fn):
        try:
            return fn()
        except (ConnectionError, TimeoutError):
            raise
        except Exception as exc:                    # nunca devolve traceback ao cliente
            print(f"erro interno ({method} {urlparse(self.path).path}): {type(exc).__name__}", file=sys.stderr)
            try:
                self._error(500, "internal_error", "Erro interno do servidor.")
            except OSError:
                pass

    def do_GET(self):
        self._guard("GET", self._get)

    do_HEAD = do_GET

    def _get(self):
        if not self._host_ok():
            return None
        raw_path = urlparse(self.path).path
        if "\x00" in unquote(raw_path):
            return self._error(400, "invalid_path", "Caminho inválido.")
        parts = self._path_parts()
        if parts[:1] == ["api"]:
            return self._api_get(parts[1:])
        if parts[:1] == ["admin"]:
            return self._admin_page(parts[1:])
        if parts[:2] == ["auth", "oauth"]:
            return self._oauth(parts[2:])
        name = "index.html" if not parts else "/".join(parts)
        if name.startswith("."):
            return self._error(404, "not_found", "Arquivo não encontrado.")
        return self._file(inside(WEB, name))

    # ---- entrada com o Google ----
    def _redirect_uri(self) -> str:
        """Endereço de retorno: fixo no sistema. O host já foi validado por _host_ok (localhost, --lan ou K_STUDY_ALLOWED_HOSTS)."""
        scheme = "https" if self.app.https else "http"
        return f"{scheme}://{self.headers.get('Host')}{oauth.CALLBACK_PATH}"

    def _oauth_cookie(self, value: str, max_age: int) -> str:
        # Lax (e não Strict): o Google devolve a pessoa por um redirecionamento vindo de outro site
        return f"{oauth.STATE_COOKIE}={value}; HttpOnly; SameSite=Lax; Path=/auth/oauth/; Max-Age={max_age}{self._secure_flag()}"

    def _oauth_back(self, error: str | None = None):
        self._set_cookies.append(self._oauth_cookie("", 0))
        return self._redirect("/" + (f"?oauth_error={error}" if error else ""))

    def _oauth(self, parts: list[str]):
        config = self.app.google
        if parts[:1] != ["google"] or parts[1:] not in (["start"], ["callback"]) or config is None:
            return self._error(404, "not_found", "Rota desconhecida.")
        if parts[1] == "start":
            flow = oauth.new_flow()
            self._set_cookies.append(self._oauth_cookie(oauth.sign_flow(flow, self.app.secret), oauth.STATE_SECONDS))
            return self._redirect(oauth.authorization_url(config["client_id"], self._redirect_uri(), flow))
        return self._oauth_callback(config)

    def _oauth_callback(self, config: dict):
        db, secret = self.app.db, self.app.secret
        query = parse_qs(urlparse(self.path).query)
        flow = oauth.read_flow(self._cookie_value(oauth.STATE_COOKIE), secret)
        state, code = (query.get("state") or [""])[0], (query.get("code") or [""])[0]
        if flow is None or not security.tokens_equal(state, flow["state"]):
            return self._oauth_back("invalid_state")
        if (query.get("error") or [""])[0]:
            return self._oauth_back("denied")
        if not code or len(code) > 2048:
            return self._oauth_back("failed")
        if security.retry_after(db, [(security.ip_key(secret, self._ip()), security.FAILS_PER_IP)]):
            return self._oauth_back("too_many")
        try:
            identity = oauth.exchange_code(config, code, self._redirect_uri(), flow)
        except oauth.OAuthError as exc:
            security.record_failure(db, security.ip_key(secret, self._ip()))
            db.audit(None, "login_oauth_failed", exc.code, self._ip())
            return self._oauth_back(exc.code)
        email = security.normalize_email(identity["email"])
        if email is None:
            return self._oauth_back("failed")
        name = security.normalize_name(identity["name"]) or security.normalize_name(email.split("@")[0]) or "Aluno"
        row = db.find_student(email)
        if row is None:
            try:
                student, first = db.create_student(email, name, oauth.UNUSABLE_HASH)
            except sqlite3.IntegrityError:
                row = db.find_student(email)
                student, first = {"id": row["id"]}, False
        else:
            student, first = {"id": row["id"]}, False
            if not row["password_hash"] or not row["name"]:           # conta antiga: o Google prova o e-mail; não fica reivindicável
                db.set_credentials(row["id"], row["name"] or name, row["password_hash"] or oauth.UNUSABLE_HASH)
        self._start_session(student["id"])
        db.audit(student["id"], "login_oauth", "primeiro administrador" if first else "google", self._ip())
        return self._oauth_back()

    def _redirect(self, location: str):
        self._send(302, b"", "text/plain; charset=utf-8", {"Location": location})

    def _admin_page(self, parts: list[str]):
        student = self._student(required=False)
        if student is None:                          # sem sessão: volta para a tela de entrada
            return self._redirect("/")
        if not student["is_admin"]:
            return self._error(403, "forbidden", "Apenas administradores podem acessar.")
        if not parts and not urlparse(self.path).path.endswith("/"):
            return self._redirect("/admin/")         # os caminhos relativos da página dependem da barra final
        name = "/".join(parts) or "index.html"
        return self._file(inside(ADMIN_WEB, name))

    def _api_get(self, parts: list[str]):
        db = self.app.db
        if parts == ["auth", "me"]:
            student = self._student(required=False)
            return self._json(200, {"student": self._person(student) if student else None,
                                    "csrfToken": self._csrf_token(student), "oauth": {"google": self.app.google is not None}})
        if parts[:1] == ["admin"]:
            return self._admin_get(parts[1:])
        if parts == ["trails"]:
            student = self._student()
            if student is None:
                return None
            self._sync()
            return self._json(200, db.list_trails(student["id"]))
        if len(parts) >= 2 and parts[0] == "trails":
            student = self._student()
            if student is None:
                return None
            slug, rest = parts[1], parts[2:]
            if not self._need_trail(slug):
                return None
            if not rest:
                return self._serve_trail_manifest(slug)
            if rest == ["cover"]:
                row = db.one("SELECT cover FROM trails WHERE slug=?", (slug,))
                return self._serve_asset(slug, row["cover"], ("cover",))
            if len(rest) == 2 and rest[0] == "figures":
                if not FIGURE.match(rest[1]):
                    return self._error(404, "not_found", "Arquivo não encontrado.")
                return self._serve_asset(slug, f"figures/{rest[1]}", ("figure",))
            if len(rest) == 2 and rest[0] == "blocks":
                if not ID.match(rest[1]):
                    return self._error(400, "invalid_id", "Identificador de bloco inválido.")
                row = db.one("SELECT file FROM blocks WHERE trail=? AND block_id=?", (slug, rest[1]))
                if row is None:
                    return self._error(404, "block_not_found", "Bloco não encontrado.")
                return self._serve_asset(slug, row["file"], ("block",))
            if len(rest) == 5 and rest[0] == "blocks" and rest[2] == "items" and rest[4] in ("content", "transcript"):
                if not self._need_item(slug, rest[1], rest[3]):
                    return None
                row = db.one("SELECT path, transcript FROM items WHERE trail=? AND block_id=? AND item_id=?",
                             (slug, rest[1], rest[3]))
                if rest[4] == "content":
                    return self._serve_asset(slug, row["path"], ("item",))
                return self._serve_asset(slug, row["transcript"], ("transcript",))
            if rest == ["progress"]:
                return self._json(200, db.progress_state(student["id"], slug))
        return self._error(404, "not_found", "Rota desconhecida.")

    def _serve_trail_manifest(self, slug: str):
        return self._file(inside(self.app.content_dir / slug, "trail.json"))

    def _admin_get(self, parts: list[str]):
        admin = self._admin()
        if admin is None:
            return None
        from .admin import queries
        db = self.app.db
        if parts == ["specs.zip"]:
            try:
                from . import packages
            except ImportError:
                return self._error(501, "not_available", "Download das specs ainda não disponível.")
            data = packages.build_specs_zip(self.app.specs)
            return self._send(200, data, "application/zip",
                              {"Content-Disposition": 'attachment; filename="k_study-specs.zip"'})
        with db.lock:
            if parts == ["overview"]:
                result = queries.overview(db.conn)
            elif parts == ["students"]:
                result = queries.students(db.conn)
            elif len(parts) == 2 and parts[0] == "students" and parts[1].isdigit():
                result = queries.student(db.conn, int(parts[1]))
            elif parts == ["trails"]:
                result = queries.trails(db.conn)
            elif len(parts) == 2 and parts[0] == "trails" and SLUG.match(parts[1]):
                result = queries.trail(db.conn, parts[1])
            else:
                return self._error(404, "not_found", "Rota desconhecida.")
        if result is None:
            return self._error(404, "not_found", "Não encontrado.")
        return self._json(200, result)

    # ---- escritas ----
    def do_POST(self):
        self._guard("POST", lambda: self._write("POST"))

    def do_PUT(self):
        self._guard("PUT", lambda: self._write("PUT"))

    def do_DELETE(self):
        self._guard("DELETE", lambda: self._write("DELETE"))

    def do_PATCH(self):
        self._guard("PATCH", self._not_allowed)

    def do_OPTIONS(self):                   # sem CORS: nenhuma origem de fora pode ler a API
        self._guard("OPTIONS", self._not_allowed)

    def _not_allowed(self):
        self._drain(MAX_BODY)
        return self._error(405, "method_not_allowed", "Método não permitido.", {"Allow": "GET, POST, PUT, DELETE"})

    def _write(self, method: str):
        parts = self._path_parts()
        is_import = method == "POST" and parts == ["api", "admin", "trails", "import"]
        raw = b""
        if not is_import:
            raw = self._read_raw()              # lê o corpo antes de qualquer resposta de erro
            if raw is None:
                return None
        if not self._host_ok() or not self._origin_ok():
            if is_import:
                self._drain()
            return None
        if parts[:1] != ["api"]:
            return self._error(404, "not_found", "Rota desconhecida.")
        parts = parts[1:]
        if is_import:
            return self._import_zip()
        if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
            return self._error(415, "unsupported_media_type", "Envie o corpo como application/json.")
        body = self._parse(raw)
        if body is None:
            return None
        if not self._csrf_ok(body, beacon=parts == ["track"]):
            return None
        if method == "POST":
            if parts[:1] == ["auth"] and len(parts) == 2:
                return self._auth(parts[1], body)
            if parts == ["track"]:
                return self._track(body)
            if len(parts) == 4 and parts[:2] == ["admin", "trails"] and parts[3] == "active":
                return self._set_active(parts[2], body)
        elif len(parts) >= 4 and parts[0] == "trails" and parts[2] == "progress":
            return self._progress(method, parts[1], parts[3], parts[4:], body)
        return self._error(404, "not_found", "Rota desconhecida.")

    # ---- autenticação ----
    def _blocked(self, email: str | None) -> bool:
        secret, ip = self.app.secret, self._ip()
        limits = [(security.ip_key(secret, ip), security.FAILS_PER_IP)]
        if email:
            limits.append((security.attempt_key(secret, email, ip), security.FAILS_PER_KEY))
        wait = security.retry_after(self.app.db, limits)
        if wait:
            self._error(429, "too_many_attempts", "Muitas tentativas. Aguarde alguns minutos e tente de novo.",
                        {"Retry-After": str(wait)})
            return True
        return False

    def _fail(self, email: str | None) -> None:
        keys = [security.ip_key(self.app.secret, self._ip())]
        if email:
            keys.append(security.attempt_key(self.app.secret, email, self._ip()))
        security.record_failure(self.app.db, *keys)

    def _start_session(self, student_id: int) -> str:
        token, csrf = secrets.token_urlsafe(32), security.new_csrf_token()
        self.app.db.create_session(student_id, token, csrf, self.headers.get("User-Agent", ""),
                                   replace_token=self._token())
        self._set_cookies.append(self._session_cookie(token))
        return csrf

    def _auth(self, action: str, body: dict):
        db, secret = self.app.db, self.app.secret
        if action == "logout":
            student = self._student(required=False)
            db.logout(self._token())
            if student:
                db.audit(student["id"], "logout", "", self._ip())
            self._set_cookies.append(self._session_cookie("", 0))
            return self._json(200, {"ok": True})
        if action not in ("check", "login", "register"):
            return self._error(404, "not_found", "Rota desconhecida.")
        email = security.normalize_email(body.get("email"))
        if email is None:
            return self._error(400, "invalid_email", "Informe um e-mail válido.")
        if self._blocked(email):
            return None
        row = db.find_student(email)
        if action == "check":
            return self._json(200, {"exists": row is not None, "firstUser": db.count_students() == 0,
                                    "needsSetup": bool(row is not None and not row["password_hash"])})
        if action == "login":
            password = body.get("password")
            password = password if isinstance(password, str) else ""
            if row is None or not row["password_hash"] or len(password) > security.MAX_PASSWORD:
                security.dummy_verify(password[:security.MAX_PASSWORD], secret)
                ok = False
            else:
                ok = security.verify_password(password, row["password_hash"], secret)
            if not ok:
                self._fail(email)
                db.audit(row["id"] if row else None, "login_failed", "", self._ip())
                return self._error(401, "invalid_credentials", "E-mail ou senha incorretos.")
            if security.needs_rehash(row["password_hash"]):
                db.set_credentials(row["id"], None, security.hash_password(password, secret))
            security.clear_failures(db, security.attempt_key(secret, email, self._ip()))
            csrf = self._start_session(row["id"])
            db.audit(row["id"], "login", "", self._ip())
            student = {"email": row["email"], "name": row["name"], "is_admin": row["is_admin"]}
            return self._json(200, {"student": self._person(student), "csrfToken": csrf})
        return self._register(body, email, row)

    def _register(self, body: dict, email: str, row):
        db, secret = self.app.db, self.app.secret
        if row is not None and row["password_hash"]:
            return self._error(409, "email_taken", "Este e-mail já tem cadastro. Entre com a senha.")
        flood = security.retry_after(db, [(security.registration_key(secret, self._ip()), security.REGISTRATIONS_PER_IP)])
        if flood:
            return self._error(429, "too_many_attempts", "Muitos cadastros deste endereço. Aguarde alguns minutos e tente de novo.",
                               {"Retry-After": str(flood)})
        name = security.normalize_name(body.get("name"))
        if name is None:
            return self._error(400, "invalid_name", "Informe seu nome (até 80 caracteres).")
        password = body.get("password")
        problem = security.check_password_policy(password, email)
        if problem:
            return self._error(400, "invalid_password", problem)
        if password != body.get("passwordConfirm"):
            return self._error(400, "password_mismatch", "A confirmação da senha não confere.")
        hashed = security.hash_password(password, secret)
        first = False
        if row is not None:                          # conta antiga (v1) sem senha: define senha e nome
            db.set_credentials(row["id"], name, hashed)
            student = {"id": row["id"], "email": email, "name": name, "is_admin": row["is_admin"]}
        else:
            try:
                student, first = db.create_student(email, name, hashed)
            except sqlite3.IntegrityError:
                return self._error(409, "email_taken", "Este e-mail já tem cadastro. Entre com a senha.")
        security.record_failure(db, security.registration_key(secret, self._ip()))        # conta cadastros por endereço
        csrf = self._start_session(student["id"])
        db.audit(student["id"], "register", "primeiro administrador" if first else "", self._ip())
        return self._json(200, {"student": self._person(student), "csrfToken": csrf, "isFirstAdmin": first})

    # ---- progresso e rastreio ----
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

    # ---- administração ----
    def _set_active(self, slug: str, body: dict):
        admin = self._admin()
        if admin is None:
            return None
        if not SLUG.match(slug) or not self.app.db.trail_exists(slug):
            self._sync()
            if not SLUG.match(slug) or not self.app.db.trail_exists(slug):
                return self._error(404, "trail_not_found", "Trilha não encontrada.")
        active = body.get("active")
        if not isinstance(active, bool):
            return self._error(400, "invalid_active", "O campo active deve ser verdadeiro ou falso.")
        self.app.db.set_trail_active(slug, active)
        self.app.db.audit(admin["id"], "trail_active", f"{slug}={'sim' if active else 'não'}", self._ip())
        return self._json(200, {"slug": slug, "active": active})

    def _drain(self, limit: int = MAX_ZIP) -> None:
        """Descarta o corpo ainda não lido, para o cliente conseguir receber a resposta de erro."""
        try:
            remaining = min(int(self.headers.get("Content-Length") or 0), limit)
        except ValueError:
            remaining = 0
        self._discard(remaining)

    def _import_zip(self):
        """Upload do pacote zip (somente admin, com CSRF). Autentica ANTES de ler o corpo."""
        student = self._student(required=False)
        failure = None
        if student is None:
            failure = (401, "login_required", "Entre com seu e-mail e senha para continuar.")
        elif not student["is_admin"]:
            failure = (403, "forbidden", "Apenas administradores podem acessar.")
        elif not security.tokens_equal(self.headers.get("X-CSRF-Token"), student["csrf_token"]):
            failure = (403, "csrf_failed", "Falha na verificação de segurança (CSRF). Recarregue a página.")
        elif (self.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/zip":
            failure = (415, "unsupported_media_type", "Envie o pacote como application/zip.")
        if failure:
            self._drain()
            return self._error(*failure)
        admin = student
        raw = self._read_raw(MAX_ZIP)
        if raw is None:
            return None
        try:
            from . import packages
        except ImportError:
            return self._error(501, "not_available", "A importação de pacotes ainda não está disponível.")
        query = parse_qs(urlparse(self.path).query)
        replace = (query.get("replace") or ["0"])[0] == "1"
        try:
            result = packages.import_trail_zip(self.app.content_dir, raw, replace=replace)
        except packages.PackageError as exc:
            self.app.db.audit(admin["id"], "import_failed", "; ".join(exc.problems)[:300], self._ip())
            return self._error(400, "invalid_package", "O pacote foi recusado.", problems=list(exc.problems))
        indexer.sync(self.app.content_dir, self.app.db, force=True)
        self.app.db.audit(admin["id"], "import_trail", f"{result.get('slug')} replace={replace}", self._ip())
        return self._json(200, {"slug": result.get("slug"), "warnings": result.get("warnings", []),
                                "replaced": bool(result.get("replaced"))})

    def log_message(self, fmt, *args):
        pass


def make_server(content_dir, db, port: int = 8765, host: str = "127.0.0.1", lan: bool = False,
                env_path=None, secret: str | None = None, specs=None) -> ThreadingHTTPServer:
    """Cria o servidor (sem iniciá-lo). `db` é um Database ou o caminho do arquivo; indexa o conteúdo antes.
    O segredo vem de `secret`, do .env (`env_path`, criado se faltar) ou, em testes, de um valor temporário."""
    if not isinstance(db, Database):
        db = Database(db)
    if secret is None:
        if env_path is None:
            secret = secrets.token_hex(32)           # sem .env informado (testes): segredo só desta execução
        else:
            secret = security.ensure_secret(Path(env_path))
    app = App(Path(content_dir), db, lan, secret, os.environ.get("K_STUDY_HTTPS") == "1", specs)
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


def serve(content_dir, db_path, port: int = 8765, lan: bool = False, env_path=".env", host: str = "127.0.0.1") -> None:
    """Sobe o servidor e imprime os endereços (em português)."""
    server = make_server(content_dir, db_path, port, host=host, lan=lan, env_path=env_path)
    trails = server.app.db.query("SELECT slug FROM trails ORDER BY slug")
    print(f"Conteúdo : {Path(content_dir).resolve()}  ({len(trails)} trilha(s))\n"
          f"Banco    : {Path(db_path).resolve()}\n"
          f"Segredo  : {Path(env_path).resolve()}  (faça backup junto com o banco; nunca o envie ao git)\n"
          f"Abra     : http://localhost:{port}/")
    if lan:
        address = lan_address()
        print(f"Rede local: http://{address or '<ip-deste-computador>'}:{port}/   (só redes privadas; o acesso "
              "exige e-mail e senha)")
    print("Google   : " + ("entrada com o Google ATIVA (retorno: /auth/oauth/google/callback)" if server.app.google
                           else "desativada (GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET vazias no .env)"))
    if server.app.db.count_students() == 0:
        print("Nenhuma conta ainda: o primeiro cadastro feito na interface vira administrador.")
    def stop(signum, frame):                 # docker stop envia SIGTERM: encerra limpo em vez de esperar o SIGKILL
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGTERM, stop)
    except (ValueError, OSError):            # fora da thread principal
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()
