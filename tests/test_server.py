import json

from conftest import Browser, start
from k_study.server import make_server

TRAIL = "/api/trails/demo"
ITEM = f"{TRAIL}/blocks/block-1/items"


def test_lista_de_trilhas_e_manifesto(student):
    status, trails = student.call("GET", "/api/trails")
    assert status == 200 and len(trails) == 1
    t = trails[0]
    assert t["slug"] == "demo" and t["title"] == "Demo" and t["tags"] == ["teste"] and t["cover"] is None
    assert t["blocks"] == 1 and t["items"] == 3 and t["requiredItems"] == 2 and t["done"] == 0
    status, manifest = student.call("GET", TRAIL)
    assert status == 200 and manifest["id"] == "demo" and manifest["blocks"][0]["id"] == "block-1"
    assert student.call("GET", "/api/trails/nao-existe")[0] == 404


def test_conteudo_por_ids(student):
    status, raw = student.call("GET", f"{ITEM}/r/content")
    assert status == 200 and raw.decode("utf-8").startswith("# Olá")
    status, block = student.call("GET", f"{TRAIL}/blocks/block-1")
    assert status == 200 and block["id"] == "block-1"
    status, questions = student.call("GET", f"{ITEM}/q/content")
    assert status == 200 and questions["questions"][0]["id"] == "q01"
    status, transcript = student.call("GET", f"{ITEM}/v/transcript")
    assert status == 200 and transcript["segments"][0][1] == "oi"
    assert student.call("GET", f"{ITEM}/v/content")[0] == 404          # vídeo não tem arquivo de aula
    assert student.call("GET", f"{ITEM}/r/transcript")[0] == 404
    assert student.call("GET", f"{ITEM}/nada/content")[0] == 404
    assert student.call("GET", f"{TRAIL}/blocks/nada")[0] == 404
    assert student.raw("GET", f"{ITEM}/r/content")[2]["Content-Type"].startswith("text/markdown")


def test_conteudo_exige_login(browser):
    for path in (TRAIL, f"{ITEM}/r/content", f"{TRAIL}/blocks/block-1", "/api/trails", f"{TRAIL}/cover",
                 f"{TRAIL}/figures/x.png"):
        status, err = browser.call("GET", path)
        assert status == 401 and err["error"] == "login_required", path


def test_figuras_so_da_lista_permitida(student, trail_dir, content, db):
    (trail_dir / "figures").mkdir(exist_ok=True)
    (trail_dir / "figures" / "fig.png").write_bytes(b"\x89PNG-dados")
    (trail_dir / "figures" / "script.js").write_text("alert(1)", encoding="utf-8")
    (content / "segredo.txt").write_text("segredo", encoding="utf-8")
    from k_study.indexer import sync
    sync(content, db, force=True)
    status, raw, headers = student.raw("GET", f"{TRAIL}/figures/fig.png")
    assert status == 200 and raw == b"\x89PNG-dados" and headers["Content-Type"] == "image/png"
    for name in ("script.js", "nao-existe.png", "..%2fsegredo.txt", "%2e%2e", "a%2fb.png", "fig.png%00"):
        assert student.call("GET", f"{TRAIL}/figures/{name}")[0] in (400, 404), name


def test_nenhuma_rota_serve_arquivo_por_caminho(student, content):
    (content / "segredo.txt").write_text("segredo", encoding="utf-8")
    (content / "demo" / "interno.txt").write_text("dentro", encoding="utf-8")
    for path in ("/api/trails/demo/files/block-1/read.md", "/api/trails/demo/files/trail.json",
                 "/api/trails/demo/files/../../segredo.txt", "/api/trails/demo/files/%2e%2e/%2e%2e/segredo.txt",
                 "/api/trails/demo/files/block-1/../interno.txt", "/api/trails/..%2fdemo/blocks/block-1",
                 "/api/trails/demo/blocks/%2e%2e%2fblock-1/items/r/content",
                 "/api/trails/demo/blocks/block-1/items/..%2f..%2fsegredo/content",
                 "/api/trails/demo/blocks/block-1/items/r%00/content", "/api/trails/demo/blocks/block-1/items/read.md/content"):
        status, body = student.call("GET", path)
        assert status in (400, 404), path
        assert b"segredo" not in (body if isinstance(body, bytes) else json.dumps(body).encode()), path
        assert b"dentro" not in (body if isinstance(body, bytes) else json.dumps(body).encode()), path


