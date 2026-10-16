"""Banco de dados SQLite do k_study (modo WAL): esquema, migrações e consultas.

O banco guarda ESTADO (índice do conteúdo, alunos, sessões, progresso, visitas). O corpo das aulas fica em arquivos.
Uma única conexão compartilhada entre as threads do servidor, protegida por um lock reentrante: simples e seguro
(o volume de escrita é pequeno). O esquema segue exatamente docs/arquitetura.md, seção 4.
"""
import hashlib
import json
import os
import re
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

EMAIL = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")
MAX_BEAT_SECONDS = 30            # limite por chamada de beat/leave
MAX_VISIT_SECONDS = 4 * 3600     # teto de uma visita


def now() -> str:
    """Data/hora atual em ISO 8601 UTC."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_email(text) -> str | None:
    """Normaliza (strip + minúsculas) e valida de forma simples. Devolve None se inválido."""
    email = str(text or "").strip().lower()
    return email if len(email) <= 254 and EMAIL.match(email) else None


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


MIGRATIONS = [_migration_1]      # a posição + 1 é o número da versão; nunca reordene nem edite uma já publicada


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

    # ---- alunos e sessões ----
    def login(self, email: str, token: str, user_agent: str = "", replace_token: str | None = None):
        """Vincula o navegador (token) ao aluno do e-mail; cadastra se não existir. Devolve (aluno, criado)."""
        stamp = now()
        with self.tx() as conn:
            row = conn.execute("SELECT id, email FROM students WHERE email=?", (email,)).fetchone()
            created = row is None
            if created:
                cursor = conn.execute("INSERT INTO students(email, created_at, last_seen_at) VALUES(?,?,?)",
                                      (email, stamp, stamp))
                student = {"id": cursor.lastrowid, "email": email}
            else:
                student = {"id": row["id"], "email": row["email"]}
                conn.execute("UPDATE students SET last_seen_at=? WHERE id=?", (stamp, student["id"]))
            if replace_token:
                conn.execute("DELETE FROM sessions WHERE token_hash=?", (hash_token(replace_token),))
            conn.execute("INSERT INTO sessions(token_hash, student_id, created_at, last_seen_at, user_agent) "
                         "VALUES(?,?,?,?,?)", (hash_token(token), student["id"], stamp, stamp, (user_agent or "")[:300]))
        return student, created

    def student_for_token(self, token: str | None, touch: bool = True):
        """Aluno ({id, email}) dono do token, ou None. Atualiza last_seen_at (no máximo uma vez por minuto)."""
        if not token:
            return None
        digest = hash_token(token)
        row = self.one("SELECT s.id, s.email, ss.last_seen_at AS seen FROM sessions ss "
                       "JOIN students s ON s.id = ss.student_id WHERE ss.token_hash=?", (digest,))
        if row is None:
            return None
        stamp = now()
        if touch and (row["seen"] or "") < stamp[:16]:        # compara até o minuto
            with self.tx() as conn:
                conn.execute("UPDATE sessions SET last_seen_at=? WHERE token_hash=?", (stamp, digest))
                conn.execute("UPDATE students SET last_seen_at=? WHERE id=?", (stamp, row["id"]))
        return {"id": row["id"], "email": row["email"]}

    def logout(self, token: str | None) -> None:
        if token:
            self.run("DELETE FROM sessions WHERE token_hash=?", (hash_token(token),))

    def get_or_create_student(self, email: str) -> tuple[dict, bool]:
        """Para a CLI (import-progress): devolve (aluno, criado) sem criar sessão."""
        stamp = now()
        with self.tx() as conn:
            row = conn.execute("SELECT id, email FROM students WHERE email=?", (email,)).fetchone()
            if row:
                return {"id": row["id"], "email": row["email"]}, False
            cursor = conn.execute("INSERT INTO students(email, created_at, last_seen_at) VALUES(?,?,?)",
                                  (email, stamp, stamp))
            return {"id": cursor.lastrowid, "email": email}, True

    # ---- trilhas (índice) ----
    def trail_exists(self, slug: str) -> bool:
        return self.one("SELECT 1 FROM trails WHERE slug=?", (slug,)) is not None

    def has_item(self, trail: str, block: str, item: str) -> bool:
        return self.one("SELECT 1 FROM items WHERE trail=? AND block_id=? AND item_id=?", (trail, block, item)) is not None

    def list_trails(self, student_id: int | None = None) -> list[dict]:
        rows = self.query("SELECT * FROM trails ORDER BY title COLLATE NOCASE, slug")
        out = []
        for t in rows:
            slug = t["slug"]
            n_blocks = self.one("SELECT COUNT(*) AS n FROM blocks WHERE trail=?", (slug,))["n"]
            total = self.one("SELECT COUNT(*) AS n, COALESCE(SUM(CASE WHEN optional=0 THEN 1 ELSE 0 END),0) AS req, "
                             "COALESCE(SUM(CASE WHEN optional=0 THEN COALESCE(minutes,0) ELSE 0 END),0) AS minutes "
                             "FROM items WHERE trail=?", (slug,))
            done = 0
            if student_id is not None:
                done = self.one("SELECT COUNT(*) AS n FROM progress p JOIN items i ON i.trail=p.trail AND "
                                "i.block_id=p.block_id AND i.item_id=p.item_id "
                                "WHERE p.student_id=? AND p.trail=? AND p.done=1 AND i.optional=0",
                                (student_id, slug))["n"]
            try:
                tags = json.loads(t["tags"] or "[]")
            except ValueError:
                tags = []
            out.append({"slug": slug, "title": t["title"], "description": t["description"] or "",
                        "language": t["language"], "level": t["level"], "tags": tags, "blocks": n_blocks,
                        "items": total["n"], "requiredItems": total["req"], "minutes": round(total["minutes"]),
                        "done": done})
        return out

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
