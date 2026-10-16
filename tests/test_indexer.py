import json
import os
import shutil

from conftest import make_trail
from k_study.indexer import estimate_minutes, sync


def test_sync_indexa_trilhas_blocos_e_itens(content, db):
    result = sync(content, db)
    assert result["indexed"] == ["demo"] and result["removed"] == [] and result["skipped"] == {}
    trail = db.one("SELECT * FROM trails WHERE slug='demo'")
    assert trail["title"] == "Demo" and json.loads(trail["tags"]) == ["teste"] and trail["synced_at"]
    assert [tuple(r) for r in db.query("SELECT block_id, title, position, file FROM blocks")] == [
        ("block-1", "B", 0, "block-1/block.json")]
    items = {r["item_id"]: r for r in db.query("SELECT * FROM items ORDER BY position")}
    assert list(items) == ["r", "v", "q"] and [i["position"] for i in items.values()] == [0, 1, 2]
    assert items["r"]["type"] == "markdown" and items["r"]["section"] == "s" and items["r"]["path"] == "block-1/read.md"
    assert items["v"]["optional"] == 1 and items["r"]["optional"] == 0
    assert items["v"]["minutes"] == 1.5                      # um trecho de 90 s
    assert items["r"]["minutes"] == 2                        # ~362 palavras / 180
    assert items["q"]["minutes"] is None


def test_estimativa_de_minutos(tmp_path):
    (tmp_path / "a.md").write_text("palavra " * 18, encoding="utf-8")
    assert estimate_minutes({"type": "markdown", "path": "a.md"}, tmp_path) == 1       # mínimo de 1 min
    assert estimate_minutes({"type": "markdown", "path": "faltando.md"}, tmp_path) is None
    assert estimate_minutes({"type": "video", "clips": [{"start": 0, "end": 60}, {"start": 100, "end": 220}]}, tmp_path) == 3
    assert estimate_minutes({"type": "video", "start": 0, "end": 120}, tmp_path) == 2
    assert estimate_minutes({"type": "video", "duration": "10 min"}, tmp_path) == 10
    assert estimate_minutes({"type": "link"}, tmp_path) is None


def test_sync_e_barato_e_reindexa_quando_o_manifesto_muda(content, db):
    sync(content, db)
    assert sync(content, db)["indexed"] == []                    # nada mudou
    block = content / "demo" / "block-1" / "block.json"
    doc = json.loads(block.read_text(encoding="utf-8"))
    doc["sections"][0]["items"].append({"id": "novo", "type": "link", "title": "Novo", "url": "https://x.org"})
    block.write_text(json.dumps(doc), encoding="utf-8")
    later = block.stat().st_mtime + 5
    os.utime(block, (later, later))
    assert sync(content, db)["indexed"] == ["demo"]
    assert db.has_item("demo", "block-1", "novo")
    trail = content / "demo" / "trail.json"
    doc = json.loads(trail.read_text(encoding="utf-8"))
    doc["title"] = "Outro título"
    trail.write_text(json.dumps(doc), encoding="utf-8")
    later = trail.stat().st_mtime + 5
    os.utime(trail, (later, later))
    assert sync(content, db)["indexed"] == ["demo"]
    assert db.one("SELECT title FROM trails")["title"] == "Outro título"
    assert sync(content, db, force=True)["indexed"] == ["demo"]


def test_trilha_removida_sai_do_indice_mas_progresso_fica(content, db):
    make_trail(content, "outra", "Outra")
    sync(content, db)
    student, _ = db.create_student("ana@exemplo.com", "Ana", "x")
    db.set_done(student["id"], "outra", "block-1", "r", True)
    db.set_answer(student["id"], "outra", "block-1", "q", "q01", ["a"], True)
    db.set_note(student["id"], "outra", "block-1", "r", "nota")
    visit = db.open_visit(student["id"], "outra", "block-1", "r")
    shutil.rmtree(content / "outra")
    result = sync(content, db)
    assert result["removed"] == ["outra"]
    assert [t["slug"] for t in db.list_trails()] == ["demo"]
    assert db.one("SELECT COUNT(*) AS n FROM items WHERE trail='outra'")["n"] == 0
    state = db.progress_state(student["id"], "outra")
    assert state["items"]["block-1/r"]["done"] and state["answers"] and state["notes"]
    assert db.one("SELECT id FROM visits WHERE id=?", (visit,)) is not None
    make_trail(content, "outra", "Outra")                         # se voltar, o aluno recupera
    sync(content, db)
    assert db.progress_state(student["id"], "outra")["items"]["block-1/r"]["done"]


