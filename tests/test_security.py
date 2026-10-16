import os
import stat

from k_study import security


def test_hash_de_senha_formato_verificacao_e_pepper():
    hashed = security.hash_password("senha-segura-1", "segredo-a")
    scheme, n, r, p, salt, digest = hashed.split("$")
    assert (scheme, int(n), int(r), int(p)) == ("scrypt", security.SCRYPT_N, security.SCRYPT_R, security.SCRYPT_P)
    assert security.verify_password("senha-segura-1", hashed, "segredo-a")
    assert not security.verify_password("senha-segura-2", hashed, "segredo-a")
    assert not security.verify_password("senha-segura-1", hashed, "segredo-b")        # outro segredo: não confere
    assert hashed != security.hash_password("senha-segura-1", "segredo-a")             # sal aleatório
    for broken in ("", "x", "scrypt$1$2", "bcrypt$1$1$1$a$b", "scrypt$x$1$1$a$b"):
        assert security.verify_password("senha-segura-1", broken, "segredo-a") is False


def test_parametros_reais_do_contrato():
    assert (2 ** 15, 8, 1) == (security.SCRYPT_N, security.SCRYPT_R, security.SCRYPT_P) or security.SCRYPT_N == 2 ** 10
    assert security.needs_rehash("scrypt$1$8$1$a$b") is True
    assert security.needs_rehash(security.hash_password("senha-segura-1", "s")) is False


def test_politica_de_senha():
    assert security.check_password_policy("12345678") is None
    assert security.check_password_policy("1234567")
    assert security.check_password_policy("x" * 129)
    assert security.check_password_policy("ana@exemplo.com", "ana@exemplo.com")
    assert security.check_password_policy(None)


def test_email_e_nome():
    assert security.normalize_email("  Ana@Exemplo.COM ") == "ana@exemplo.com"
    for bad in ("a@b", "", None, "a@@b.co", "a b@c.co", "a" * 250 + "@x.com", "a@b.c\x00o"):
        assert security.normalize_email(bad) is None, bad
    for hostile in ("<script>@x.co", 'a"b@x.co', "a(b)@x.co", "a,b@x.co", "a;b@x.co", "a\b@x.co", "a@x_<b>.co", "a@[127.0.0.1]"):
        assert security.normalize_email(hostile) is None, hostile
    assert security.normalize_email("josé.o'neil+tag@exemplo.com.br") == "josé.o'neil+tag@exemplo.com.br"
    assert security.normalize_name("  Ana   Maria ") == "Ana Maria"
    assert security.normalize_name("") is None and security.normalize_name("x" * 81) is None
    assert security.normalize_name("a\x07b") is None


def test_env_cria_com_segredo_e_permissao_e_nao_sobrescreve(tmp_path, monkeypatch, capsys):
    env = tmp_path / "sub" / ".env"
    secret = security.ensure_secret(env)
    assert len(secret) == 64 and f"K_STUDY_SECRET={secret}\n" in env.read_text(encoding="utf-8")
    if os.name != "nt":
        assert stat.S_IMODE(env.stat().st_mode) == 0o600
    assert security.ensure_secret(env) == secret                       # idempotente
    assert secret not in capsys.readouterr().out
    monkeypatch.delenv("K_STUDY_SECRET")
    assert security.ensure_secret(env) == secret                       # relido do arquivo


def test_env_nao_sobrescreve_o_ambiente_e_preserva_outras_linhas(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("# comentário\nOUTRA=1\nK_STUDY_SECRET='do-arquivo'\n", encoding="utf-8")
    monkeypatch.setenv("K_STUDY_SECRET", "do-ambiente")
    assert security.ensure_secret(env) == "do-ambiente"
    monkeypatch.delenv("K_STUDY_SECRET")
    monkeypatch.delenv("OUTRA", raising=False)
    security.load_env(env)
    assert os.environ["OUTRA"] == "1" and os.environ["K_STUDY_SECRET"] == "do-arquivo"
    monkeypatch.delenv("OUTRA")
    monkeypatch.delenv("K_STUDY_SECRET")
    env.write_text("OUTRA=1\n", encoding="utf-8")                      # sem a chave: acrescenta, mantém o resto
    new = security.ensure_secret(env)
    text = env.read_text(encoding="utf-8")
    assert text.startswith("OUTRA=1\n") and f"K_STUDY_SECRET={new}" in text
    monkeypatch.delenv("OUTRA", raising=False)


def test_make_server_cria_o_env(tmp_path, content, db):
    from k_study.server import make_server
    env = tmp_path / ".env"
    srv = make_server(content, db, port=0, env_path=env)
    srv.server_close()
    assert env.is_file() and "K_STUDY_SECRET=" in env.read_text(encoding="utf-8")


def test_tokens():
    a = security.pre_token("s", "valor")
    assert a == security.pre_token("s", "valor") and a != security.pre_token("s", "outro") and a != security.pre_token("t", "valor")
    assert security.tokens_equal("x", "x") and not security.tokens_equal("x", "y")
    assert not security.tokens_equal(None, "x") and not security.tokens_equal("", "")
