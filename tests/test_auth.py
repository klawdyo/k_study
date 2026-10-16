import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

from conftest import PASSWORD, Browser, start
from k_study import security
from k_study.server import make_server

REG = {"email": "bia@exemplo.com", "name": "Bia", "password": PASSWORD, "passwordConfirm": PASSWORD}


def test_anonimo_e_rotas_protegidas(browser):
    status, body = browser.call("GET", "/api/auth/me")
    assert status == 200 and body["student"] is None and body["csrfToken"]
    status, err = browser.call("GET", "/api/trails/demo/progress")
    assert status == 401 and err["error"] == "login_required"
    assert browser.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True}, csrf=False)[0] in (401, 403)
    browser.me()
    assert browser.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True})[0] == 401
    assert browser.call("POST", "/api/track", {"event": "open"})[0] == 401


def test_primeiro_cadastro_vira_admin_e_os_outros_nao(make_browser, db):
    a, b = make_browser(), make_browser()
    status, body = a.register("ana@exemplo.com", "Ana")
    assert status == 200 and body["isFirstAdmin"] is True and body["student"] == {
        "email": "ana@exemplo.com", "name": "Ana", "isAdmin": True}
    status, body = b.register("bia@exemplo.com", "Bia")
    assert status == 200 and body["isFirstAdmin"] is False and body["student"]["isAdmin"] is False
    assert [r["is_admin"] for r in db.query("SELECT is_admin FROM students ORDER BY id")] == [1, 0]


