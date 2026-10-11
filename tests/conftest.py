import json
import threading

import pytest

from study_app.server import make_server


@pytest.fixture()
def data_dir(tmp_path):
    """A minimal data folder: one block, one reading, one question set, one video with transcript."""
    (tmp_path / "block-1").mkdir()
    (tmp_path / "transcripts").mkdir()
    (tmp_path / "config.json").write_text(json.dumps(
        {"schema": "config/v2", "title": "T", "blocks": [{"id": "block-1", "title": "B", "file": "block-1/block.json"}]}), encoding="utf-8")
    (tmp_path / "block-1" / "read.md").write_text("# Hello\n", encoding="utf-8")
    (tmp_path / "transcripts" / "aaaaaaaaaaa.json").write_text(json.dumps(
        {"lang": "pt", "generated": True, "duration": 10, "source": "test", "segments": [[0, "hi"]]}), encoding="utf-8")
    (tmp_path / "block-1" / "q.json").write_text(json.dumps({
        "schema": "questions/v2", "id": "q", "title": "Q",
        "questions": [{"id": "q01", "type": "single", "prompt": "2+2?", "generalExplanation": "g",
                       "options": [{"id": "a", "text": "4", "correct": True, "explanation": "yes"},
                                   {"id": "b", "text": "5", "correct": False, "explanation": "no"}]}]}), encoding="utf-8")
    (tmp_path / "block-1" / "block.json").write_text(json.dumps({
        "schema": "block/v2", "id": "block-1", "title": "B", "description": "",
        "sections": [{"id": "s", "title": "S", "items": [
            {"id": "r", "type": "markdown", "title": "R", "path": "read.md"},
            {"id": "v", "type": "video", "title": "V", "url": "https://www.youtube.com/watch?v=aaaaaaaaaaa",
             "transcript": "../transcripts/aaaaaaaaaaa.json", "clips": [{"start": 0, "end": 5}]},
            {"id": "q", "type": "questions", "title": "Q", "path": "q.json"}]}]}), encoding="utf-8")
    return tmp_path


@pytest.fixture()
def api(data_dir):
    """Running server on a free port; yields a tiny HTTP helper."""
    import http.client

    server = make_server(data_dir, port=0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def call(method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        payload = json.dumps(body) if body is not None else None
        conn.request(method, path, payload, {"Content-Type": "application/json"})
        response = conn.getresponse()
        raw = response.read()
        conn.close()
        return response.status, raw

    yield call
    server.shutdown()
