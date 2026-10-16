OPEN = {"event": "open", "trail": "demo", "block": "block-1", "item": "r"}


def test_open_cria_visita_e_beat_leave_somam_segundos(student, db):
    status, body = student.call("POST", "/api/track", OPEN)
    assert status == 200
    visit = body["visit"]
    assert db.one("SELECT seconds, started_at FROM visits WHERE id=?", (visit,))["seconds"] == 0
    assert student.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 10})[1]["seconds"] == 10
    assert student.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 10})[1]["seconds"] == 20
    assert student.call("POST", "/api/track", {"event": "leave", "visit": visit, "seconds": 3})[1]["seconds"] == 23
    row = db.one("SELECT * FROM visits WHERE id=?", (visit,))
    assert row["seconds"] == 23 and (row["trail"], row["block_id"], row["item_id"]) == ("demo", "block-1", "r")
    assert row["student_id"] == db.one("SELECT id FROM students WHERE email='ana@exemplo.com'")["id"]


def test_limites_de_segundos_por_chamada(student):
    visit = student.call("POST", "/api/track", OPEN)[1]["visit"]
    assert student.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 9999})[1]["seconds"] == 30
    assert student.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 0})[1]["seconds"] == 31
    assert student.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": -50})[1]["seconds"] == 32


def test_teto_por_visita(student, db):
    visit = student.call("POST", "/api/track", OPEN)[1]["visit"]
    db.run("UPDATE visits SET seconds=14395 WHERE id=?", (visit,))
    assert student.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 30})[1]["seconds"] == 14400


def test_visita_de_outro_aluno_e_recusada(make_browser, admin):
    a, b = make_browser(), make_browser()
    a.register("ana@exemplo.com", "Ana")
    b.register("bia@exemplo.com", "Bia")
    visit = a.call("POST", "/api/track", OPEN)[1]["visit"]
    status, err = b.call("POST", "/api/track", {"event": "beat", "visit": visit, "seconds": 10})
    assert status == 404 and err["error"] == "visit_not_found"


def test_eventos_e_campos_invalidos(student):
    assert student.call("POST", "/api/track", {"event": "xyz"})[1]["error"] == "invalid_track"
    assert student.call("POST", "/api/track", {"event": "beat", "visit": "1", "seconds": 5})[0] == 400
    assert student.call("POST", "/api/track", {"event": "beat", "visit": 1, "seconds": "5"})[0] == 400
    assert student.call("POST", "/api/track", {"event": "beat", "visit": True, "seconds": 5})[0] == 400
    assert student.call("POST", "/api/track", {"event": "beat", "visit": 9999, "seconds": 5})[0] == 404
    assert student.call("POST", "/api/track", {**OPEN, "item": "nao-existe"})[1]["error"] == "item_not_found"
    assert student.call("POST", "/api/track", {**OPEN, "trail": "nada"})[0] == 404


def test_sendbeacon_leva_o_csrf_no_corpo(student):
    """navigator.sendBeacon não envia cabeçalhos: o token vai no corpo JSON."""
    visit = student.call("POST", "/api/track", OPEN)[1]["visit"]
    payload = '{"event":"leave","visit":%d,"seconds":4,"csrf":"%s"}' % (visit, student.csrf)
    status, body = student.call("POST", "/api/track", payload, csrf=False)
    assert status == 200 and body["seconds"] == 4