def test_primeiro_admin_sem_corrida(server):
    results, port = [], server.server_address[1]

    def go(n):
        b = Browser(port)
        results.append(b.register(f"u{n}@exemplo.com", f"U{n}")[1].get("isFirstAdmin"))

    threads = [threading.Thread(target=go, args=(n,)) for n in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert results.count(True) == 1 and results.count(False) == 7


def test_check_informa_existencia_e_primeiro_usuario(browser, make_browser):
    browser.me()
    assert browser.call("POST", "/api/auth/check", {"email": "Ana@Exemplo.com"})[1] == {
        "exists": False, "firstUser": True, "needsSetup": False}
    make_browser().register("ana@exemplo.com", "Ana")
    assert browser.call("POST", "/api/auth/check", {"email": " ANA@exemplo.com "})[1] == {
        "exists": True, "firstUser": False, "needsSetup": False}


def test_cadastro_normaliza_email_e_valida_campos(browser):
    browser.me()
    for email in ("", "sem-arroba", "a@b", "a b@c.com", None, 12, "@x.com", "a@.com", "a@@b.com"):
        status, err = browser.call("POST", "/api/auth/register", {**REG, "email": email})
        assert status == 400 and err["error"] == "invalid_email" and err["message"], email
    for name in ("", "   ", None, "x" * 81, "a\x00b"):
        assert browser.call("POST", "/api/auth/register", {**REG, "name": name})[1]["error"] == "invalid_name", name
    for password in ("curta", "x" * 129, None, 12345678):
        body = {**REG, "password": password, "passwordConfirm": password}
        assert browser.call("POST", "/api/auth/register", body)[1]["error"] == "invalid_password", password
    body = {**REG, "email": "igual@exemplo.com", "password": "igual@exemplo.com", "passwordConfirm": "igual@exemplo.com"}
    assert browser.call("POST", "/api/auth/register", body)[1]["error"] == "invalid_password"
    status, err = browser.call("POST", "/api/auth/register", {**REG, "passwordConfirm": "outra-senha-1"})
    assert status == 400 and err["error"] == "password_mismatch"
    status, body = browser.call("POST", "/api/auth/register", {**REG, "email": "  Bia@Exemplo.COM ", "name": "  Bia   Souza "})
    assert status == 200 and body["student"]["email"] == "bia@exemplo.com" and body["student"]["name"] == "Bia Souza"


def test_email_repetido_e_recusado(make_browser):
    make_browser().register("ana@exemplo.com", "Ana")
    status, err = make_browser().register("ANA@exemplo.com", "Outra")
    assert status == 409 and err["error"] == "email_taken"


def test_login_certo_e_errado_com_mensagem_generica(make_browser, browser):
    make_browser().register("ana@exemplo.com", "Ana")
    browser.me()
    wrong = browser.call("POST", "/api/auth/login", {"email": "ana@exemplo.com", "password": "senha-errada-1"})
    ghost = browser.call("POST", "/api/auth/login", {"email": "ninguem@exemplo.com", "password": PASSWORD})
    assert wrong[0] == ghost[0] == 401 and wrong[1] == ghost[1]
    assert wrong[1]["error"] == "invalid_credentials"
    status, body = browser.login("ana@exemplo.com")
    assert status == 200 and body["student"]["name"] == "Ana" and body["csrfToken"]
    assert browser.call("GET", "/api/auth/me")[1]["student"]["email"] == "ana@exemplo.com"


def test_senhas_nunca_em_texto_puro_e_hashes_diferentes(make_browser, db):
    make_browser().register("ana@exemplo.com", "Ana")
    make_browser().register("bia@exemplo.com", "Bia")
    hashes = [r["password_hash"] for r in db.query("SELECT password_hash FROM students ORDER BY id")]
    assert hashes[0] != hashes[1]                                  # sal diferente por conta, mesma senha
    for h in hashes:
        assert h.startswith("scrypt$") and PASSWORD not in h and len(h.split("$")) == 6
    assert db.one("SELECT COUNT(*) AS n FROM audit_log WHERE detail LIKE ?", (f"%{PASSWORD}%",))["n"] == 0


def test_cookie_da_sessao_e_o_hash_no_banco(make_browser, db):
    b = make_browser()
    b.register("ana@exemplo.com", "Ana")
    status, data, headers = make_browser().raw("GET", "/api/auth/me")
    assert "kstudy_pre=" in headers["Set-Cookie"] and "HttpOnly" in headers["Set-Cookie"]
    c = make_browser()
    c.me()
    status, data, headers = c.raw("POST", "/api/auth/login", {"email": "ana@exemplo.com", "password": PASSWORD})
    cookie = headers["Set-Cookie"]
    assert cookie.startswith("kstudy_sid=") and "HttpOnly" in cookie and "SameSite=Strict" in cookie
    assert "Path=/" in cookie and "Max-Age=2592000" in cookie and "Secure" not in cookie
    token = c.cookies["kstudy_sid"]
    hashes = {r["token_hash"] for r in db.query("SELECT token_hash FROM sessions")}
    assert hashlib.sha256(token.encode()).hexdigest() in hashes and token not in hashes


def test_cookie_secure_com_https(content, db, monkeypatch):
    monkeypatch.setenv("K_STUDY_HTTPS", "1")
    srv = make_server(content, db, port=0)
    port = start(srv)
    try:
        b = Browser(port)
        b.me()
        headers = b.raw("POST", "/api/auth/register", {**REG})[2]
        assert "; Secure" in headers["Set-Cookie"]
    finally:
        srv.shutdown()


def test_token_de_sessao_e_trocado_a_cada_login(make_browser, db):
    make_browser().register("ana@exemplo.com", "Ana")
    b = make_browser()
    b.login()
    first = b.cookies["kstudy_sid"]
    b.login()
    assert b.cookies["kstudy_sid"] != first
    assert db.one("SELECT COUNT(*) AS n FROM sessions WHERE student_id=1")["n"] == 2      # a do cadastro + a do navegador b
    b.cookies["kstudy_sid"] = first
    assert b.call("GET", "/api/auth/me")[1]["student"] is None                           # o token antigo morreu


def test_logout_apaga_no_servidor(student, db):
    status, data, headers = student.raw("POST", "/api/auth/logout", {})
    assert status == 200 and "Max-Age=0" in headers["Set-Cookie"]
    assert db.one("SELECT COUNT(*) AS n FROM sessions WHERE student_id=2")["n"] == 0
    assert student.call("GET", "/api/trails/demo/progress")[0] == 401


def test_cookie_falso_nao_autentica(browser):
    browser.cookies["kstudy_sid"] = "token-inventado"
    assert browser.call("GET", "/api/auth/me")[1]["student"] is None
    assert browser.call("GET", "/api/trails/demo/progress")[0] == 401


def test_sessao_expira_por_inatividade_e_por_limite_absoluto(student, db):
    old = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(timespec="seconds")
    db.run("UPDATE sessions SET expires_at=? WHERE student_id=2", (old,))
    assert student.call("GET", "/api/auth/me")[1]["student"] is None
    assert db.one("SELECT COUNT(*) AS n FROM sessions WHERE student_id=2")["n"] == 0


def test_validade_deslizante_respeita_o_teto_de_90_dias(student, db):
    created = (datetime.now(timezone.utc) - timedelta(days=89)).isoformat(timespec="seconds")
    db.run("UPDATE sessions SET created_at=?, last_seen_at='2020-01-01T00:00:00+00:00' WHERE student_id=2", (created,))
    assert student.call("GET", "/api/auth/me")[1]["student"] is not None
    expires = datetime.fromisoformat(db.one("SELECT expires_at FROM sessions WHERE student_id=2")["expires_at"])
    assert expires - datetime.now(timezone.utc) < timedelta(days=2)       # não passa de 90 dias desde a criação


def test_isolamento_entre_alunos(make_browser, admin):
    a, b = make_browser(), make_browser()
    a.register("ana@exemplo.com", "Ana")
    b.register("bia@exemplo.com", "Bia")
    a.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True})
    a.call("PUT", "/api/trails/demo/progress/notes/block-1/r", {"text": "da ana"})
    assert b.call("GET", "/api/trails/demo/progress")[1] == {"items": {}, "answers": {}, "notes": {}}
    assert b.call("GET", "/api/trails")[1][0]["done"] == 0 and a.call("GET", "/api/trails")[1][0]["done"] == 1
    visit = a.call("POST", "/api/track", {"event": "open", "trail": "demo", "block": "block-1", "item": "r"})[1]["visit"]
    assert b.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 5})[0] == 404


