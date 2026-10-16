"""Entrada com o Google: o botão só existe com as duas variáveis preenchidas; o fluxo é testado com um Google falso
(nenhuma rede): `oauth.exchange_code` é trocado por uma função que devolve a identidade ou levanta OAuthError."""
import http.client
import json
import time
import urllib.parse

import pytest

from conftest import PASSWORD, Browser
from k_study import oauth, security

CALLBACK = "/auth/oauth/google/callback"


@pytest.fixture()
def google(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "id-de-teste.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "segredo-de-teste")


def no_redirect(browser, path):
    """GET sem seguir redirecionamentos; devolve (status, cabeçalhos)."""
    status, data, headers = browser.raw("GET", path)
    return status, headers


def start_flow(browser):
    status, headers = no_redirect(browser, "/auth/oauth/google/start")
    assert status == 302
    query = urllib.parse.parse_qs(urllib.parse.urlparse(headers["Location"]).query)
    return headers, query


def fake_identity(monkeypatch, email="gina@exemplo.com", name="Gina Google", error=None):
    def fake(config, code, redirect_uri, flow):
        if error:
            raise oauth.OAuthError(error)
        return {"email": email, "name": name}
    monkeypatch.setattr(oauth, "exchange_code", fake)


# ---- o botão só aparece se estiver configurado ----

def test_sem_variaveis_nao_ha_botao_nem_rotas(browser):
    assert browser.call("GET", "/api/auth/me")[1]["oauth"] == {"google": False}
    for path in ("/auth/oauth/google/start", CALLBACK + "?code=x&state=y"):
        assert browser.call("GET", path)[0] == 404


def test_variaveis_vazias_ou_so_uma_nao_ativam(browser, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "")
    assert browser.call("GET", "/api/auth/me")[1]["oauth"]["google"] is False
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "so-o-id")
    assert browser.call("GET", "/api/auth/me")[1]["oauth"]["google"] is False
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "   ")
    assert browser.call("GET", "/api/auth/me")[1]["oauth"]["google"] is False
    assert browser.call("GET", "/auth/oauth/google/start")[0] == 404


def test_com_as_duas_variaveis_o_botao_aparece(browser, google):
    assert browser.call("GET", "/api/auth/me")[1]["oauth"] == {"google": True}


def test_o_segredo_do_google_nunca_vai_para_o_cliente(browser, google):
    headers, query = start_flow(browser)
    blob = json.dumps(browser.call("GET", "/api/auth/me")[1]) + headers["Location"] + str(headers)
    assert "segredo-de-teste" not in blob


# ---- início do fluxo ----

