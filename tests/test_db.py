import sqlite3
import threading

from k_study.db import Database, MIGRATIONS, hash_token, normalize_email

TABLES = {
    "meta": ["key", "value"],
    "trails": ["slug", "title", "description", "language", "level", "tags", "manifest_mtime", "synced_at"],
    "blocks": ["trail", "block_id", "title", "position", "file"],
    "items": ["trail", "block_id", "item_id", "section", "position", "type", "title", "path", "optional", "minutes"],
    "students": ["id", "email", "created_at", "last_seen_at"],
    "sessions": ["token_hash", "student_id", "created_at", "last_seen_at", "user_agent"],
    "progress": ["student_id", "trail", "block_id", "item_id", "done", "at"],
    "answers": ["student_id", "trail", "block_id", "item_id", "question_id", "chosen", "correct", "at"],
    "notes": ["student_id", "trail", "block_id", "item_id", "text", "at"],
    "visits": ["id", "student_id", "trail", "block_id", "item_id", "started_at", "seconds", "last_beat_at"],
}


def test_esquema_segue_o_contrato(db):
    for table, columns in TABLES.items():
        assert [r["name"] for r in db.query(f"PRAGMA table_info({table})")] == columns, table
    indexes = {r["name"] for r in db.query("PRAGMA index_list(visits)")}
    assert {"visits_student", "visits_item"} <= indexes


def test_wal_chaves_estrangeiras_e_versao(db):
    assert db.one("PRAGMA journal_mode")[0] == "wal"
    assert db.one("PRAGMA foreign_keys")[0] == 1
    assert db.schema_version() == len(MIGRATIONS)
    try:
        db.run("INSERT INTO sessions(token_hash, student_id) VALUES('x', 999)")
        raise AssertionError("a chave estrangeira deveria recusar")
    except sqlite3.IntegrityError:
        pass


def test_reabrir_nao_repete_migracoes_nem_perde_dados(tmp_path):
    path = tmp_path / "novo" / "pasta" / "k.db"          # a pasta do banco é criada
    first = Database(path)
    first.get_or_create_student("ana@exemplo.com")
    first.close()
    second = Database(path)
    assert second.schema_version() == len(MIGRATIONS)
    assert second.one("SELECT COUNT(*) AS n FROM students")["n"] == 1
    second.close()


def test_transacao_desfaz_em_caso_de_erro(db):
    try:
        with db.tx() as conn:
            conn.execute("INSERT INTO students(email) VALUES('a@b.co')")
            raise RuntimeError("falha")
    except RuntimeError:
        pass
    assert db.one("SELECT COUNT(*) AS n FROM students")["n"] == 0


def test_email_normalizado():
    assert normalize_email("  Ana@Exemplo.COM ") == "ana@exemplo.com"
    assert normalize_email("a@b") is None and normalize_email("") is None and normalize_email(None) is None
    assert normalize_email("a" * 250 + "@x.com") is None
    assert len(hash_token("x")) == 64


def test_escritas_concorrentes(db):
    student, _ = db.get_or_create_student("ana@exemplo.com")
    errors = []

    def work(n):
        try:
            for i in range(20):
                db.set_done(student["id"], "t", "b", f"i{n}-{i}", True)
                visit = db.open_visit(student["id"], "t", "b", "i")
                db.add_seconds(student["id"], visit, 5)
        except Exception as exc:          # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=work, args=(n,)) for n in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert errors == []
    assert db.one("SELECT COUNT(*) AS n FROM progress")["n"] == 160
    assert db.one("SELECT SUM(seconds) AS s FROM visits")["s"] == 160 * 5