# ---- CSRF ----

def test_csrf_sem_token_ou_com_token_errado(student):
    path = "/api/trails/demo/progress/items/block-1/r"
    status, err = student.call("PUT", path, {"done": True}, csrf=False)
    assert status == 403 and err["error"] == "csrf_failed"
    assert student.call("PUT", path, {"done": True}, headers={"X-CSRF-Token": "errado"})[0] == 403
    assert student.call("PUT", path, {"done": True})[0] == 200
    assert student.call("POST", "/api/auth/logout", {}, csrf=False)[0] == 403


def test_csrf_pre_login(browser, make_browser):
    make_browser().register("ana@exemplo.com", "Ana")
    assert browser.call("POST", "/api/auth/check", {"email": "ana@exemplo.com"}, csrf=False)[0] == 403
    browser.me()
    assert browser.call("POST", "/api/auth/check", {"email": "ana@exemplo.com"})[0] == 200
    other = make_browser()
    other.me()                                       # token de OUTRO navegador não vale neste
    assert browser.call("POST", "/api/auth/check", {"email": "ana@exemplo.com"},
                        headers={"X-CSRF-Token": other.csrf})[0] == 403


def test_csrf_beacon_no_corpo(student):
    visit = student.call("POST", "/api/track", {"event": "open", "trail": "demo", "block": "block-1", "item": "r"})[1]["visit"]
    body = {"event": "leave", "visit": visit, "seconds": 4, "csrf": student.csrf}
    status, out = student.call("POST", "/api/track", body, csrf=False)
    assert status == 200 and out["seconds"] == 4
    assert student.call("POST", "/api/track", {**body, "csrf": "x"}, csrf=False)[0] == 403
    # o corpo só vale para /api/track
    assert student.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True, "csrf": student.csrf},
                        csrf=False)[0] == 403


# ---- limite de tentativas ----

def test_limite_de_tentativas_por_email_e_ip(make_browser, browser):
    make_browser().register("ana@exemplo.com", "Ana")
    browser.me()
    bad = {"email": "ana@exemplo.com", "password": "senha-errada-1"}
    for _ in range(security.FAILS_PER_KEY):
        assert browser.call("POST", "/api/auth/login", bad)[0] == 401
    status, data, headers = browser.raw("POST", "/api/auth/login", {"email": "ana@exemplo.com", "password": PASSWORD})
    assert status == 429 and int(headers["Retry-After"]) > 0 and json.loads(data)["error"] == "too_many_attempts"
    assert browser.call("POST", "/api/auth/check", {"email": "ana@exemplo.com"})[0] == 429
    assert browser.call("POST", "/api/auth/check", {"email": "outra@exemplo.com"})[0] == 200      # outro e-mail segue livre


