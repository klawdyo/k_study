"""Testes do painel do admin: consultas SQL e rotas HTTP, com banco temporário criado com o DDL do contrato."""
import http.client
import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

import pytest

from k_study.admin import queries, server as admin_server

DDL = """
PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
CREATE TABLE meta      (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE trails    (slug TEXT PRIMARY KEY, title TEXT, description TEXT, language TEXT, level TEXT,
                        tags TEXT, manifest_mtime REAL, synced_at TEXT);
CREATE TABLE blocks    (trail TEXT, block_id TEXT, title TEXT, position INTEGER, file TEXT,
                        PRIMARY KEY (trail, block_id));
CREATE TABLE items     (trail TEXT, block_id TEXT, item_id TEXT, section TEXT, position INTEGER, type TEXT,
                        title TEXT, path TEXT, optional INTEGER DEFAULT 0, minutes REAL,
                        PRIMARY KEY (trail, block_id, item_id));
CREATE TABLE students  (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, created_at TEXT, last_seen_at TEXT);
CREATE TABLE sessions  (token_hash TEXT PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id),
                        created_at TEXT, last_seen_at TEXT, user_agent TEXT);
CREATE TABLE progress  (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, done INTEGER, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
CREATE TABLE answers   (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, question_id TEXT,
                        chosen TEXT, correct INTEGER, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id, question_id));
CREATE TABLE notes     (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, text TEXT, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
CREATE TABLE visits    (id INTEGER PRIMARY KEY, student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT,
                        started_at TEXT, seconds INTEGER DEFAULT 0, last_beat_at TEXT);
CREATE INDEX visits_student ON visits(student_id, trail); CREATE INDEX visits_item ON visits(trail, block_id, item_id);
"""

NOW = datetime(2026, 10, 16, 12, 0, 0, tzinfo=timezone.utc)


def iso(days_ago=0, hour=10):
    d = (NOW - timedelta(days=days_ago)).replace(hour=hour, minute=0, second=0)
    return d.isoformat(timespec="seconds")


def make_db(path, populate=True):
    conn = sqlite3.connect(path)
    conn.executescript(DDL)
    if populate:
        fill(conn)
    conn.commit()
    conn.close()


def fill(conn):
    conn.executemany("INSERT INTO trails(slug, title, description) VALUES (?,?,?)",
                     [("am", "Aprendizado de Máquina", "Prova de AM"), ("py", "Python", "")])
    conn.executemany("INSERT INTO blocks VALUES ('am',?,?,?,?)", [("b1", "Bloco 1", 1, "b1/block.json"),
                                                                  ("b2", "Bloco 2", 2, "b2/block.json")])
    conn.executemany("INSERT INTO items(trail, block_id, item_id, section, position, type, title, optional) "
                     "VALUES (?,?,?,?,?,?,?,?)", [
        ("am", "b1", "v1", "Aula 1", 1, "video", "Vídeo 1", 0),
        ("am", "b1", "r1", "Aula 1", 2, "markdown", "Leitura 1", 0),
        ("am", "b1", "q1", "Aula 1", 3, "questions", "Questões 1", 0),
        ("am", "b2", "v2", "Aula 2", 1, "video", "Vídeo 2", 0),
        ("am", "b2", "v3", "Aula 2", 2, "video", "Vídeo extra", 1),
        ("py", "p1", "x1", "Intro", 1, "markdown", "Intro", 0)])
    conn.execute("INSERT INTO blocks VALUES ('py','p1','Bloco P',1,'p1/block.json')")
    conn.executemany("INSERT INTO students VALUES (?,?,?,?)", [
        (1, "ana@exemplo.com", iso(20), iso(1)),
        (2, "bia@exemplo.com", iso(10), iso(9)),
        (3, "caio@exemplo.com", iso(2), None)])
    # visitas: (aluno, trilha, bloco, item, dias atrás, segundos)
    visits = [(1, "am", "b1", "v1", 1, 600), (1, "am", "b1", "v1", 1, 5), (1, "am", "b1", "r1", 1, 300),
              (1, "am", "b1", "q1", 0, 200), (1, "am", "b2", "v2", 0, 120),
              (2, "am", "b1", "v1", 9, 8), (2, "am", "b1", "v1", 9, 3), (2, "am", "b1", "r1", 10, 4),
              (3, "am", "b1", "v1", 2, 2), (3, "py", "p1", "x1", 2, 60)]
    for i, (sid, t, b, it, d, s) in enumerate(visits, 1):
        conn.execute("INSERT INTO visits VALUES (?,?,?,?,?,?,?,?)", (i, sid, t, b, it, iso(d), s, iso(d)))
    conn.executemany("INSERT INTO progress VALUES (?,?,?,?,?,?)", [
        (1, "am", "b1", "v1", 1, iso(1)), (1, "am", "b1", "r1", 1, iso(1)), (1, "am", "b1", "q1", 1, iso(0)),
        (1, "am", "b2", "v3", 1, iso(0)),            # opcional
        (2, "am", "b1", "v1", 1, iso(9)), (2, "am", "b1", "r1", 0, iso(9)),
        (1, "am", "b9", "removido", 1, iso(0))])      # item que não está mais no conteúdo: não conta
    conn.executemany("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?)", [
        (1, "am", "b1", "q1", "q01", '["a"]', 1, iso(0)), (1, "am", "b1", "q1", "q02", '["b","c"]', 0, iso(0)),
        (2, "am", "b1", "q1", "q01", '["a"]', 1, iso(9)), (2, "am", "b1", "q1", "q02", '["d"]', 0, iso(9)),
        (3, "am", "b1", "q1", "q02", '["d"]', 0, iso(2))])


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "k_study.db"
    make_db(path)
    return path