def test_inicio_redireciona_ao_google_com_state_pkce_e_nonce(browser, google):
    headers, query = start_flow(browser)
    assert headers["Location"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert query["client_id"] == ["id-de-teste.apps.googleusercontent.com"] and query["response_type"] == ["code"]
    assert query["redirect_uri"] == [f"http://127.0.0.1:{browser.port}{CALLBACK}"]          # fixo no sistema
    assert query["scope"] == ["openid email profile"] and query["code_challenge_method"] == ["S256"]
    assert query["state"][0] and query["nonce"][0] and query["code_challenge"][0]
    cookie = headers["Set-Cookie"]
    assert cookie.startswith("kstudy_oauth=") and "HttpOnly" in cookie and "SameSite=Lax" in cookie and "Path=/auth/oauth/" in cookie
    assert "Max-Age=600" in cookie


def test_retorno_usa_https_quando_configurado(browser, google, monkeypatch, server):
    server.app.https = True
    headers, query = start_flow(browser)
    assert query["redirect_uri"][0].startswith("https://127.0.0.1:") and query["redirect_uri"][0].endswith(CALLBACK)
    assert "; Secure" in headers["Set-Cookie"]


def test_host_nao_permitido_nao_vira_endereco_de_retorno(server, google):
    port = server.server_address[1]
    status, data, headers = Browser(port).raw("GET", "/auth/oauth/google/start", host="evil.example.com")
    assert status == 403 and "Location" not in headers


def test_hosts_extras_so_com_variavel(server, google, monkeypatch):
    port = server.server_address[1]
    assert Browser(port).raw("GET", "/api/auth/me", host="estudos.exemplo.com")[0] == 403
    server.app.allowed_hosts = {"estudos.exemplo.com"}
    assert Browser(port).raw("GET", "/api/auth/me", host="estudos.exemplo.com")[0] == 200
    status, data, headers = Browser(port).raw("GET", "/auth/oauth/google/start", host="estudos.exemplo.com")
    assert urllib.parse.parse_qs(urllib.parse.urlparse(headers["Location"]).query)["redirect_uri"] == ["http://estudos.exemplo.com" + CALLBACK]


# ---- retorno do Google ----

def test_cadastro_pelo_google_primeiro_vira_admin_e_entra_logado(browser, google, monkeypatch, db):
    fake_identity(monkeypatch)
    headers, query = start_flow(browser)
    status, headers = no_redirect(browser, f"{CALLBACK}?code=abc&state={query['state'][0]}")
    assert status == 302 and headers["Location"] == "/"
    assert "kstudy_sid=" in headers["Set-Cookie"] or browser.cookies.get("kstudy_sid")
    me = browser.call("GET", "/api/auth/me")[1]
    assert me["student"] == {"email": "gina@exemplo.com", "name": "Gina Google", "isAdmin": True}
    row = db.find_student("gina@exemplo.com")
    assert row["password_hash"] == oauth.UNUSABLE_HASH and row["is_admin"] == 1
    assert db.one("SELECT action FROM audit_log ORDER BY id DESC")["action"] == "login_oauth"


def test_conta_criada_pelo_google_nao_pode_ser_reivindicada_por_senha(make_browser, browser, google, monkeypatch, admin):
    fake_identity(monkeypatch)
    google_user = make_browser()
    headers, query = start_flow(google_user)
    no_redirect(google_user, f"{CALLBACK}?code=abc&state={query['state'][0]}")
    assert google_user.call("GET", "/api/auth/me")[1]["student"]["isAdmin"] is False       # o admin já existia
    attacker = make_browser()
    attacker.me()
    assert attacker.call("POST", "/api/auth/check", {"email": "gina@exemplo.com"})[1] == {
        "exists": True, "firstUser": False, "needsSetup": False}
    assert attacker.call("POST", "/api/auth/register", {"email": "gina@exemplo.com", "name": "X", "password": PASSWORD,
                                                        "passwordConfirm": PASSWORD})[0] == 409
    assert attacker.call("POST", "/api/auth/login", {"email": "gina@exemplo.com", "password": "oauth$google"})[0] == 401
    assert attacker.call("POST", "/api/auth/login", {"email": "gina@exemplo.com", "password": ""})[0] == 401


def test_conta_existente_com_senha_entra_pelo_google_sem_trocar_a_senha(make_browser, google, monkeypatch, db):
    make_browser().register("gina@exemplo.com", "Gina Antiga")
    before = db.find_student("gina@exemplo.com")["password_hash"]
    fake_identity(monkeypatch, name="Outro Nome")
    b = make_browser()
    headers, query = start_flow(b)
    assert no_redirect(b, f"{CALLBACK}?code=abc&state={query['state'][0]}")[0] == 302
    me = b.call("GET", "/api/auth/me")[1]["student"]
    assert me["email"] == "gina@exemplo.com" and me["name"] == "Gina Antiga"
    assert db.find_student("gina@exemplo.com")["password_hash"] == before
    assert make_browser().login("gina@exemplo.com")[0] == 200                           # a senha continua valendo


def test_conta_antiga_sem_senha_deixa_de_ser_reivindicavel_depois_do_google(make_browser, google, monkeypatch, db):
    db.run("INSERT INTO students(email, name, password_hash, created_at) VALUES('velha@exemplo.com','','','2026-01-01')")
    fake_identity(monkeypatch, email="velha@exemplo.com", name="Velha")
    b = make_browser()
    headers, query = start_flow(b)
    no_redirect(b, f"{CALLBACK}?code=abc&state={query['state'][0]}")
    row = db.find_student("velha@exemplo.com")
    assert row["password_hash"] == oauth.UNUSABLE_HASH and row["name"] == "Velha"


def test_state_errado_ausente_ou_adulterado_e_recusado(browser, google, monkeypatch, db):
    fake_identity(monkeypatch)
    headers, query = start_flow(browser)
    state = query["state"][0]
    for path in (f"{CALLBACK}?code=abc&state=errado", f"{CALLBACK}?code=abc", f"{CALLBACK}?state={state}&code=",
                 f"{CALLBACK}"):
        status, h = no_redirect(browser, path)
        assert status == 302 and h["Location"].startswith("/?oauth_error="), path
    assert browser.call("GET", "/api/auth/me")[1]["student"] is None
    assert db.count_students() == 0


def test_callback_sem_passar_pelo_inicio_ou_com_cookie_de_outro_navegador(make_browser, google, monkeypatch, db):
    fake_identity(monkeypatch)
    attacker, victim = make_browser(), make_browser()
    a_headers, a_query = start_flow(attacker)                                        # o atacante inicia o fluxo dele
    status, h = no_redirect(victim, f"{CALLBACK}?code=abc&state={a_query['state'][0]}")        # e faz a vítima abrir o link
    assert h["Location"] == "/?oauth_error=invalid_state"                            # a vítima não tem o cookie assinado
    assert victim.call("GET", "/api/auth/me")[1]["student"] is None


def test_cookie_do_fluxo_adulterado_ou_vencido_nao_vale(browser, google, monkeypatch, server):
    fake_identity(monkeypatch)
    flow = oauth.new_flow()
    secret = server.app.secret
    good = oauth.sign_flow(flow, secret)
    browser.cookies["kstudy_oauth"] = good[:-3] + ("aaa" if not good.endswith("aaa") else "bbb")
    assert no_redirect(browser, f"{CALLBACK}?code=abc&state={flow['state']}")[1]["Location"].endswith("invalid_state")
    browser.cookies["kstudy_oauth"] = oauth.sign_flow(flow, secret, now=time.time() - 3600)
    assert no_redirect(browser, f"{CALLBACK}?code=abc&state={flow['state']}")[1]["Location"].endswith("invalid_state")
    browser.cookies["kstudy_oauth"] = oauth.sign_flow(flow, "outro-segredo")
    assert no_redirect(browser, f"{CALLBACK}?code=abc&state={flow['state']}")[1]["Location"].endswith("invalid_state")
    browser.cookies["kstudy_oauth"] = good
    assert no_redirect(browser, f"{CALLBACK}?code=abc&state={flow['state']}")[1]["Location"] == "/"       # o bom funciona


def test_o_estado_e_de_uso_unico_no_navegador(browser, google, monkeypatch):
    fake_identity(monkeypatch)
    headers, query = start_flow(browser)
    path = f"{CALLBACK}?code=abc&state={query['state'][0]}"
    assert no_redirect(browser, path)[1]["Location"] == "/"
    assert "kstudy_oauth" not in browser.cookies                                       # o cookie do fluxo foi apagado
    assert no_redirect(browser, path)[1]["Location"].endswith("invalid_state")


@pytest.mark.parametrize("error", ["failed", "unverified", "invalid_state"])
def test_erros_do_google_viram_mensagem_fixa_sem_criar_conta(browser, google, monkeypatch, db, error):
    fake_identity(monkeypatch, error=error)
    headers, query = start_flow(browser)
    status, h = no_redirect(browser, f"{CALLBACK}?code=abc&state={query['state'][0]}")
    assert h["Location"] == f"/?oauth_error={error}"
    assert db.count_students() == 0 and browser.call("GET", "/api/auth/me")[1]["student"] is None
    assert db.one("SELECT COUNT(*) AS n FROM audit_log WHERE action='login_oauth_failed'")["n"] == 1


def test_usuario_cancelou_no_google(browser, google, monkeypatch):
    fake_identity(monkeypatch)
    headers, query = start_flow(browser)
    status, h = no_redirect(browser, f"{CALLBACK}?error=access_denied&state={query['state'][0]}")
    assert h["Location"] == "/?oauth_error=denied"


def test_limite_de_falhas_por_endereco_vale_para_o_google(browser, google, monkeypatch):
    fake_identity(monkeypatch, error="failed")
    for _ in range(security.FAILS_PER_IP):
        headers, query = start_flow(browser)
        no_redirect(browser, f"{CALLBACK}?code=abc&state={query['state'][0]}")
    headers, query = start_flow(browser)
    assert no_redirect(browser, f"{CALLBACK}?code=abc&state={query['state'][0]}")[1]["Location"] == "/?oauth_error=too_many"


def test_mensagem_de_erro_nao_reflete_texto_da_url(browser, google):
    status, h = no_redirect(browser, f"{CALLBACK}?error=<script>alert(1)</script>&state=x")
    assert "<" not in h["Location"] and h["Location"] == "/?oauth_error=invalid_state"


# ---- validação do id_token ----

def claims(**over):
    base = {"aud": "cid", "iss": "https://accounts.google.com", "exp": time.time() + 600, "nonce": "n1", "email": "a@x.co",
            "email_verified": True, "name": "A"}
    base.update(over)
    return base


def test_validate_claims_aceita_o_bom_e_recusa_os_ruins():
    assert oauth.validate_claims(claims(), "cid", "n1") == {"email": "a@x.co", "name": "A"}
    assert oauth.validate_claims(claims(iss="accounts.google.com", aud=["cid", "outro"]), "cid", "n1")["email"] == "a@x.co"
    bad = {"aud": claims(aud="outro"), "iss": claims(iss="https://evil.example.com"), "exp": claims(exp=time.time() - 5),
           "sem exp": {k: v for k, v in claims().items() if k != "exp"}, "sem email": claims(email=""),
           "nonce": claims(nonce="outro"), "não verificado": claims(email_verified=False), "verificado como texto": claims(email_verified="false")}
    for name, c in bad.items():
        with pytest.raises(oauth.OAuthError):
            oauth.validate_claims(c, "cid", "n1")
    with pytest.raises(oauth.OAuthError) as exc:
        oauth.validate_claims(claims(email_verified=False), "cid", "n1")
    assert exc.value.code == "unverified"


def test_exchange_code_nao_vaza_erro_de_rede(monkeypatch):
    def boom(*a, **k):
        raise OSError("sem rede")
    monkeypatch.setattr(oauth.urllib.request, "urlopen", boom)
    with pytest.raises(oauth.OAuthError) as exc:
        oauth.exchange_code({"client_id": "c", "client_secret": "s"}, "code", "http://x/cb", oauth.new_flow())
    assert exc.value.code == "failed"


def test_exchange_code_fala_so_com_o_endereco_fixo_do_google(monkeypatch):
    seen = {}

    class Fake:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n=-1):
            payload = oauth._b64(json.dumps(claims()).encode())
            return json.dumps({"id_token": f"x.{payload}.y"}).encode()

    def fake_open(request, timeout=0):
        seen["url"], seen["data"] = request.full_url, urllib.parse.parse_qs(request.data.decode())
        return Fake()

    monkeypatch.setattr(oauth.urllib.request, "urlopen", fake_open)
    flow = {"state": "s", "nonce": "n1", "verifier": "v" * 50}
    out = oauth.exchange_code({"client_id": "cid", "client_secret": "sec"}, "o-codigo", "http://localhost:8765" + CALLBACK, flow)
    assert out["email"] == "a@x.co" and seen["url"] == oauth.TOKEN_URL
    assert seen["data"]["code_verifier"] == ["v" * 50] and seen["data"]["grant_type"] == ["authorization_code"]
    assert seen["data"]["redirect_uri"] == ["http://localhost:8765" + CALLBACK]


