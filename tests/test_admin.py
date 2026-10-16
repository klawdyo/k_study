"""Testes das consultas do painel do admin, contra um banco temporário criado com o DDL EXATO do contrato (seção 4).

As rotas HTTP /api/admin/* e as páginas ficam em tests/test_server.py (acesso) e na verificação no navegador.
"""
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from k_study.admin import queries

DDL = """
PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
CREATE TABLE meta      (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE trails    (slug TEXT PRIMARY KEY, title TEXT, description TEXT, language TEXT, level TEXT, tags TEXT,
                        cover TEXT, active INTEGER NOT NULL DEFAULT 1, manifest_mtime REAL, synced_at TEXT);
CREATE TABLE blocks    (trail TEXT, block_id TEXT, title TEXT, position INTEGER, file TEXT, PRIMARY KEY (trail, block_id));
CREATE TABLE items     (trail TEXT, block_id TEXT, item_id TEXT, section TEXT, position INTEGER, type TEXT, title TEXT,
                        path TEXT, transcript TEXT, optional INTEGER DEFAULT 0, minutes REAL,
                        PRIMARY KEY (trail, block_id, item_id));
CREATE TABLE assets    (trail TEXT, path TEXT, kind TEXT, size INTEGER, PRIMARY KEY (trail, path));
CREATE TABLE students  (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
                        password_hash TEXT NOT NULL, is_admin INTEGER NOT NULL DEFAULT 0, created_at TEXT, last_seen_at TEXT);
CREATE TABLE sessions  (token_hash TEXT PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                        csrf_token TEXT NOT NULL, created_at TEXT, last_seen_at TEXT, expires_at TEXT, user_agent TEXT);
CREATE TABLE login_attempts (key TEXT NOT NULL, at TEXT NOT NULL);
CREATE TABLE audit_log (id INTEGER PRIMARY KEY, at TEXT, student_id INTEGER, action TEXT, detail TEXT, ip TEXT);
CREATE TABLE progress  (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, done INTEGER, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
CREATE TABLE answers   (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, question_id TEXT, chosen TEXT,
                        correct INTEGER, at TEXT, PRIMARY KEY (student_id, trail, block_id, item_id, question_id));
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
    conn.executemany("INSERT INTO trails(slug, title, description, cover, active) VALUES (?,?,?,?,?)",
                     [("am", "Aprendizado de Máquina", "Prova de AM", "capa.png", 1), ("py", "Python", "", None, 0)])
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
    conn.executemany("INSERT INTO students(id, email, name, password_hash, is_admin, created_at, last_seen_at) "
                     "VALUES (?,?,?,?,?,?,?)", [
        (1, "ana@exemplo.com", "Ana Souza", "x", 1, iso(20), iso(1)),
        (2, "bia@exemplo.com", "Bia Lima", "x", 0, iso(10), iso(9)),
        (3, "caio@exemplo.com", "", "", 0, iso(2), None)])            # conta antiga sem nome nem senha
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


def test_nome_e_email_em_todas_as_respostas(db):
    conn = conn_of(db)
    rows = {s["email"]: s for s in queries.students(conn)["students"]}
    assert rows["ana@exemplo.com"]["name"] == "Ana Souza" and rows["caio@exemplo.com"]["name"] == ""
    assert queries.student(conn, 1)["student"]["name"] == "Ana Souza"
    recent = queries.overview(conn, NOW)["recent"]
    assert recent and all("name" in e and e["email"] for e in recent)
    assert {e["name"] for e in recent} >= {"Ana Souza"}


def test_trilhas_trazem_capa_e_active(db):
    listing = {t["slug"]: t for t in queries.trails(conn_of(db), NOW)["trails"]}
    assert listing["am"]["active"] is True and listing["am"]["cover"] == "/api/trails/am/cover"
    assert listing["py"]["active"] is False and listing["py"]["cover"] is None       # desativada continua listada
    assert queries.trail(conn_of(db), "py", NOW)["trail"]["active"] is False