def conn_of(path):
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------- consultas ----------------------------------

def test_overview_totals_and_daily(db):
    data = queries.overview(conn_of(db), NOW)
    t = data["totals"]
    assert t["students"] == 3 and t["trails"] == 2
    assert t["seconds"] == 600 + 5 + 300 + 200 + 120 + 8 + 3 + 4 + 2 + 60
    assert t["visits"] == 10 and t["quick_visits"] == 5      # 5, 3, 4, 2 e 8 (< 10)
    assert t["active_7d"] == 2                               # ana (visitas) e caio (visita há 2 dias)
    assert t["answers"] == 5 and t["accuracy"] == 0.4
    assert len(data["daily"]) == 30 and data["daily"][-1]["date"] == "2026-10-16"
    last = data["daily"][-1]
    assert last["seconds"] == 320 and last["active_students"] == 1 and last["visits"] == 2
    assert data["daily"][-2]["date"] == "2026-10-15"


def test_overview_hardest_and_abandoned(db):
    data = queries.overview(conn_of(db), NOW)
    q = data["hardest_questions"]
    assert q[0]["question_id"] == "q02" and q[0]["answers"] == 3 and q[0]["wrong"] == 3 and q[0]["error_rate"] == 1.0
    assert all(x["question_id"] != "q01" for x in q)         # q01 sem erros não entra
    ab = data["abandoned_items"]
    assert ab and ab[0]["item_id"] == "v1" and ab[0]["visits"] == 5 and ab[0]["quick_visits"] == 4
    assert data["recent"][0]["at"] >= data["recent"][-1]["at"]


def test_overview_trails_completion(db):
    trails = {t["slug"]: t for t in queries.overview(conn_of(db), NOW)["trails"]}
    # am: obrigatórios = v1, r1, q1, v2 (4). ana fez 3, bia fez 1, caio só visitou e teve respostas: 0
    assert trails["am"]["students"] == 3
    assert trails["am"]["avg_completion"] == pytest.approx((0.75 + 0.25 + 0.0) / 3, abs=1e-3)
    assert trails["py"]["students"] == 1 and trails["py"]["avg_completion"] == 0.0


def test_students_list(db):
    rows = {s["email"]: s for s in queries.students(conn_of(db))["students"]}
    ana = rows["ana@exemplo.com"]
    assert ana["seconds"] == 1225 and ana["visits"] == 5 and ana["quick_visits"] == 1
    assert ana["items_done"] == 4 and ana["required_done"] == 3          # o item removido não conta
    assert ana["answers"] == 2 and ana["correct"] == 1 and ana["accuracy"] == 0.5
    assert ana["last_activity"] == iso(0)
    assert rows["caio@exemplo.com"]["last_activity"] == iso(2)           # sem last_seen_at: usa a visita


def test_student_detail(db):
    data = queries.student(conn_of(db), 1)
    assert data["student"]["email"] == "ana@exemplo.com"
    assert [t["slug"] for t in data["trails"]] == ["am"]
    am = data["trails"][0]
    assert am["required_items"] == 4 and am["required_done"] == 3 and am["completion"] == 0.75
    items = {i["item_id"]: i for i in am["items"]}
    assert items["v1"]["seconds"] == 605 and items["v1"]["visits"] == 2 and items["v1"]["quick_visits"] == 1
    assert items["v3"]["done"] and items["v3"]["optional"] and items["v3"]["visits"] == 0
    assert [q["question_id"] for q in items["q1"]["questions"]] == ["q01", "q02"]
    assert items["q1"]["questions"][1]["chosen"] == ["b", "c"] and items["q1"]["questions"][1]["correct"] is False
    assert queries.student(conn_of(db), 999) is None