def test_arquivo_fora_da_lista_nao_sai_mesmo_com_item_apontando_para_ele(student, trail_dir, content, db):
    """Um block.json que aponta para fora da pasta ou para extensão não permitida nunca entra na lista."""
    (content / "segredo.md").write_text("segredo", encoding="utf-8")
    (trail_dir / "block-1" / "x.sh").write_text("echo", encoding="utf-8")
    doc = json.loads((trail_dir / "block-1" / "block.json").read_text(encoding="utf-8"))
    doc["sections"][0]["items"] += [{"id": "fora", "type": "markdown", "title": "F", "path": "../../segredo.md"},
                                    {"id": "sh", "type": "markdown", "title": "S", "path": "x.sh"}]
    (trail_dir / "block-1" / "block.json").write_text(json.dumps(doc), encoding="utf-8")
    from k_study.indexer import sync
    sync(content, db, force=True)
    for item in ("fora", "sh"):
        assert student.call("GET", f"{ITEM}/{item}/content")[0] == 404


def test_interface_estatica_e_rotas_desconhecidas(browser):
    status, data, headers = browser.raw("GET", "/")
    assert status == 200 and headers["Cache-Control"] == "no-store"
    status, err = browser.call("GET", "/api/nada")
    assert status == 404 and err["error"] == "not_found" and err["message"]
    assert browser.call("GET", "/../pyproject.toml")[0] == 404
    assert browser.call("GET", "/%2e%2e/%2e%2e/pyproject.toml")[0] == 404
    assert browser.call("GET", "/.env")[0] == 404


def test_cabecalhos_de_seguranca_em_todas_as_respostas(browser, student):
    for path in ("/", "/api/auth/me", "/api/nada"):
        headers = browser.raw("GET", path)[2]
        assert "default-src 'self'" in headers["Content-Security-Policy"] and "object-src 'none'" in headers["Content-Security-Policy"]
        assert headers["X-Content-Type-Options"] == "nosniff" and headers["X-Frame-Options"] == "DENY"
        assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin" and headers["Cross-Origin-Resource-Policy"] == "same-origin"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert browser.raw("GET", "/api/auth/me")[2]["Cache-Control"] == "no-store"
    assert "Python" not in browser.raw("GET", "/")[2].get("Server", "")


def test_json_invalido_corpo_grande_e_content_type(student):
    path = f"{TRAIL}/progress/items/block-1/r"
    status, err = student.call("PUT", path, "{nao e json")
    assert status == 400 and err["error"] == "invalid_json" and err["message"]
    assert student.call("PUT", path, "[1]")[0] == 400
    assert student.call("POST", "/api/auth/check", "x" * 1_100_000)[0] == 413
    status, err = student.call("PUT", path, '{"done": true}', headers={"Content-Type": "text/plain"})
    assert status == 415 and err["error"] == "unsupported_media_type"


def test_origem_diferente_do_host_e_recusada(student):
    path = f"{TRAIL}/progress/items/block-1/r"
    status, err = student.call("PUT", path, {"done": True}, headers={"Origin": "http://evil.example.com"})
    assert status == 403 and err["error"] == "forbidden_origin"
    host = f"localhost:{student.port}"
    status, _ = student.call("PUT", path, {"done": True}, headers={"Origin": f"http://{host}"}, host=host)
    assert status == 200


def test_cabecalho_host_falso_e_recusado(content, db):
    srv = make_server(content, db, port=0)
    port = start(srv)
    try:
        b = Browser(port)
        for host, expected in ((f"localhost:{port}", 200), (f"127.0.0.1:{port}", 200), (f"[::1]:{port}", 200),
                               ("evil.example.com", 403), (f"evil.example.com:{port}", 403),
                               (f"192.168.0.10:{port}", 403)):
            assert b.raw("GET", "/api/auth/me", host=host)[0] == expected, host
        assert json.loads(b.raw("GET", "/api/auth/me", host="evil.example.com")[1])["error"] == "forbidden_host"
        assert srv.server_address[0] == "127.0.0.1"
    finally:
        srv.shutdown()


def test_modo_lan_aceita_hosts_ip_mas_nao_nomes(content, db):
    srv = make_server(content, db, port=0, lan=True)
    port = start(srv)
    try:
        b = Browser(port)
        assert srv.server_address[0] == "0.0.0.0"
        for host, expected in ((f"192.168.0.10:{port}", 200), (f"[fe80::1]:{port}", 200), (f"localhost:{port}", 200),
                               ("evil.example.com", 403)):
            assert b.raw("GET", "/api/auth/me", host=host)[0] == expected, host
    finally:
        srv.shutdown()


def test_modo_lan_recusa_cliente_de_fora_da_rede_privada(content, db, monkeypatch):
    from k_study import server as server_module
    srv = make_server(content, db, port=0, lan=True)
    port = start(srv)
    try:
        monkeypatch.setattr(server_module.Handler, "_client_ok", lambda self: False)
        status, data, _ = Browser(port).raw("GET", "/api/auth/me", host=f"localhost:{port}")
        assert status == 403 and json.loads(data)["error"] == "forbidden_client"
    finally:
        srv.shutdown()


