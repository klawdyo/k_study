"""Validates a data folder. Run before calling a block done:  study validate

Checks that make a data folder INVALID (problems), for every block listed in config.json:
  * unique item ids; known item types; paths exist and stay inside the data folder;
  * images referenced in Markdown, prompts and explanations exist;
  * videos: valid YouTube URL; clips with end > start; transcript file exists when referenced;
  * questions: unique ids; 'single' has exactly 1 correct option, 'multiple' has 2 or more;
    EVERY option has an explanation; every question has a generalExplanation;
  * no control characters left by broken JSON escapes (a "\\beta" that became a backspace).

Heuristics that only WARN (they never fail the validation: look at them and decide):
  * a clip or a review time that goes past the end of the video by more than a tolerance (max(30 s, 5 %): the end
    of a video is often music or silence), or a clip that starts long after the last spoken line;
  * LaTeX in Markdown or questions (the app does not render it);
  * answer position: most 'single' answers on the same letter, or the correct option almost always the longest;
  * very short option explanations; very short readings.
"""
import json
import re
from pathlib import Path

ITEM_TYPES = {"video", "markdown", "pdf", "link", "questions"}
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
YOUTUBE = re.compile(r"(?:v=|youtu\.be/)([\w-]{11})")
LATEX = re.compile(r"\\(?:frac|text|sum|beta|alpha|hat|le|ge|leq|geq|times|cdot|bigcup|sqrt|lambda|mu|sigma)\b|"
                   r"(?<![A-Za-z0-9])\$[^\s$][^$\n]{0,60}\$(?![0-9])")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
CLOCK = re.compile(r"\b(\d{1,2}):(\d{2})\b")
TOLERANCE_SECONDS, TOLERANCE_FRACTION = 30, 0.05      # slack allowed past the end of a video before warning
SPOKEN_GAP_SECONDS = 90                               # a clip starting this long after the last spoken line


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(data: Path) -> tuple[list[str], list[str]]:
    """Returns (summary lines, problems). See `inspect` for the non-blocking warnings too."""
    summary, problems, _ = inspect(data)
    return summary, problems


