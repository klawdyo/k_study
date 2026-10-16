import http.client
import json
import threading
from http.cookies import SimpleCookie

import pytest

from k_study import security
from k_study.db import Database
from k_study.server import make_server

PASSWORD = "senha-segura-1"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Nunca usar o conteúdo, o banco ou o segredo reais da máquina; scrypt barato só nos testes."""
    for name in ("K_STUDY_CONTENT", "K_STUDY_DB", "K_STUDY_ENV", "K_STUDY_SECRET", "K_STUDY_HTTPS",
                 "K_STUDY_SPECS_ROOT", "K_STUDY_ALLOWED_HOSTS", "K_STUDY_HOST", "GOOGLE_CLIENT_ID",
                 "GOOGLE_CLIENT_SECRET"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(security, "SCRYPT_N", 2 ** 10)


def write_json(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")


def make_trail(content, slug="demo", title="Demo"):
    """Cria content/<slug>/ com um bloco: uma leitura (r), um vídeo com transcrição (v) e uma lista de questões (q)."""
    folder = content / slug
    write_json(folder / "trail.json", {
        "schema": "trail/v1", "id": slug, "title": title, "description": "Trilha de teste", "language": "pt-BR",
        "level": "iniciante", "tags": ["teste"], "blocks": [{"id": "block-1", "title": "B", "file": "block-1/block.json"}]})
    (folder / "block-1").mkdir(exist_ok=True)
    (folder / "transcripts").mkdir(exist_ok=True)
    (folder / "block-1" / "read.md").write_text("# Olá\n" + "palavra " * 360, encoding="utf-8")
    write_json(folder / "transcripts" / "aaaaaaaaaaa.json",
               {"lang": "pt", "generated": True, "duration": 10, "source": "test", "segments": [[0, "oi"]]})
    write_json(folder / "block-1" / "q.json", {
        "schema": "questions/v2", "id": "q", "title": "Q",
        "questions": [{"id": "q01", "type": "single", "prompt": "2+2?", "generalExplanation": "g",
                       "options": [{"id": "a", "text": "4", "correct": True, "explanation": "sim"},
                                   {"id": "b", "text": "5", "correct": False, "explanation": "não"}]}]})
    write_json(folder / "block-1" / "block.json", {
        "schema": "block/v2", "id": "block-1", "title": "B", "description": "",
        "sections": [{"id": "s", "title": "S", "items": [
            {"id": "r", "type": "markdown", "title": "R", "path": "read.md"},
            {"id": "v", "type": "video", "title": "V", "url": "https://www.youtube.com/watch?v=aaaaaaaaaaa",
             "transcript": "../transcripts/aaaaaaaaaaa.json", "clips": [{"start": 0, "end": 90}], "optional": True},
            {"id": "q", "type": "questions", "title": "Q", "path": "q.json"}]}]})
    return folder


@pytest.fixture()
def content(tmp_path):
    """Pasta content/ temporária com a trilha `demo`."""
    root = tmp_path / "content"
    make_trail(root)
    return root


@pytest.fixture()
def trail_dir(content):
    return content / "demo"


@pytest.fixture()
def db(tmp_path):
    database = Database(tmp_path / "data" / "k_study.db")
    yield database
    database.close()


class Browser:
    """Cliente HTTP com cookies próprios (um 'navegador') que guarda e envia o token CSRF."""

    def __init__(self, port):
        self.port, self.cookies, self.csrf = port, {}, None

    @property
    def cookie(self):
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items()) or None

    def raw(self, method, path, body=None, headers=None, host=None, csrf=True):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        payload = body if isinstance(body, (bytes, str)) else (json.dumps(body) if body is not None else None)
        send = {"Content-Type": "application/json", **(headers or {})}
        if host:
            send["Host"] = host
        if self.cookie:
            send["Cookie"] = self.cookie
        if csrf and method not in ("GET", "HEAD") and self.csrf and "X-CSRF-Token" not in send:
            send["X-CSRF-Token"] = self.csrf
        conn.request(method, path, payload, send)
        response = conn.getresponse()
        data = response.read()
        for key, value in response.getheaders():
            if key.lower() == "set-cookie":
                jar = SimpleCookie(value)
                for name, morsel in jar.items():
                    if morsel.value:
                        self.cookies[name] = morsel.value
                    else:
                        self.cookies.pop(name, None)
        out = response.status, data, dict(response.getheaders())
        conn.close()
        return out

    def call(self, method, path, body=None, **kw):
        """Devolve (status, JSON ou bytes)."""
        status, data, headers = self.raw(method, path, body, **kw)
        if headers.get("Content-Type", "").startswith("application/json"):
            return status, json.loads(data)
        return status, data

    def me(self):
        """GET /api/auth/me e guarda o token CSRF devolvido."""
        status, body = self.call("GET", "/api/auth/me")
        self.csrf = body["csrfToken"]
        return body

    def register(self, email="ana@exemplo.com", name="Ana", password=PASSWORD):
        self.me()
        status, body = self.call("POST", "/api/auth/register", {
            "email": email, "name": name, "password": password, "passwordConfirm": password})
        if status == 200:
            self.csrf = body["csrfToken"]
        return status, body

    def login(self, email="ana@exemplo.com", password=PASSWORD):
        self.me()
        status, body = self.call("POST", "/api/auth/login", {"email": email, "password": password})
        if status == 200:
            self.csrf = body["csrfToken"]
        return status, body


def start(server):
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    return server.server_address[1]


@pytest.fixture()
def server(content, db):
    srv = make_server(content, db, port=0)
    start(srv)
    yield srv
    srv.shutdown()
    srv.server_close()


@pytest.fixture()
def browser(server):
    """Um navegador anônimo."""
    return Browser(server.server_address[1])


@pytest.fixture()
def make_browser(server):
    return lambda: Browser(server.server_address[1])


@pytest.fixture()
def admin(make_browser):
    """O primeiro cadastro: administrador (admin@exemplo.com)."""
    b = make_browser()
    assert b.register("admin@exemplo.com", "Admin")[1]["isFirstAdmin"] is True
    return b


@pytest.fixture()
def student(make_browser, admin):
    """Um navegador logado como ana@exemplo.com (aluna comum; o admin já existe)."""
    b = make_browser()
    assert b.register("ana@exemplo.com", "Ana")[0] == 200
    return b
