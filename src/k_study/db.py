"""Banco de dados SQLite do k_study (modo WAL): esquema, migrações e consultas.

O banco guarda ESTADO (índice do conteúdo, alunos, sessões, progresso, visitas). O corpo das aulas fica em arquivos.
Uma única conexão compartilhada entre as threads do servidor, protegida por um lock reentrante: simples e seguro
(o volume de escrita é pequeno). O esquema segue exatamente docs/arquitetura.md, seção 4.
"""
import hashlib
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from datetime import timedelta
from pathlib import Path

from . import security

MAX_BEAT_SECONDS = 30            # limite por chamada de beat/leave
MAX_VISIT_SECONDS = 4 * 3600     # teto de uma visita
SESSION_SLIDING_DAYS, SESSION_ABSOLUTE_DAYS = 30, 90


def now() -> str:
    """Data/hora atual em ISO 8601 UTC."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_email(text) -> str | None:
    """Normaliza (strip + minúsculas) e valida de forma simples. Devolve None se inválido."""
    return security.normalize_email(text)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ---- esquema e migrações -------------------------------------------------------------------------------------------

def _migration_1(conn: sqlite3.Connection) -> None:
    script = """
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
    CREATE INDEX visits_student ON visits(student_id, trail);
    CREATE INDEX visits_item ON visits(trail, block_id, item_id);
    """
    for statement in script.split(";"):      # executescript faria COMMIT implícito dentro da transação
        if statement.strip():
            conn.execute(statement)


def _migration_2(conn: sqlite3.Connection) -> None:
    """v1 -> v2: senhas, nome, admin, sessões com CSRF e validade, capa/ativa, assets, auditoria, tentativas."""
    statements = [
        "ALTER TABLE students ADD COLUMN name TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE students ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE students ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE trails ADD COLUMN cover TEXT",
        "ALTER TABLE trails ADD COLUMN active INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE items ADD COLUMN transcript TEXT",
        "DROP TABLE sessions",       # sessões antigas não têm CSRF nem validade: todos entram de novo
        """CREATE TABLE sessions (token_hash TEXT PRIMARY KEY,
                                  student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                                  csrf_token TEXT NOT NULL, created_at TEXT, last_seen_at TEXT, expires_at TEXT,
                                  user_agent TEXT)""",
        "UPDATE trails SET manifest_mtime=0",      # força a reindexação (capa, assets, transcrições)
        "CREATE TABLE assets (trail TEXT, path TEXT, kind TEXT, size INTEGER, PRIMARY KEY (trail, path))",
        "CREATE TABLE login_attempts (key TEXT NOT NULL, at TEXT NOT NULL)",
        "CREATE INDEX login_attempts_key ON login_attempts(key, at)",
        "CREATE TABLE audit_log (id INTEGER PRIMARY KEY, at TEXT, student_id INTEGER, action TEXT, detail TEXT, ip TEXT)",
    ]
    for statement in statements:
        conn.execute(statement)


MIGRATIONS = [_migration_1, _migration_2]      # a posição + 1 é o número da versão; nunca reordene nem edite uma já publicada


class Database:
    """Acesso ao banco. Use `tx()` para escrever em bloco e os métodos de consulta para o resto."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False, isolation_level=None, timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=10000")
        self.migrate()

    def close(self) -> None:
        with self.lock:
            self.conn.close()

    # ---- migrações ----
    def schema_version(self) -> int:
        has_meta = self.conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='meta'").fetchone()
        if not has_meta:
            return 0
        row = self.conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        return int(row["value"]) if row else 0

    def migrate(self) -> None:
        with self.tx() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
            version = self.schema_version()
            for number, step in enumerate(MIGRATIONS, start=1):
                if number > version:
                    step(conn)
                    conn.execute("INSERT INTO meta(key, value) VALUES('schema_version', ?) "
                                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(number),))

    # ---- transações e consultas genéricas ----
    @contextmanager
    def tx(self):
        """Transação de escrita (BEGIN IMMEDIATE ... COMMIT; ROLLBACK em caso de erro)."""
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                yield self.conn
            except BaseException:
                self.conn.execute("ROLLBACK")
                raise
            else:
                self.conn.execute("COMMIT")

    def query(self, sql: str, params=()) -> list[sqlite3.Row]:
        with self.lock:
            return self.conn.execute(sql, params).fetchall()

    def one(self, sql: str, params=()):
        with self.lock:
            return self.conn.execute(sql, params).fetchone()

    def run(self, sql: str, params=()) -> None:
        with self.tx() as conn:
            conn.execute(sql, params)

    # ---- contas e sessões ----
    def count_students(self) -> int:
        return self.one("SELECT COUNT(*) AS n FROM students")["n"]

    def find_student(self, email: str):
        return self.one("SELECT * FROM students WHERE email=?", (email,))

    def create_student(self, email: str, name: str, password_hash: str):
        """Cria a conta. O PRIMEIRO cadastro vira admin, decidido dentro da transação. Devolve (aluno, é_primeiro).
        Levanta sqlite3.IntegrityError se o e-mail já existir."""
        stamp = now()
        with self.tx() as conn:
            first = conn.execute("SELECT COUNT(*) AS n FROM students").fetchone()["n"] == 0
            cursor = conn.execute("INSERT INTO students(email, name, password_hash, is_admin, created_at, last_seen_at) "
                                  "VALUES(?,?,?,?,?,?)", (email, name, password_hash, 1 if first else 0, stamp, stamp))
        return {"id": cursor.lastrowid, "email": email, "name": name, "is_admin": first}, first

    def set_credentials(self, student_id: int, name: str | None, password_hash: str) -> None:
        if name is None:
            self.run("UPDATE students SET password_hash=? WHERE id=?", (password_hash, student_id))
        else:
            self.run("UPDATE students SET name=?, password_hash=? WHERE id=?", (name, password_hash, student_id))

    def set_admin(self, student_id: int, value: bool = True) -> None:
        self.run("UPDATE students SET is_admin=? WHERE id=?", (1 if value else 0, student_id))

    def create_session(self, student_id: int, token: str, csrf: str, user_agent: str = "",
                       replace_token: str | None = None) -> None:
        """Sessão nova (o token é trocado a cada login); a sessão anterior do navegador é descartada."""
        moment = datetime.now(timezone.utc)
        stamp = moment.isoformat(timespec="seconds")
        expires = (moment + timedelta(days=SESSION_SLIDING_DAYS)).isoformat(timespec="seconds")
        with self.tx() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at<?", (stamp,))
            if replace_token:
                conn.execute("DELETE FROM sessions WHERE token_hash=?", (hash_token(replace_token),))
            conn.execute("INSERT INTO sessions(token_hash, student_id, csrf_token, created_at, last_seen_at, "
                         "expires_at, user_agent) VALUES(?,?,?,?,?,?,?)",
                         (hash_token(token), student_id, csrf, stamp, stamp, expires, (user_agent or "")[:300]))
            conn.execute("UPDATE students SET last_seen_at=? WHERE id=?", (stamp, student_id))

    def student_for_token(self, token: str | None, touch: bool = True):
        """Aluno ({id, email, name, is_admin, csrf_token}) dono do token, ou None (inexistente ou expirada).
        A validade é deslizante (30 dias) e absoluta (90 dias desde a criação)."""
        if not token:
            return None
        digest = hash_token(token)
        row = self.one("SELECT s.id, s.email, s.name, s.is_admin, ss.csrf_token, ss.created_at, ss.last_seen_at AS seen, "
                       "ss.expires_at FROM sessions ss JOIN students s ON s.id = ss.student_id "
                       "WHERE ss.token_hash=?", (digest,))
        if row is None:
            return None
        moment = datetime.now(timezone.utc)
        stamp = moment.isoformat(timespec="seconds")
        if (row["expires_at"] or "") < stamp:
            self.run("DELETE FROM sessions WHERE token_hash=?", (digest,))
            return None
        if touch and (row["seen"] or "") < stamp[:16]:        # compara até o minuto
            created = datetime.fromisoformat(row["created_at"])
            expires = min(moment + timedelta(days=SESSION_SLIDING_DAYS),
                          created + timedelta(days=SESSION_ABSOLUTE_DAYS)).isoformat(timespec="seconds")
            with self.tx() as conn:
                conn.execute("UPDATE sessions SET last_seen_at=?, expires_at=? WHERE token_hash=?", (stamp, expires, digest))
                conn.execute("UPDATE students SET last_seen_at=? WHERE id=?", (stamp, row["id"]))
        return {"id": row["id"], "email": row["email"], "name": row["name"], "is_admin": bool(row["is_admin"]),
                "csrf_token": row["csrf_token"]}

    def logout(self, token: str | None) -> None:
        if token:
            self.run("DELETE FROM sessions WHERE token_hash=?", (hash_token(token),))

    def audit(self, student_id: int | None, action: str, detail: str = "", ip: str = "") -> None:
        """Registro de logins e ações do admin. Nunca grave senhas ou tokens aqui."""
        self.run("INSERT INTO audit_log(at, student_id, action, detail, ip) VALUES(?,?,?,?,?)",
                 (now(), student_id, action, (detail or "")[:500], ip))

    # ---- trilhas (índice) ----
    def trail_exists(self, slug: str) -> bool:
        return self.one("SELECT 1 FROM trails WHERE slug=?", (slug,)) is not None

    def has_item(self, trail: str, block: str, item: str) -> bool:
        return self.one("SELECT 1 FROM items WHERE trail=? AND block_id=? AND item_id=?", (trail, block, item)) is not None

    def trail_active(self, slug: str) -> bool:
        row = self.one("SELECT active FROM trails WHERE slug=?", (slug,))
        return bool(row and row["active"])

    def set_trail_active(self, slug: str, active: bool) -> bool:
        with self.tx() as conn:
            cursor = conn.execute("UPDATE trails SET active=? WHERE slug=?", (1 if active else 0, slug))
            return cursor.rowcount > 0

    def list_trails(self, student_id: int | None = None, only_active: bool = True) -> list[dict]:
        rows = self.query("SELECT * FROM trails " + ("WHERE active=1 " if only_active else "")
                          + "ORDER BY title COLLATE NOCASE, slug")
        out = []
        for t in rows:
            slug = t["slug"]
            n_blocks = self.one("SELECT COUNT(*) AS n FROM blocks WHERE trail=?", (slug,))["n"]
            total = self.one("SELECT COUNT(*) AS n, COALESCE(SUM(CASE WHEN optional=0 THEN 1 ELSE 0 END),0) AS req, "
                             "COALESCE(SUM(CASE WHEN optional=0 THEN COALESCE(minutes,0) ELSE 0 END),0) AS minutes "
                             "FROM items WHERE trail=?", (slug,))
            done = required_done = 0
            if student_id is not None:
                counts = self.one("SELECT COUNT(*) AS n, COALESCE(SUM(CASE WHEN i.optional=0 THEN 1 ELSE 0 END),0) AS req "
                                  "FROM progress p JOIN items i ON i.trail=p.trail AND i.block_id=p.block_id "
                                  "AND i.item_id=p.item_id WHERE p.student_id=? AND p.trail=? AND p.done=1",
                                  (student_id, slug))
                done, required_done = counts["n"], counts["req"]
            try:
                tags = json.loads(t["tags"] or "[]")
            except ValueError:
                tags = []
            out.append({"slug": slug, "title": t["title"], "description": t["description"] or "",
                        "language": t["language"], "level": t["level"], "tags": tags,
                        "cover": f"/api/trails/{slug}/cover" if t["cover"] else None, "active": bool(t["active"]),
                        "blocks": n_blocks, "items": total["n"], "requiredItems": total["req"],
                        "minutes": round(total["minutes"]), "done": done, "requiredDone": required_done})
        return out

    def asset(self, trail: str, path: str):
        return self.one("SELECT * FROM assets WHERE trail=? AND path=?", (trail, path))

    # ---- progresso (por aluno e por trilha) ----
    def progress_state(self, student_id: int, trail: str) -> dict:
        """Mesmo formato do progress.json antigo: {items, answers, notes}."""
        state = {"items": {}, "answers": {}, "notes": {}}
        for r in self.query("SELECT block_id, item_id, done, at FROM progress WHERE student_id=? AND trail=?",
                            (student_id, trail)):
            state["items"][f"{r['block_id']}/{r['item_id']}"] = {"done": bool(r["done"]), "at": r["at"]}
        for r in self.query("SELECT block_id, item_id, question_id, chosen, correct, at FROM answers "
                            "WHERE student_id=? AND trail=?", (student_id, trail)):
            try:
                chosen = json.loads(r["chosen"] or "[]")
            except ValueError:
                chosen = []
            state["answers"].setdefault(f"{r['block_id']}/{r['item_id']}", {})[r["question_id"]] = {
                "chosen": chosen, "correct": bool(r["correct"]), "at": r["at"]}
        for r in self.query("SELECT block_id, item_id, text FROM notes WHERE student_id=? AND trail=?",
                            (student_id, trail)):
            state["notes"][f"{r['block_id']}/{r['item_id']}"] = r["text"]
        return state

    def set_done(self, student_id, trail, block, item, done: bool) -> None:
        self.run("INSERT INTO progress(student_id, trail, block_id, item_id, done, at) VALUES(?,?,?,?,?,?) "
                 "ON CONFLICT(student_id, trail, block_id, item_id) DO UPDATE SET done=excluded.done, at=excluded.at",
                 (student_id, trail, block, item, 1 if done else 0, now()))

    def set_answer(self, student_id, trail, block, item, question, chosen: list, correct: bool, at: str | None = None) -> None:
        self.run("INSERT INTO answers(student_id, trail, block_id, item_id, question_id, chosen, correct, at) "
                 "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(student_id, trail, block_id, item_id, question_id) "
                 "DO UPDATE SET chosen=excluded.chosen, correct=excluded.correct, at=excluded.at",
                 (student_id, trail, block, item, question, json.dumps(chosen, ensure_ascii=False),
                  1 if correct else 0, at or now()))

    def delete_answer(self, student_id, trail, block, item, question) -> None:
        self.run("DELETE FROM answers WHERE student_id=? AND trail=? AND block_id=? AND item_id=? AND question_id=?",
                 (student_id, trail, block, item, question))

    def set_note(self, student_id, trail, block, item, text: str) -> None:
        """Texto vazio (só espaços) apaga a anotação."""
        if not text.strip():
            self.run("DELETE FROM notes WHERE student_id=? AND trail=? AND block_id=? AND item_id=?",
                     (student_id, trail, block, item))
            return
        self.run("INSERT INTO notes(student_id, trail, block_id, item_id, text, at) VALUES(?,?,?,?,?,?) "
                 "ON CONFLICT(student_id, trail, block_id, item_id) DO UPDATE SET text=excluded.text, at=excluded.at",
                 (student_id, trail, block, item, text, now()))

    def import_state(self, student_id: int, trail: str, state: dict) -> dict:
        """Importa um progress.json antigo. Devolve contagens. Não apaga nada existente (só sobrescreve chaves iguais)."""
        counts = {"items": 0, "answers": 0, "notes": 0, "skipped": 0}
        stamp = now()
        with self.tx() as conn:
            for key, value in (state.get("items") or {}).items():
                parts = str(key).split("/")
                if len(parts) != 2 or not isinstance(value, dict):
                    counts["skipped"] += 1
                    continue
                conn.execute("INSERT INTO progress(student_id, trail, block_id, item_id, done, at) VALUES(?,?,?,?,?,?) "
                             "ON CONFLICT(student_id, trail, block_id, item_id) DO UPDATE SET "
                             "done=excluded.done, at=excluded.at",
                             (student_id, trail, parts[0], parts[1], 1 if value.get("done") else 0, value.get("at") or stamp))
                counts["items"] += 1
            for key, questions in (state.get("answers") or {}).items():
                parts = str(key).split("/")
                if len(parts) != 2 or not isinstance(questions, dict):
                    counts["skipped"] += 1
                    continue
                for question, value in questions.items():
                    if not isinstance(value, dict):
                        counts["skipped"] += 1
                        continue
                    conn.execute("INSERT INTO answers(student_id, trail, block_id, item_id, question_id, chosen, correct, at) "
                                 "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(student_id, trail, block_id, item_id, question_id) "
                                 "DO UPDATE SET chosen=excluded.chosen, correct=excluded.correct, at=excluded.at",
                                 (student_id, trail, parts[0], parts[1], str(question),
                                  json.dumps(list(value.get("chosen") or []), ensure_ascii=False),
                                  1 if value.get("correct") else 0, value.get("at") or stamp))
                    counts["answers"] += 1
            for key, text in (state.get("notes") or {}).items():
                parts = str(key).split("/")
                if len(parts) != 2 or not isinstance(text, str) or not text.strip():
                    counts["skipped"] += 1
                    continue
                conn.execute("INSERT INTO notes(student_id, trail, block_id, item_id, text, at) VALUES(?,?,?,?,?,?) "
                             "ON CONFLICT(student_id, trail, block_id, item_id) DO UPDATE SET text=excluded.text, at=excluded.at",
                             (student_id, trail, parts[0], parts[1], text, stamp))
                counts["notes"] += 1
        return counts

    # ---- rastreio de tempo ----
    def open_visit(self, student_id, trail, block, item) -> int:
        stamp = now()
        with self.tx() as conn:
            cursor = conn.execute("INSERT INTO visits(student_id, trail, block_id, item_id, started_at, seconds, last_beat_at) "
                                  "VALUES(?,?,?,?,?,0,?)", (student_id, trail, block, item, stamp, stamp))
            return cursor.lastrowid

    def add_seconds(self, student_id: int, visit_id: int, seconds: int) -> int | None:
        """Soma segundos (1..30 por chamada; teto de 4 h por visita) a uma visita do próprio aluno.
        Devolve o total, ou None se a visita não existe ou é de outro aluno."""
        seconds = max(1, min(MAX_BEAT_SECONDS, int(seconds)))
        with self.tx() as conn:
            row = conn.execute("SELECT seconds FROM visits WHERE id=? AND student_id=?", (visit_id, student_id)).fetchone()
            if row is None:
                return None
            total = min(MAX_VISIT_SECONDS, (row["seconds"] or 0) + seconds)
            conn.execute("UPDATE visits SET seconds=?, last_beat_at=? WHERE id=?", (total, now(), visit_id))
            return total


def default_db_path(explicit=None) -> Path:
    """--db, senão K_STUDY_DB, senão ./data/k_study.db."""
    return Path(explicit or os.environ.get("K_STUDY_DB") or Path("data") / "k_study.db")
