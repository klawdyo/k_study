import json


def get_json(api, path):
    status, raw = api("GET", path)
    return status, json.loads(raw)


def test_config_and_content_are_read_through_the_api(api):
    status, config = get_json(api, "/api/config")
    assert status == 200 and config["blocks"][0]["id"] == "block-1"
    status, raw = api("GET", "/api/content/block-1/read.md")
    assert status == 200 and raw.decode("utf-8").startswith("# Hello")


def test_content_cannot_escape_the_data_folder(api):
    status, _ = api("GET", "/api/content/../../etc/passwd")
    assert status == 404
    status, _ = api("GET", "/api/content/%2e%2e/%2e%2e/secret")
    assert status == 404


def test_progress_starts_empty(api):
    status, state = get_json(api, "/api/progress")
    assert status == 200 and state == {"items": {}, "answers": {}, "notes": {}}


def test_item_done_roundtrip_and_persistence(api, data_dir):
    status, raw = api("PUT", "/api/progress/items/block-1/r", {"done": True})
    state = json.loads(raw)
    assert status == 200 and state["items"]["block-1/r"]["done"] is True
    # the file on disk is the single source of truth
    on_disk = json.loads((data_dir / "progress.json").read_text(encoding="utf-8"))
    assert on_disk["items"]["block-1/r"]["done"] is True
    _, state = get_json(api, "/api/progress")
    assert state["items"]["block-1/r"]["done"] is True
    status, raw = api("PUT", "/api/progress/items/block-1/r", {"done": False})
    assert json.loads(raw)["items"]["block-1/r"]["done"] is False


def test_answers_can_be_saved_and_removed(api):
    body = {"chosen": ["a"], "correct": True}
    status, raw = api("PUT", "/api/progress/answers/block-1/q/q01", body)
    state = json.loads(raw)
    assert status == 200 and state["answers"]["block-1/q"]["q01"]["chosen"] == ["a"]
    status, raw = api("DELETE", "/api/progress/answers/block-1/q/q01")
    assert json.loads(raw)["answers"]["block-1/q"] == {}


def test_notes_are_saved_and_blank_notes_are_removed(api):
    _, raw = api("PUT", "/api/progress/notes/block-1/r", {"text": "remember"})
    assert json.loads(raw)["notes"]["block-1/r"] == "remember"
    _, raw = api("PUT", "/api/progress/notes/block-1/r", {"text": "  "})
    assert "block-1/r" not in json.loads(raw)["notes"]


def test_unknown_routes_and_bad_json(api):
    assert api("PUT", "/api/progress/bogus/block-1/r", {})[0] == 404
    assert api("GET", "/api/nothing")[0] == 404
    assert api("GET", "/")[0] == 200            # web UI is served
    assert api("GET", "/app.js")[0] == 200