def inspect(data: Path) -> tuple[list[str], list[str], list[str]]:
    """Returns (summary lines, problems, warnings). Only problems make a data folder invalid."""
    data = data.resolve()
    problems: list[str] = []
    warnings: list[str] = []
    latex_hits: dict[str, list[str]] = {}
    short_hits: dict[str, int] = {}

    def item_of(where: str) -> str:
        return "/".join(where.split("/")[:2])

    def inside(path: Path) -> bool:
        return data in path.resolve().parents

    def check_images(text: str, base: Path, where: str):
        for ref in IMAGE.findall(text or ""):
            if not ref.startswith("http") and not (base / ref).resolve().exists():
                problems.append(f"{where}: missing image {ref}")

    def check_text(text: str, where: str):
        if CONTROL.search(text or ""):
            problems.append(f"{where}: control character in the text (a broken JSON escape such as \\beta or \\text)")
        found = LATEX.search(text or "")
        if found:
            latex_hits.setdefault(item_of(where), []).append(f"{where.split('/', 2)[-1] if where.count('/') > 1 else 'text'} {found.group(0)[:24]!r}")

    def check_questions(path: Path, where: str) -> int:
        doc = _load(path)
        ids = [q["id"] for q in doc["questions"]]
        if len(set(ids)) != len(ids):
            problems.append(f"{where}: duplicate question ids")
        singles, correct_at, longest = 0, {}, 0
        for q in doc["questions"]:
            w = f"{where}/{q['id']}"
            check_text(str(q.get("prompt", "")) + str(q.get("generalExplanation", "")), w)
            correct = sum(bool(o["correct"]) for o in q["options"])
            if q["type"] == "single" and correct != 1:
                problems.append(f"{w}: 'single' with {correct} correct options")
            elif q["type"] == "multiple" and correct < 2:
                problems.append(f"{w}: 'multiple' with {correct} correct options")
            elif q["type"] not in ("single", "multiple"):
                problems.append(f"{w}: unknown question type {q['type']}")
            if q["type"] == "single" and correct == 1:
                at = next(i for i, o in enumerate(q["options"]) if o["correct"])
                singles += 1
                correct_at[at] = correct_at.get(at, 0) + 1
                lengths = [len(str(o.get("text", ""))) for o in q["options"]]
                longest += lengths[at] == max(lengths)
            for o in q["options"]:
                check_text(str(o.get("text", "")) + str(o.get("explanation", "")), f"{w}/{o['id']}")
                explanation = str(o.get("explanation", "")).strip()
                if not explanation:
                    problems.append(f"{w}/{o['id']}: option without explanation")
                elif len(explanation) < 40:
                    short_hits[item_of(w)] = short_hits.get(item_of(w), 0) + 1
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
        if singles >= 6:
            letter, count = max(correct_at.items(), key=lambda kv: kv[1])
            if count / singles > 0.6:
                warnings.append(f"{where}: {count} of {singles} single answers are option {'ABCDEFGH'[letter]}; shuffle the options")
            if longest / singles > 0.7:
                warnings.append(f"{where}: the correct option is the longest in {longest} of {singles} single questions; balance the lengths")
        return len(doc["questions"])

    def check_video_times(item: dict, transcript: dict, w: str):
        segments = transcript.get("segments") or []
        duration = transcript.get("duration") or (segments[-1][0] if segments else 0)
        if not duration:
            return
        slack = max(TOLERANCE_SECONDS, TOLERANCE_FRACTION * duration)
        last_spoken = segments[-1][0] if segments else duration
        for clip in item.get("clips", []):
            if clip["start"] >= duration:
                warnings.append(f"{w}: clip {clip['start']}-{clip['end']} s starts after the end of the video ({duration} s)")
            elif clip["end"] > duration + slack:
                warnings.append(f"{w}: clip {clip['start']}-{clip['end']} s ends {clip['end'] - duration:.0f} s past the end of the video ({duration} s)")
            elif clip["start"] > last_spoken + SPOKEN_GAP_SECONDS:
                warnings.append(f"{w}: clip starts at {clip['start']} s but the last spoken line is at {last_spoken} s")
        for line in (item.get("review") or {}).get("covers", []):
            for minutes, seconds in CLOCK.findall(line):
                if int(minutes) * 60 + int(seconds) > duration + slack:
                    warnings.append(f"{w}: review mentions {minutes}:{seconds} but the video lasts {int(duration) // 60}:{int(duration) % 60:02d}")
                    break

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
                        text = target.read_text(encoding="utf-8")
                        check_images(text, target.parent, w)
                        check_text(text, w)
                        name = item["path"].lower()
                        if text.count("\n") < 250 and "guia" not in name and "guide" not in name:
                            warnings.append(f"{w}: short reading ({text.count(chr(10))} lines; the target is 350 to 700)")
                if item["type"] == "video":
                    n_videos += 1
                    if not YOUTUBE.search(item.get("url", "")):
                        problems.append(f"{w}: invalid video URL")
                    if item.get("transcript"):
                        t = (block_path.parent / item["transcript"]).resolve()
                        if not inside(t) or not t.exists():
                            problems.append(f"{w}: transcript not found {item['transcript']}")
                        else:
                            check_video_times(item, _load(t), w)
                    if item.get("review") and not item.get("transcript"):
                        problems.append(f"{w}: has a review but no transcript")
                    for clip in item.get("clips", []):
                        if clip["end"] <= clip["start"]:
                            problems.append(f"{w}: clip with end <= start")
        summary.append(f"{block['id']}: {len(seen)} items, {n_videos} videos, {n_questions} questions")
    for where, hits in latex_hits.items():
        warnings.append(f"{where}: {len(hits)} spot(s) look like LaTeX (e.g. {hits[0]}); the app does not render it, use Unicode")
    for where, count in short_hits.items():
        warnings.append(f"{where}: {count} option explanation(s) shorter than 40 characters")
    return summary, problems, warnings
