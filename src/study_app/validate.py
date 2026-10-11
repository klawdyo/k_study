"""Validates a data folder. Run before calling a block done:  study validate

Checks, for every block listed in config.json:
  * unique item ids; known item types; paths exist and stay inside the data folder;
  * images referenced in Markdown, prompts and explanations exist;
  * videos: valid YouTube URL; clips with end > start; transcript file exists when referenced;
  * questions: unique ids; 'single' has exactly 1 correct option, 'multiple' has 2 or more;
    EVERY option has an explanation; every question has a generalExplanation.
"""
import json
import re
from pathlib import Path

ITEM_TYPES = {"video", "markdown", "pdf", "link", "questions"}
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
YOUTUBE = re.compile(r"(?:v=|youtu\.be/)([\w-]{11})")


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(data: Path) -> tuple[list[str], list[str]]:
    """Returns (summary lines, problems)."""
    data = data.resolve()
    problems: list[str] = []

    def inside(path: Path) -> bool:
        return data in path.resolve().parents

    def check_images(text: str, base: Path, where: str):
        for ref in IMAGE.findall(text or ""):
            if not ref.startswith("http") and not (base / ref).resolve().exists():
                problems.append(f"{where}: missing image {ref}")

    def check_questions(path: Path, where: str) -> int:
        doc = _load(path)
        ids = [q["id"] for q in doc["questions"]]
        if len(set(ids)) != len(ids):
            problems.append(f"{where}: duplicate question ids")
        for q in doc["questions"]:
            w = f"{where}/{q['id']}"
            correct = sum(bool(o["correct"]) for o in q["options"])
            if q["type"] == "single" and correct != 1:
                problems.append(f"{w}: 'single' with {correct} correct options")
            elif q["type"] == "multiple" and correct < 2:
                problems.append(f"{w}: 'multiple' with {correct} correct options")
            elif q["type"] not in ("single", "multiple"):
                problems.append(f"{w}: unknown question type {q['type']}")
            for o in q["options"]:
                if not str(o.get("explanation", "")).strip():
                    problems.append(f"{w}/{o['id']}: option without explanation")
            if not q.get("generalExplanation"):
                problems.append(f"{w}: missing generalExplanation")
            prompt = q.get("prompt", "")
            if q.get("promptFile"):
                pf = path.parent / q["promptFile"]
                if not pf.exists():
                    problems.append(f"{w}: promptFile not found")
                else:
                    prompt = pf.read_text(encoding="utf-8")
            check_images(prompt, path.parent, w)
            check_images(q.get("generalExplanation", ""), path.parent, w)
            for o in q["options"]:
                check_images(o.get("explanation", ""), path.parent, w)
        return len(doc["questions"])

    summary = []
    config = _load(data / "config.json")
    for entry in config["blocks"]:
        block_path = data / entry["file"]
        block = _load(block_path)
        if block["id"] != entry["id"]:
            problems.append(f"{entry['id']}: block.json id ({block['id']}) differs from config.json")
        seen, n_questions, n_videos = set(), 0, 0
        for section in block["sections"]:
            for item in section["items"]:
                w = f"{block['id']}/{item['id']}"
                if item["id"] in seen:
                    problems.append(f"{w}: duplicate item id")
                seen.add(item["id"])
                if item["type"] not in ITEM_TYPES:
                    problems.append(f"{w}: unknown type {item['type']}")
                if "path" in item:
                    target = (block_path.parent / item["path"]).resolve()
                    if not inside(target):
                        problems.append(f"{w}: path leaves the data folder")
                    elif not target.exists():
                        problems.append(f"{w}: file not found {item['path']}")
                    elif item["type"] == "questions":
                        n_questions += check_questions(target, w)
                    elif item["type"] == "markdown":
                        check_images(target.read_text(encoding="utf-8"), target.parent, w)
                if item["type"] == "video":
                    n_videos += 1
                    if not YOUTUBE.search(item.get("url", "")):
                        problems.append(f"{w}: invalid video URL")
                    if item.get("transcript"):
                        t = (block_path.parent / item["transcript"]).resolve()
                        if not inside(t) or not t.exists():
                            problems.append(f"{w}: transcript not found {item['transcript']}")
                    if item.get("review") and not item.get("transcript"):
                        problems.append(f"{w}: has a review but no transcript")
                    for clip in item.get("clips", []):
                        if clip["end"] <= clip["start"]:
                            problems.append(f"{w}: clip with end <= start")
        summary.append(f"{block['id']}: {len(seen)} items, {n_videos} videos, {n_questions} questions")
    return summary, problems
