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
