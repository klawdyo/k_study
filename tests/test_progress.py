from conftest import make_trail

BASE = "/api/trails/demo/progress"


def test_progresso_comeca_vazio(student):
    assert student.call("GET", BASE) == (200, {"items": {}, "answers": {}, "notes": {}})


def test_item_feito_vai_e_volta_e_persiste(student, db):
    status, state = student.call("PUT", f"{BASE}/items/block-1/r", {"done": True})
    assert status == 200 and state["items"]["block-1/r"]["done"] is True and state["items"]["block-1/r"]["at"]
    assert student.call("GET", BASE)[1]["items"]["block-1/r"]["done"] is True
    assert db.one("SELECT done FROM progress")["done"] == 1
    state = student.call("PUT", f"{BASE}/items/block-1/r", {"done": False})[1]
    assert state["items"]["block-1/r"]["done"] is False


def test_respostas_podem_ser_salvas_e_removidas(student):
    status, state = student.call("PUT", f"{BASE}/answers/block-1/q/q01", {"chosen": ["a"], "correct": True})
    assert status == 200
    assert state["answers"]["block-1/q"]["q01"]["chosen"] == ["a"] and state["answers"]["block-1/q"]["q01"]["correct"] is True
    state = student.call("PUT", f"{BASE}/answers/block-1/q/q01", {"chosen": ["b"], "correct": False})[1]
    assert state["answers"]["block-1/q"]["q01"]["chosen"] == ["b"]            # sobrescreve
    status, state = student.call("DELETE", f"{BASE}/answers/block-1/q/q01")
    assert status == 200 and not state["answers"].get("block-1/q")


def test_anotacoes_e_texto_vazio_apaga(student):
    state = student.call("PUT", f"{BASE}/notes/block-1/r", {"text": "lembrar"})[1]
    assert state["notes"]["block-1/r"] == "lembrar"
    state = student.call("PUT", f"{BASE}/notes/block-1/r", {"text": "  "})[1]
    assert "block-1/r" not in state["notes"]


def test_progresso_e_separado_por_aluno(make_browser, admin):
    a, b = make_browser(), make_browser()
    a.register("ana@exemplo.com", "Ana")
    b.register("bia@exemplo.com", "Bia")
    a.call("PUT", f"{BASE}/items/block-1/r", {"done": True})
    a.call("PUT", f"{BASE}/answers/block-1/q/q01", {"chosen": ["a"], "correct": True})
    assert b.call("GET", BASE)[1] == {"items": {}, "answers": {}, "notes": {}}
    b.call("PUT", f"{BASE}/notes/block-1/r", {"text": "da bia"})
    assert "block-1/r" not in a.call("GET", BASE)[1]["notes"]


def test_progresso_e_separado_por_trilha(student, content):
    make_trail(content, "outra", "Outra")
    student.call("PUT", f"{BASE}/items/block-1/r", {"done": True})
    assert student.call("GET", "/api/trails/outra/progress")[1] == {"items": {}, "answers": {}, "notes": {}}
    student.call("PUT", "/api/trails/outra/progress/notes/block-1/q", {"text": "x"})
    assert student.call("GET", BASE)[1]["notes"] == {}
    trails = {t["slug"]: t for t in student.call("GET", "/api/trails")[1]}
    assert trails["demo"]["done"] == 1 and trails["outra"]["done"] == 0


def test_done_conta_toda_aula_e_required_done_so_as_obrigatorias(student):
    student.call("PUT", f"{BASE}/items/block-1/v", {"done": True})              # v é opcional
    t = student.call("GET", "/api/trails")[1][0]
    assert t["done"] == 1 and t["requiredDone"] == 0 and t["items"] == 3
    student.call("PUT", f"{BASE}/items/block-1/r", {"done": True})
    t = student.call("GET", "/api/trails")[1][0]
    assert t["done"] == 2 and t["requiredDone"] == 1


def test_item_ou_trilha_inexistente_e_ids_invalidos(student):
    assert student.call("PUT", f"{BASE}/items/block-1/nao-existe", {"done": True})[1]["error"] == "item_not_found"
    assert student.call("PUT", "/api/trails/nada/progress/items/block-1/r", {"done": True})[0] == 404
    assert student.call("GET", "/api/trails/nada/progress")[0] == 404
    assert student.call("PUT", f"{BASE}/items/block-1/r%20x", {"done": True})[1]["error"] == "invalid_id"
    assert student.call("PUT", f"{BASE}/bogus/block-1/r", {})[0] == 404
    assert student.call("PUT", f"{BASE}/answers/block-1/q/q01", {"chosen": "a"})[1]["error"] == "invalid_chosen"
    assert student.call("PUT", f"{BASE}/notes/block-1/r", {"text": 5})[1]["error"] == "invalid_text"
    assert student.call("PUT", f"{BASE}/notes/block-1/r", {"text": "x" * 60000})[0] == 413


def test_progresso_sobrevive_a_item_que_some_do_conteudo(student, content, db):
    from k_study.indexer import sync
    student.call("PUT", f"{BASE}/items/block-1/r", {"done": True})
    (content / "demo" / "block-1" / "block.json").write_text(
        '{"schema":"block/v2","id":"block-1","title":"B","sections":[]}', encoding="utf-8")
    sync(content, db, force=True)
    assert db.has_item("demo", "block-1", "r") is False
    assert student.call("GET", BASE)[1]["items"]["block-1/r"]["done"] is True       # o progresso ficou
