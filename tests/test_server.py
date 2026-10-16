import json

from conftest import Browser, start
from k_study.server import make_server


def test_lista_de_trilhas_e_manifesto(browser):
    status, trails = browser.call("GET", "/api/trails")
    assert status == 200 and len(trails) == 1
    t = trails[0]
    assert t["slug"] == "demo" and t["title"] == "Demo" and t["tags"] == ["teste"]
    assert t["blocks"] == 1 and t["items"] == 3 and t["requiredItems"] == 2 and t["done"] == 0
    status, manifest = browser.call("GET", "/api/trails/demo")
    assert status == 200 and manifest["id"] == "demo" and manifest["blocks"][0]["id"] == "block-1"
    assert browser.call("GET", "/api/trails/nao-existe")[0] == 404


def test_arquivos_da_trilha_sao_servidos(browser):
    status, raw = browser.call("GET", "/api/trails/demo/files/block-1/read.md")
    assert status == 200 and raw.decode("utf-8").startswith("# Olá")
    status, block = browser.call("GET", "/api/trails/demo/files/block-1/block.json")
    assert status == 200 and block["id"] == "block-1"
    assert browser.call("GET", "/api/trails/demo/files/transcripts/aaaaaaaaaaa.json")[0] == 200
    assert browser.call("GET", "/api/trails/demo/files/block-1/nao-existe.md")[0] == 404


def test_arquivos_nao_escapam_da_pasta_da_trilha(browser, content):
    (content / "segredo.txt").write_text("segredo", encoding="utf-8")
    (content / "demo" / "interno.txt").write_text("dentro", encoding="utf-8")
    for path in ("/api/trails/demo/files/../../segredo.txt",
                 "/api/trails/demo/files/%2e%2e/%2e%2e/segredo.txt",
                 "/api/trails/demo/files/..%2f..%2fsegredo.txt",
                 "/api/trails/demo/files/block-1/../../../segredo.txt",
                 "/api/trails/..%2fdemo/files/block-1/read.md",
                 "/api/trails/demo/files/%00"):
        status, body = browser.call("GET", path)
        assert status in (400, 404), path
        assert b"segredo" not in (body if isinstance(body, bytes) else json.dumps(body).encode()), path
    # um caminho com .. que continua dentro da pasta da trilha é permitido
    assert browser.call("GET", "/api/trails/demo/files/block-1/../interno.txt")[1] == b"dentro"


def test_interface_estatica_e_rotas_desconhecidas(browser):
    assert browser.call("GET", "/")[0] == 200
    status, err = browser.call("GET", "/api/nada")
    assert status == 404 and err["error"] == "not_found" and err["message"]
    assert browser.call("GET", "/../pyproject.toml")[0] == 404
    assert browser.call("GET", "/%2e%2e/%2e%2e/pyproject.toml")[0] == 404
    assert browser.raw("GET", "/")[2]["Cache-Control"] == "no-store"


def test_json_invalido_e_corpo_grande(student):
    status, err = student.call("PUT", "/api/trails/demo/progress/items/block-1/r", "{nao e json")
    assert status == 400 and err["error"] == "invalid_json" and err["message"]
    assert student.call("PUT", "/api/trails/demo/progress/items/block-1/r", "[1]")[0] == 400
    assert student.call("POST", "/api/login", "x" * 1_100_000)[0] == 413


def test_origem_diferente_do_host_e_recusada(student):
    status, err = student.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True},
                               headers={"Origin": "http://evil.example.com"})
    assert status == 403 and err["error"] == "forbidden_origin"
    host = f"localhost:{student.port}"
    status, _ = student.call("PUT", "/api/trails/demo/progress/items/block-1/r", {"done": True},
                             headers={"Origin": f"http://{host}"}, host=host)
    assert status == 200


def test_cabecalho_host_falso_e_recusado(content, db):
    srv = make_server(content, db, port=0)
    port = start(srv)
    try:
        b = Browser(port)
        for host, expected in ((f"localhost:{port}", 200), (f"127.0.0.1:{port}", 200), (f"[::1]:{port}", 200),
                               ("evil.example.com", 403), (f"evil.example.com:{port}", 403),
                               (f"192.168.0.10:{port}", 403)):
            assert b.raw("GET", "/api/trails", host=host)[0] == expected, host
        assert json.loads(b.raw("GET", "/api/trails", host="evil.example.com")[1])["error"] == "forbidden_host"
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
            assert b.raw("GET", "/api/trails", host=host)[0] == expected, host
    finally:
        srv.shutdown()


def test_modo_lan_recusa_cliente_de_fora_da_rede_privada(content, db, monkeypatch):
    from k_study import server as server_module
    srv = make_server(content, db, port=0, lan=True)
    port = start(srv)
    try:
        monkeypatch.setattr(server_module.Handler, "_client_ok", lambda self: False)
        status, data, _ = Browser(port).raw("GET", "/api/trails", host=f"localhost:{port}")
        assert status == 403 and json.loads(data)["error"] == "forbidden_client"
    finally:
        srv.shutdown()