def test_trails_list_and_detail(db):
    listing = {t["slug"]: t for t in queries.trails(conn_of(db), NOW)["trails"]}
    am = listing["am"]
    assert am["blocks"] == 2 and am["items"] == 5 and am["required_items"] == 4
    assert am["students"] == 3 and am["active_7d"] == 2 and am["visits"] == 9
    assert am["avg_seconds"] == round(am["seconds"] / 3)
    data = queries.trail(conn_of(db), "am", NOW)
    assert [b["block_id"] for b in data["blocks"]] == ["b1", "b2"]
    b1 = data["blocks"][0]
    v1 = b1["sections"][0]["items"][0]
    assert b1["sections"][0]["title"] == "Aula 1" and v1["item_id"] == "v1"
    assert v1["students_opened"] == 3 and v1["visits"] == 5 and v1["quick_visits"] == 4
    assert v1["abandon_rate"] == 0.8 and v1["done"] == 2 and v1["completion"] == pytest.approx(2 / 3, abs=1e-3)
    assert v1["avg_seconds"] == round(618 / 3)
    q1 = b1["sections"][0]["items"][2]
    assert q1["answers"] == 5 and q1["accuracy"] == 0.4
    assert data["hardest_questions"][0]["question_id"] == "q02"
    assert queries.trail(conn_of(db), "nao-existe", NOW) is None


def test_empty_database(tmp_path):
    path = tmp_path / "vazio.db"
    make_db(path, populate=False)
    conn = conn_of(path)
    data = queries.overview(conn, NOW)
    assert data["totals"]["students"] == 0 and data["totals"]["accuracy"] is None
    assert len(data["daily"]) == 30 and all(d["seconds"] == 0 for d in data["daily"])
    assert data["trails"] == [] and data["recent"] == [] and data["hardest_questions"] == []
    assert queries.students(conn) == {"students": []}
    assert queries.trails(conn, NOW) == {"trails": []}


def test_trail_without_students(tmp_path):
    path = tmp_path / "t.db"
    make_db(path, populate=False)
    conn = sqlite3.connect(path)
    conn.execute("INSERT INTO trails(slug, title) VALUES ('novo','Novo')")
    conn.execute("INSERT INTO blocks VALUES ('novo','b1','B',1,'x')")
    conn.execute("INSERT INTO items(trail, block_id, item_id, section, position, type, title) VALUES ('novo','b1','i','S',1,'video','V')")
    conn.commit()
    conn.close()
    data = queries.trail(conn_of(path), "novo", NOW)
    assert data["trail"]["students"] == 0 and data["trail"]["avg_completion"] is None
    item = data["blocks"][0]["sections"][0]["items"][0]
    assert item["completion"] is None and item["abandon_rate"] is None and item["avg_seconds"] == 0


# ---------------------------------------------------------------- HTTP ---------------------------------------

class Client:
    def __init__(self, srv):
        self.port = srv.server_address[1]

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        h = dict(headers or {})
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        conn.request(method, path, data, h)
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = raw
        return resp.status, payload, resp


def start(db, **kwargs):
    srv = admin_server.make_server(db, port=0, **kwargs)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, Client(srv)


@pytest.fixture
def panel(db):
    srv, client = start(db)
    yield client
    srv.shutdown()
    srv.server_close()


def test_routes(panel):
    status, data, _ = panel.request("GET", "/api/admin/overview")
    assert status == 200 and data["totals"]["students"] == 3
    assert panel.request("GET", "/api/admin/students")[1]["students"][0]["email"]
    assert panel.request("GET", "/api/admin/students/1")[1]["student"]["id"] == 1
    assert panel.request("GET", "/api/admin/students/999")[0] == 404
    assert panel.request("GET", "/api/admin/students/abc")[0] == 404
    assert len(panel.request("GET", "/api/admin/trails")[1]["trails"]) == 2
    assert panel.request("GET", "/api/admin/trails/am")[1]["trail"]["slug"] == "am"
    assert panel.request("GET", "/api/admin/trails/xxx")[0] == 404
    assert panel.request("GET", "/api/admin/nada")[0] == 404
    status, data, resp = panel.request("GET", "/api/admin/session")
    assert data == {"required": False, "authenticated": True}
    assert resp.getheader("Cache-Control") == "no-store"


def test_static_files(panel):
    status, body, resp = panel.request("GET", "/")
    assert status == 200 and b"<html" in body.lower() and "text/html" in resp.getheader("Content-Type")
    assert panel.request("GET", "/app.js")[0] == 200
    assert panel.request("GET", "/style.css")[0] == 200
    assert panel.request("GET", "/..%2f..%2fserver.py")[0] == 404
    assert panel.request("GET", "/%2e%2e/server.py")[0] == 404