def test_erro_interno_nao_vaza_traceback(student, monkeypatch):
    from k_study import server as server_module

    def quebra(self):
        raise RuntimeError("segredo-interno")

    monkeypatch.setattr(server_module.Handler, "_serve_trail_manifest", quebra)
    status, data, _ = student.raw("GET", TRAIL)
    assert status == 500 and b"segredo-interno" not in data and b"Traceback" not in data
    assert json.loads(data)["error"] == "internal_error"


def test_trilha_inativa_some_para_alunos_e_o_progresso_fica(admin, student, db):
    student.call("PUT", f"{TRAIL}/progress/items/block-1/r", {"done": True})
    status, body = admin.call("POST", "/api/admin/trails/demo/active", {"active": False})
    assert status == 200 and body == {"slug": "demo", "active": False}
    assert student.call("GET", "/api/trails")[1] == []
    for path in (TRAIL, f"{ITEM}/r/content", f"{TRAIL}/progress", f"{TRAIL}/blocks/block-1"):
        assert student.call("GET", path)[0] == 404, path
    assert student.call("PUT", f"{TRAIL}/progress/items/block-1/r", {"done": True})[0] == 404
    assert admin.call("GET", f"{ITEM}/r/content")[0] == 200            # o admin ainda abre
    admin.call("POST", "/api/admin/trails/demo/active", {"active": True})
    assert student.call("GET", f"{TRAIL}/progress")[1]["items"]["block-1/r"]["done"] is True
    assert db.one("SELECT COUNT(*) AS n FROM audit_log WHERE action='trail_active'")["n"] == 2


def test_reindexar_preserva_active(admin, student, content, db):
    admin.call("POST", "/api/admin/trails/demo/active", {"active": False})
    from k_study.indexer import sync
    sync(content, db, force=True)
    assert db.trail_active("demo") is False


def test_rotas_admin_exigem_login_e_admin(browser, student, admin):
    for method, path, body in (("GET", "/api/admin/overview", None), ("GET", "/api/admin/students", None),
                               ("GET", "/api/admin/trails", None), ("GET", "/api/admin/specs.zip", None),
                               ("POST", "/api/admin/trails/demo/active", {"active": False})):
        assert browser.call(method, path, body)[0] in (401, 403), path
        status, err = student.call(method, path, body)
        assert status == 403 and err["error"] == "forbidden", path
    status, _, headers = browser.raw("GET", "/admin/")
    assert status == 302 and headers["Location"] == "/"                # sem sessão: manda para a entrada
    assert student.call("GET", "/admin/")[0] == 403 and student.call("GET", "/admin/app.js")[0] == 403
    assert admin.call("GET", "/api/admin/overview")[0] == 200
    status, page, headers = admin.raw("GET", "/admin/")
    assert status == 200 and b"Administra" in page and "text/html" in headers["Content-Type"]
    assert admin.raw("GET", "/admin")[2]["Location"] == "/admin/"
    assert admin.raw("GET", "/admin/app.js")[0] == 200 and admin.raw("GET", "/admin/theme.js")[0] == 200
    assert admin.raw("GET", "/admin/..%2f..%2fpyproject.toml")[0] == 404


def test_importar_zip_sem_modulo_ou_com_pacote_falso(admin, student, monkeypatch, content):
    """A rota usa packages.import_trail_zip e traduz PackageError em 400 invalid_package."""
    import sys
    import types

    class PackageError(Exception):
        def __init__(self, problems):
            super().__init__("; ".join(problems))
            self.problems = problems

    fake = types.ModuleType("k_study.packages")
    fake.PackageError = PackageError

    def import_trail_zip(content_dir, data, replace=False):
        if data == b"ruim":
            raise PackageError(["falta o trail.json"])
        return {"slug": "demo", "warnings": ["aviso"], "replaced": replace}

    fake.import_trail_zip = import_trail_zip
    fake.build_specs_zip = lambda root: b"PKzip"
    monkeypatch.setitem(sys.modules, "k_study.packages", fake)
    import k_study
    monkeypatch.setattr(k_study, "packages", fake, raising=False)

    headers = {"Content-Type": "application/zip"}
    status, body = admin.call("POST", "/api/admin/trails/import?replace=1", b"zipdados", headers=headers)
    assert status == 200 and body == {"slug": "demo", "warnings": ["aviso"], "replaced": True}
    status, body = admin.call("POST", "/api/admin/trails/import", b"ruim", headers=headers)
    assert status == 400 and body["error"] == "invalid_package" and body["problems"] == ["falta o trail.json"]
    assert student.call("POST", "/api/admin/trails/import", b"zipdados", headers=headers)[0] == 403
    assert admin.call("POST", "/api/admin/trails/import", b"zipdados", headers=headers, csrf=False)[0] == 403
    assert admin.call("POST", "/api/admin/trails/import", b"zipdados")[0] == 415       # Content-Type JSON
    status, data, h = admin.raw("GET", "/api/admin/specs.zip")
    assert status == 200 and data == b"PKzip" and "attachment" in h["Content-Disposition"]
