import json


def jget(call, path):
    status, raw = call("GET", path)
    return status, json.loads(raw)


def test_first_run_needs_setup_and_blocks_data_routes(blank_api):
    status, info = jget(blank_api, "/api/setup")
    assert status == 200 and info["configured"] is False and info["dataDir"] is None
    assert blank_api("GET", "/api/config")[0] == 409
    assert blank_api("GET", "/api/progress")[0] == 409
    assert blank_api("PUT", "/api/progress/items/block-1/r", {"done": True})[0] == 409
    assert blank_api("GET", "/")[0] == 200            # the UI itself is served so it can show the setup screen


def test_choosing_a_valid_folder_saves_it_and_unlocks_the_app(blank_api, data_dir):
    status, raw = blank_api("PUT", "/api/setup", {"path": str(data_dir)})
    info = json.loads(raw)
    assert status == 200 and info["configured"] is True and info["source"] == "saved"
    assert blank_api("GET", "/api/config")[0] == 200
    from study_app import settings
    assert settings.saved_data_dir() == str(data_dir.resolve())
    # the choice survives a restart: resolve() finds it without flags or env vars
    from study_app import paths
    path, source = paths.resolve()
    assert path == data_dir.resolve() and source == "saved"


def test_a_folder_without_config_json_is_rejected(blank_api, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    status, raw = blank_api("PUT", "/api/setup", {"path": str(empty)})
    assert status == 400 and json.loads(raw)["error"] == "not_a_data_folder"
    assert jget(blank_api, "/api/setup")[1]["configured"] is False


def test_folder_fixed_by_flag_or_env_cannot_be_changed_in_the_ui(api, tmp_path):
    status, raw = api("PUT", "/api/setup", {"path": str(tmp_path)})
    assert status == 409 and json.loads(raw)["error"] == "locked"


def test_app_never_lists_the_disk(blank_api):
    assert blank_api("GET", "/api/fs?path=C:/")[0] == 404          # the folder browser route no longer exists


def test_native_file_dialog_result_is_returned_but_not_saved(blank_api, data_dir, monkeypatch):
    from study_app import picker, settings
    monkeypatch.setattr(picker, "pick_config_file", lambda initial=None: {
        "available": True, "cancelled": False, "folder": str(data_dir), "isDataDir": True})
    status, raw = blank_api("POST", "/api/setup/pick", {})
    result = json.loads(raw)
    assert status == 200 and result["folder"] == str(data_dir) and result["isDataDir"] is True
    assert settings.saved_data_dir() is None                          # only PUT /api/setup saves


def test_file_dialog_is_refused_when_the_folder_is_fixed(api):
    assert api("POST", "/api/setup/pick", {})[0] == 409


def test_env_var_wins_over_the_saved_folder(data_dir, tmp_path, monkeypatch):
    from study_app import paths, settings
    other = tmp_path / "other"
    other.mkdir()
    (other / "config.json").write_text("{}", encoding="utf-8")
    settings.save_data_dir(other)
    monkeypatch.setenv("STUDY_DATA_DIR", str(data_dir))
    path, source = paths.resolve()
    assert path == data_dir.resolve() and source == "env"


def test_forged_host_header_is_refused(data_dir):
    import http.client
    import threading

    from study_app.server import make_server

    server = make_server(data_dir, port=0, source="flag")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        port = server.server_address[1]
        for host, expected in ((f"localhost:{port}", 200), (f"127.0.0.1:{port}", 200), ("evil.example.com", 403), (f"evil.example.com:{port}", 403)):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
            conn.request("GET", "/api/progress", headers={"Host": host})
            assert conn.getresponse().status == expected, host
            conn.close()
    finally:
        server.shutdown()