def test_read_only_database(db, panel):
    # o painel nunca escreve: uma tentativa direta pela mesma forma de conexão falha
    with pytest.raises(sqlite3.OperationalError):
        conn_of(db).execute("DELETE FROM students")
    assert panel.request("POST", "/api/admin/students", {})[0] == 404
    assert panel.request("PUT", "/api/admin/students/1", {})[0] == 405
    assert panel.request("DELETE", "/api/admin/students/1")[0] == 405


def test_missing_database(tmp_path):
    srv, client = start(tmp_path / "nao-existe.db")
    try:
        status, data, _ = client.request("GET", "/api/admin/overview")
        assert status == 503 and data["error"] == "database_missing" and "banco" in data["message"]
        assert client.request("GET", "/")[0] == 200            # a interface carrega e mostra o aviso
    finally:
        srv.shutdown()
        srv.server_close()


def test_database_without_tables(tmp_path):
    path = tmp_path / "x.db"
    sqlite3.connect(path).close()
    srv, client = start(path)
    try:
        status, data, _ = client.request("GET", "/api/admin/overview")
        assert status == 503 and data["error"] == "database_error"
    finally:
        srv.shutdown()
        srv.server_close()


def test_invalid_host_rejected(panel):
    status, data, _ = panel.request("GET", "/api/admin/overview", headers={"Host": "evil.example.com"})
    assert status == 403 and data["error"] == "forbidden_host"
    assert panel.request("GET", "/api/admin/overview", headers={"Host": "192.168.1.5:8766"})[0] == 403   # sem --lan
    assert panel.request("GET", "/", headers={"Host": "evil.example.com:8766"})[0] == 403
    assert panel.request("GET", "/api/admin/overview", headers={"Host": "localhost:8766"})[0] == 200
    assert panel.request("GET", "/api/admin/overview", headers={"Host": "[::1]:8766"})[0] == 200


def test_lan_requires_password(db):
    with pytest.raises(ValueError, match="senha"):
        admin_server.make_server(db, port=0, lan=True, password=None)
    with pytest.raises(ValueError):
        admin_server.run(db, port=0, lan=True, password="")


def test_lan_login_flow(db):
    srv, client = start(db, lan=True, password="segredo")
    try:
        assert client.request("GET", "/api/admin/session")[1] == {"required": True, "authenticated": False}
        status, data, _ = client.request("GET", "/api/admin/overview")
        assert status == 401 and data["error"] == "login_required"
        assert client.request("GET", "/")[0] == 200                          # a tela de login é servida
        status, data, _ = client.request("POST", "/api/admin/login", {"password": "errada"})
        assert status == 401 and data["error"] == "invalid_password"
        status, _, resp = client.request("POST", "/api/admin/login", {"password": "segredo"})
        assert status == 200
        cookie = resp.getheader("Set-Cookie")
        assert cookie.startswith("kstudy_admin_sid=") and "HttpOnly" in cookie and "SameSite=Strict" in cookie
        token = cookie.split(";")[0]
        status, data, _ = client.request("GET", "/api/admin/overview", headers={"Cookie": token, "Host": "192.168.0.10:8766"})
        assert status == 200 and data["totals"]["students"] == 3             # Host por IP aceito em --lan
        assert client.request("GET", "/api/admin/overview", headers={"Cookie": "kstudy_sid=" + token.split("=")[1]})[0] == 401
        assert client.request("GET", "/api/admin/overview", headers={"Cookie": token, "Host": "evil.example.com"})[0] == 403
        client.request("POST", "/api/admin/logout", {}, {"Cookie": token})
        assert client.request("GET", "/api/admin/overview", headers={"Cookie": token})[0] == 401
    finally:
        srv.shutdown()
        srv.server_close()


def test_lan_brute_force_blocked(db):
    srv, client = start(db, lan=True, password="segredo")
    try:
        for _ in range(admin_server.MAX_FAILURES):
            assert client.request("POST", "/api/admin/login", {"password": "x"})[0] == 401
        status, data, _ = client.request("POST", "/api/admin/login", {"password": "segredo"})
        assert status == 429 and data["error"] == "too_many_attempts"
    finally:
        srv.shutdown()
        srv.server_close()


def test_client_outside_private_network_refused(db, monkeypatch):
    srv, client = start(db, lan=True, password="segredo")
    try:
        monkeypatch.setattr(admin_server.Handler, "_client_ip",
                            lambda self: __import__("ipaddress").ip_address("8.8.8.8"))
        status, data, _ = client.request("GET", "/api/admin/session")
        assert status == 403 and data["error"] == "forbidden_client"
        assert client.request("POST", "/api/admin/login", {"password": "segredo"})[0] == 403
    finally:
        srv.shutdown()
        srv.server_close()