def test_limite_por_ip(make_browser, browser):
    browser.me()
    for n in range(security.FAILS_PER_IP):
        browser.call("POST", "/api/auth/login", {"email": f"u{n}@exemplo.com", "password": "senha-errada-1"})
    assert browser.call("POST", "/api/auth/check", {"email": "novo@exemplo.com"})[0] == 429


def test_login_certo_zera_as_falhas_do_email(make_browser, browser):
    make_browser().register("ana@exemplo.com", "Ana")
    browser.me()
    for _ in range(security.FAILS_PER_KEY - 1):
        browser.call("POST", "/api/auth/login", {"email": "ana@exemplo.com", "password": "senha-errada-1"})
    assert browser.login()[0] == 200
    for _ in range(security.FAILS_PER_KEY - 1):
        assert browser.call("POST", "/api/auth/login", {"email": "ana@exemplo.com", "password": "senha-errada-1"})[0] == 401


# ---- auditoria ----

def test_auditoria_de_logins(make_browser, browser, db):
    make_browser().register("ana@exemplo.com", "Ana")
    browser.me()
    browser.call("POST", "/api/auth/login", {"email": "ana@exemplo.com", "password": "senha-errada-1"})
    browser.login()
    actions = [r["action"] for r in db.query("SELECT action FROM audit_log ORDER BY id")]
    assert actions == ["register", "login_failed", "login"]


# ---- migração v1 -> v2 ----

def test_migracao_v1_para_v2_mantem_contas_e_pede_senha(tmp_path, content):
    from k_study.db import Database, _migration_1
    path = tmp_path / "antigo.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    _migration_1(conn)
    conn.execute("INSERT INTO meta VALUES('schema_version','1')")
    conn.execute("INSERT INTO students(email, created_at) VALUES('velha@exemplo.com','2026-01-01T00:00:00+00:00')")
    conn.execute("INSERT INTO sessions(token_hash, student_id) VALUES('x', 1)")
    conn.execute("INSERT INTO progress VALUES(1,'demo','block-1','r',1,'2026-01-02T00:00:00+00:00')")
    conn.execute("INSERT INTO trails(slug, title, manifest_mtime) VALUES('demo','Demo',123.0)")
    conn.commit()
    conn.close()
    db = Database(path)
    assert db.schema_version() == 2
    row = db.find_student("velha@exemplo.com")
    assert row["password_hash"] == "" and row["name"] == "" and row["is_admin"] == 0
    assert db.one("SELECT COUNT(*) AS n FROM sessions")["n"] == 0                 # sessões antigas descartadas
    assert db.one("SELECT done FROM progress")["done"] == 1                       # progresso intacto
    assert db.one("SELECT active, manifest_mtime FROM trails")["active"] == 1
    assert db.one("SELECT manifest_mtime FROM trails")["manifest_mtime"] == 0     # força reindexar

    srv = make_server(content, db, port=0)
    port = start(srv)
    try:
        b = Browser(port)
        b.me()
        assert b.call("POST", "/api/auth/check", {"email": "velha@exemplo.com"})[1] == {
            "exists": True, "firstUser": False, "needsSetup": True}
        assert b.call("POST", "/api/auth/login", {"email": "velha@exemplo.com", "password": PASSWORD})[0] == 401
        body = {"email": "velha@exemplo.com", "name": "Velha", "password": PASSWORD, "passwordConfirm": PASSWORD}
        status, out = b.call("POST", "/api/auth/register", body)
        assert status == 200 and out["student"]["name"] == "Velha"
        b.csrf = out["csrfToken"]
        assert b.call("GET", "/api/trails/demo/progress")[1]["items"]["block-1/r"]["done"] is True
        assert db.find_student("velha@exemplo.com")["password_hash"].startswith("scrypt$")
        assert b.call("POST", "/api/auth/register", body)[0] == 409          # agora tem senha: não se redefine por aqui
    finally:
        srv.shutdown()
