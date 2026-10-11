"""Downloads YouTube's own captions into <data>/transcripts/<id>.json  (extra: pip install study-app[captions]).

YouTube blocks the IP after roughly 15 consecutive requests (IpBlocked / 429), even with pauses. Fetch few
videos at a time; if blocked, change network or wait, or use `study transcribe` (local speech recognition).

Transcript file format (shared with `study transcribe`):
  {"lang", "generated" (auto captions?), "duration" (s), "source", "title", "segments": [[start_second, "text"], ...]}
"""
import json
import time
from pathlib import Path


def fetch(video_id: str, out_dir: Path) -> dict:
    """Returns the transcript (from cache or network). On failure returns {"error": ExceptionName}."""
    target = out_dir / f"{video_id}.json"
    if target.exists():
        return json.loads(target.read_text(encoding="utf-8"))
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return {"error": "MissingDependency: pip install study-app[captions]"}
    try:
        listing = YouTubeTranscriptApi().list(video_id)
        chosen = None
        for code in ("pt", "pt-BR", "en"):
            try:
                chosen = listing.find_transcript([code])
                break
            except Exception:
                pass
        if chosen is None:
            chosen = next(iter(listing))
        fetched = chosen.fetch()
        doc = {"lang": chosen.language_code, "generated": chosen.is_generated,
               "duration": round(fetched[-1].start + fetched[-1].duration), "source": "YouTube captions",
               "segments": [[round(s.start), s.text.replace("\n", " ")] for s in fetched]}
    except Exception as exc:
        return {"error": type(exc).__name__}
    out_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return doc


def fetch_many(video_ids: list[str], out_dir: Path, pause: int = 6, log=print) -> None:
    for video_id in video_ids:
        cached = (out_dir / f"{video_id}.json").exists()
        doc = fetch(video_id, out_dir)
        if "error" in doc:
            log(f"{video_id}: ERROR {doc['error']}")
            if doc["error"] in ("IpBlocked", "RequestBlocked"):
                log("Blocked by YouTube: stop, change network or wait a few hours.")
                return
        else:
            log(f"{video_id}: ok{' (cached)' if cached else ''} {doc['lang']} {round(doc['duration'] / 60)} min")
        if not cached:
            time.sleep(pause)
