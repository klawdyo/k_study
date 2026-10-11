import json

from study_app.validate import validate


def test_valid_data_folder_has_no_problems(data_dir):
    summary, problems = validate(data_dir)
    assert problems == []
    assert summary == ["block-1: 3 items, 1 videos, 1 questions"]


def test_every_option_needs_an_explanation(data_dir):
    path = data_dir / "block-1" / "q.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["questions"][0]["options"][1]["explanation"] = ""
    path.write_text(json.dumps(doc), encoding="utf-8")
    _, problems = validate(data_dir)
    assert any("option without explanation" in p for p in problems)


def test_single_question_needs_exactly_one_correct_option(data_dir):
    path = data_dir / "block-1" / "q.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["questions"][0]["options"][1]["correct"] = True
    path.write_text(json.dumps(doc), encoding="utf-8")
    _, problems = validate(data_dir)
    assert any("'single' with 2 correct" in p for p in problems)


def test_missing_files_and_bad_clips_are_reported(data_dir):
    path = data_dir / "block-1" / "block.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["sections"][0]["items"][0]["path"] = "nope.md"
    doc["sections"][0]["items"][1]["clips"] = [{"start": 9, "end": 3}]
    path.write_text(json.dumps(doc), encoding="utf-8")
    _, problems = validate(data_dir)
    assert any("file not found" in p for p in problems)
    assert any("end <= start" in p for p in problems)


def _set_clip(data_dir, start, end):
    import json
    path = data_dir / "block-1" / "block.json"
    block = json.loads(path.read_text(encoding="utf-8"))
    video = next(i for s in block["sections"] for i in s["items"] if i["type"] == "video")
    video["clips"] = [{"start": start, "end": end}]
    path.write_text(json.dumps(block), encoding="utf-8")


def test_a_clip_slightly_past_the_end_only_gets_no_warning_but_a_far_one_warns_without_failing(data_dir):
    from study_app.validate import inspect
    _set_clip(data_dir, 0, 35)                                       # 25 s past a 10 s video: inside the 30 s tolerance
    _, problems, warnings = inspect(data_dir)
    assert problems == [] and not any("past the end" in w for w in warnings)
    _set_clip(data_dir, 0, 200)                                      # far past the end
    _, problems, warnings = inspect(data_dir)
    assert problems == [] and any("past the end" in w for w in warnings)      # a warning, never a failure


def test_broken_json_escapes_fail_but_latex_and_answer_position_only_warn(data_dir):
    import json
    from study_app.validate import inspect
    path = data_dir / "block-1" / "q.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["questions"][0]["options"][0]["text"] = "valor $" + chr(92) + "beta$ = 0"
    path.write_text(json.dumps(doc), encoding="utf-8")
    _, problems, warnings = inspect(data_dir)
    assert problems == [] and any("LaTeX" in w for w in warnings)
    doc["questions"][0]["options"][0]["text"] = "valor " + chr(8) + "eta = 0"            # what a broken backslash-beta becomes
    path.write_text(json.dumps(doc), encoding="utf-8")
    _, problems, _ = inspect(data_dir)
    assert any("control character" in p for p in problems)