# ---- .env ----

def test_env_novo_traz_as_variaveis_vazias_e_o_comentario_sem_redirect_uri(tmp_path):
    env = tmp_path / ".env"
    security.ensure_secret(env)
    text = env.read_text(encoding="utf-8")
    assert "GOOGLE_CLIENT_ID=\n" in text and "GOOGLE_CLIENT_SECRET=\n" in text
    assert "/auth/oauth/google/callback" in text and "K_STUDY_SECRET=" in text
    assert "REDIRECT" not in text.upper().replace("REDIRECIONAMENTO", "")                # o retorno é fixo: não é variável
    values = security.parse_env(text)
    assert values["GOOGLE_CLIENT_ID"] == "" and values["GOOGLE_CLIENT_SECRET"] == "" and len(values["K_STUDY_SECRET"]) == 64
    assert oauth.google_config(values) is None


def test_env_existente_ganha_as_variaveis_sem_perder_o_resto(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OUTRA=1\n", encoding="utf-8")
    security.ensure_secret(env)
    values = security.parse_env(env.read_text(encoding="utf-8"))
    assert values["OUTRA"] == "1" and values["GOOGLE_CLIENT_ID"] == ""
    monkeypatch.delenv("K_STUDY_SECRET")
    security.ensure_secret(env)                                                          # idempotente: não duplica
    assert env.read_text(encoding="utf-8").count("GOOGLE_CLIENT_ID") == 1 + env.read_text(encoding="utf-8").count("# GOOGLE")


def test_env_example_existe_e_nao_tem_redirect_uri():
    from pathlib import Path
    text = (Path(__file__).resolve().parent.parent / ".env.example").read_text(encoding="utf-8")
    values = security.parse_env(text)
    assert values["GOOGLE_CLIENT_ID"] == "" and values["GOOGLE_CLIENT_SECRET"] == ""
    assert "/auth/oauth/google/callback" in text
    assert not any("REDIRECT" in key.upper() for key in values)
    assert "K_STUDY_SECRET" not in values                                                # nunca um segredo de exemplo
