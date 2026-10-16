import hashlib


def test_sem_login_o_aluno_e_anonimo_e_o_progresso_exige_login(browser):
    assert browser.call("GET", "/api/me") == (200, {"student": None})
    status, err = browser.call("GET", "/api/trails/demo/progress")
    assert status == 401 and err["error"] == "login_required"
    assert browser.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True})[0] == 401
    assert browser.call("POST", "/api/track", {"event": "open"})[0] == 401


def test_login_cadastra_e_cookie_tem_os_atributos_do_contrato(browser, db):
    status, data, headers = browser.raw("POST", "/api/login", {"email": "  Ana@Exemplo.COM "})
    assert status == 200
    import json
    body = json.loads(data)
    assert body == {"student": {"email": "ana@exemplo.com"}, "created": True}
    cookie = headers["Set-Cookie"]
    assert cookie.startswith("kstudy_sid=") and "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert "Path=/" in cookie and "Max-Age=31536000" in cookie
    assert browser.call("GET", "/api/me") == (200, {"student": {"email": "ana@exemplo.com"}})
    # o banco guarda só o hash SHA-256 do token
    token = browser.cookie.split("=", 1)[1]
    row = db.one("SELECT token_hash FROM sessions")
    assert row["token_hash"] == hashlib.sha256(token.encode()).hexdigest() and token not in row["token_hash"]


def test_email_existente_vincula_o_navegador_sem_recadastrar(make_browser):
    a, b = make_browser(), make_browser()
    assert a.login("ana@exemplo.com")[1]["created"] is True
    status, body = b.login("ANA@exemplo.com")
    assert status == 200 and body["created"] is False


def test_emails_invalidos_sao_recusados(browser):
    for email in ("", "sem-arroba", "a@b", "a b@c.com", None, 12, "@x.com", "a@.com"):
        status, err = browser.call("POST", "/api/login", {"email": email})
        assert status == 400 and err["error"] == "invalid_email" and err["message"], email
    assert browser.call("GET", "/api/me")[1] == {"student": None}


def test_dois_navegadores_com_o_mesmo_email_veem_o_mesmo_progresso(make_browser):
    a, b, c = make_browser(), make_browser(), make_browser()
    a.login("ana@exemplo.com")
    a.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True})
    a.call("PUT", "/api/trails/demo/progress/notes/block-1/r", {"text": "lembrar"})
    b.login("ana@exemplo.com")
    state = b.call("GET", "/api/trails/demo/progress")[1]
    assert state["items"]["block-1/r"]["done"] is True and state["notes"]["block-1/r"] == "lembrar"
    c.login("bia@exemplo.com")
    assert c.call("GET", "/api/trails/demo/progress")[1] == {"items": {}, "answers": {}, "notes": {}}
    assert c.call("GET", "/api/trails")[1][0]["done"] == 0 and b.call("GET", "/api/trails")[1][0]["done"] == 1


def test_logout_apaga_a_sessao_e_o_cookie(student, db):
    status, data, headers = student.raw("POST", "/api/logout", {})
    assert status == 200 and "Max-Age=0" in headers["Set-Cookie"]
    assert db.one("SELECT COUNT(*) AS n FROM sessions")["n"] == 0
    assert student.call("GET", "/api/me")[1] == {"student": None}
    assert student.call("GET", "/api/trails/demo/progress")[0] == 401


def test_cookie_falso_nao_autentica(browser):
    browser.cookie = "kstudy_sid=token-inventado"
    assert browser.call("GET", "/api/me")[1] == {"student": None}
    assert browser.call("GET", "/api/trails/demo/progress")[0] == 401


def test_trocar_de_email_no_mesmo_navegador_troca_o_aluno(student, db):
    student.login("bia@exemplo.com")
    assert student.call("GET", "/api/me")[1]["student"]["email"] == "bia@exemplo.com"
    assert db.one("SELECT COUNT(*) AS n FROM sessions")["n"] == 1        # a sessão antiga é descartada


def test_sessao_atualiza_last_seen_at(student, db):
    db.run("UPDATE sessions SET last_seen_at='2020-01-01T00:00:00+00:00'")
    student.call("GET", "/api/me")
    assert db.one("SELECT last_seen_at FROM sessions")["last_seen_at"] > "2020"