def test_trilhas_invalidas_sao_ignoradas_sem_derrubar_o_resto(content, db):
    (content / "quebrada").mkdir()
    (content / "quebrada" / "trail.json").write_text("{nao e json", encoding="utf-8")
    make_trail(content, "id-errado")
    doc = json.loads((content / "id-errado" / "trail.json").read_text(encoding="utf-8"))
    doc["id"] = "outro"
    (content / "id-errado" / "trail.json").write_text(json.dumps(doc), encoding="utf-8")
    (content / "Nome Ruim").mkdir()
    (content / "Nome Ruim" / "trail.json").write_text("{}", encoding="utf-8")
    result = sync(content, db)
    assert result["indexed"] == ["demo"] and set(result["skipped"]) == {"quebrada", "id-errado"}
    assert [t["slug"] for t in db.list_trails()] == ["demo"]


def test_bloco_ausente_nao_quebra_o_indice(content, db):
    (content / "demo" / "block-1" / "block.json").unlink()
    sync(content, db)
    assert db.one("SELECT COUNT(*) AS n FROM blocks")["n"] == 1
    assert db.one("SELECT COUNT(*) AS n FROM items")["n"] == 0


def test_pasta_de_conteudo_inexistente(tmp_path, db):
    assert sync(tmp_path / "nao-existe", db) == {"indexed": [], "removed": [], "skipped": {}}


def test_servidor_enxerga_trilha_nova_sem_reiniciar(student, content):
    browser = student
    assert len(browser.call("GET", "/api/trails")[1]) == 1
    make_trail(content, "nova", "Nova")
    assert [t["slug"] for t in browser.call("GET", "/api/trails")[1]] == ["demo", "nova"]
    shutil.rmtree(content / "nova")
    assert [t["slug"] for t in browser.call("GET", "/api/trails")[1]] == ["demo"]


def test_assets_capa_transcricao_e_figuras(content, db):
    from conftest import write_json
    folder = content / "demo"
    (folder / "figures").mkdir()
    (folder / "figures" / "a.png").write_bytes(b"png")
    (folder / "figures" / "mau.svg").write_text("<svg/>", encoding="utf-8")
    (folder / "capa.webp").write_bytes(b"webp")
    manifest = json.loads((folder / "trail.json").read_text(encoding="utf-8"))
    manifest["cover"] = "capa.webp"
    write_json(folder / "trail.json", manifest)
    sync(content, db)
    assets = {r["path"]: r["kind"] for r in db.query("SELECT path, kind FROM assets WHERE trail='demo'")}
    assert assets == {"capa.webp": "cover", "figures/a.png": "figure", "block-1/block.json": "block",
                      "block-1/read.md": "item", "block-1/q.json": "item",
                      "transcripts/aaaaaaaaaaa.json": "transcript"}
    assert db.one("SELECT cover FROM trails")["cover"] == "capa.webp"
    assert db.one("SELECT transcript FROM items WHERE item_id='v'")["transcript"] == "transcripts/aaaaaaaaaaa.json"
    assert db.list_trails()[0]["cover"] == "/api/trails/demo/cover"


def test_capa_invalida_e_ignorada(content, db):
    from conftest import write_json
    folder = content / "demo"
    (content / "fora.png").write_bytes(b"x")
    manifest = json.loads((folder / "trail.json").read_text(encoding="utf-8"))
    manifest["cover"] = "../fora.png"
    write_json(folder / "trail.json", manifest)
    sync(content, db)
    assert db.one("SELECT cover FROM trails")["cover"] is None
    assert db.one("SELECT COUNT(*) AS n FROM assets WHERE kind='cover'")["n"] == 0
