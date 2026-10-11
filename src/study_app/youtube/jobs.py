"""Shared transcription queue: any number of `study transcribe` calls, one runner.

Every call only ADDS its videos to one queue on disk (inside the work folder, outside the data folder) and then either
becomes the single runner (lock file with a heartbeat) or waits for the runner that is already working. So calls from any
number of terminals never download or transcribe at the same time, and a video is never done twice. A call returns when
ITS videos are done (`wait=False` returns right after queuing). Nothing here deletes audio: only `study clean` does.

Layout (under <work folder>/_queue/): jobs/<id>.json (pending), failed/<id>.txt (gave up), runner.lock, BLOCKED.
"""
import json
import os
import threading
import time
from pathlib import Path

from ..paths import work_dir
from . import extract_id
from .transcribe import QUEUE_NAME, log_line, transcribe_many

LOCK_STALE_SECONDS = 60          # a lock whose heartbeat is older than this belongs to a crashed runner


def queue_dir() -> Path:
    return work_dir() / QUEUE_NAME


def _jobs_dir() -> Path:
    return queue_dir() / "jobs"


def _failed_dir() -> Path:
    return queue_dir() / "failed"


def _lock_file() -> Path:
    return queue_dir() / "runner.lock"


def _blocked_file() -> Path:
    return queue_dir() / "BLOCKED"


def runner_active() -> bool:
    try:
        return time.time() - _lock_file().stat().st_mtime < LOCK_STALE_SECONDS
    except OSError:
        return False


def _acquire_runner() -> bool:
    """Exclusive creation of the lock file; a lock whose heartbeat stopped (crashed runner) is taken over."""
    queue_dir().mkdir(parents=True, exist_ok=True)
    lock = _lock_file()
    for _ in range(2):
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            if runner_active():
                return False
            try:
                lock.unlink()
            except OSError:
                return False
    return False


def _release_runner() -> None:
    try:
        _lock_file().unlink()
    except OSError:
        pass


def enqueue(ids: list[str], model: str, language: str, overwrite: bool) -> int:
    """Adds videos to the queue (an id already queued is not added twice). Clears old failure/block marks of a new request."""
    _jobs_dir().mkdir(parents=True, exist_ok=True)
    _failed_dir().mkdir(parents=True, exist_ok=True)
    _blocked_file().unlink(missing_ok=True)
    added = 0
    for video_id in ids:
        (_failed_dir() / f"{video_id}.txt").unlink(missing_ok=True)
        job = _jobs_dir() / f"{video_id}.json"
        if job.exists():
            continue
        tmp = job.with_suffix(".tmp")
        tmp.write_text(json.dumps({"id": video_id, "model": model, "language": language, "overwrite": overwrite}), encoding="utf-8")
        os.replace(tmp, job)
        added += 1
    return added


def _read_jobs() -> list[dict]:
    found = []
    if _jobs_dir().exists():
        for f in _jobs_dir().glob("*.json"):
            try:                                                     # a job may be removed by the runner meanwhile
                found.append((f.stat().st_mtime, json.loads(f.read_text(encoding="utf-8"))))
            except (OSError, ValueError):
                continue
    return [job for _, job in sorted(found, key=lambda pair: pair[0])]


def queue_status() -> dict:
    return {"pending": [j["id"] for j in _read_jobs()],
            "failed": sorted(p.stem for p in _failed_dir().glob("*.txt")) if _failed_dir().exists() else [],
            "blocked": _blocked_file().exists(), "runner": runner_active()}


def _run_queue(out_dir: Path, pause: int, device: str, downloads: int, workers: int, log) -> None:
    """The runner: drains the queue (including videos other calls add meanwhile) until it is empty or YouTube blocks."""
    stop = threading.Event()

    def heartbeat() -> None:
        while not stop.wait(5):
            try:
                os.utime(_lock_file())
            except OSError:
                pass

    threading.Thread(target=heartbeat, daemon=True).start()
    try:
        while True:
            jobs = []
            for job in _read_jobs():
                if not job.get("overwrite") and (out_dir / f"{job['id']}.json").exists():
                    (_jobs_dir() / f"{job['id']}.json").unlink(missing_ok=True)        # already done
                else:
                    jobs.append(job)
            if not jobs:
                return
            first = jobs[0]
            key = (first["model"], first["language"], bool(first.get("overwrite")))
            ids = [j["id"] for j in jobs if (j["model"], j["language"], bool(j.get("overwrite"))) == key]
            log(f"queue: {len(jobs)} pending; running {len(ids)} (model={key[0]}, language={key[1]})")
            summary = transcribe_many(ids, out_dir, key[0], key[1], pause, key[2], device, downloads, workers, log)
            for video_id in ids:
                if video_id in summary["ok"]:
                    (_jobs_dir() / f"{video_id}.json").unlink(missing_ok=True)
                elif not summary["blocked"]:
                    _failed_dir().mkdir(parents=True, exist_ok=True)
                    (_failed_dir() / f"{video_id}.txt").write_text("not transcribed; see the runner's log", encoding="utf-8")
                    (_jobs_dir() / f"{video_id}.json").unlink(missing_ok=True)
            if summary["blocked"]:
                _blocked_file().write_text("blocked by YouTube", encoding="utf-8")
                return
    finally:
        stop.set()
        _release_runner()


def submit(entries: list[str], out_dir: Path, model: str = "small", language: str = "pt", pause: int = 4,
           overwrite: bool = False, device: str = "auto", downloads: int = 1, workers: int = 2,
           wait: bool = True, log=log_line) -> dict:
    """Queues the videos and, if wait, returns when THEY are done. Returns {'ok','failed','blocked','queued'}."""
    ids = list(dict.fromkeys(extract_id(e) for e in entries))
    todo = [i for i in ids if overwrite or not (out_dir / f"{i}.json").exists()]
    for skipped in set(ids) - set(todo):
        log(f"{skipped}: already transcribed; skipping")
    result = {"ok": [], "failed": [], "blocked": False, "queued": 0}
    if not todo:
        return result
    result["queued"] = enqueue(todo, model, language, overwrite)
    log(f"queued {result['queued']} new video(s) ({len(todo) - result['queued']} were already in the queue)")
    last_note = 0.0
    while True:
        if _acquire_runner():
            log("this call is the runner")
            _run_queue(out_dir, pause, device, downloads, workers, log)
        elif not wait:
            log("another call is the runner; it will process these videos")
            return result
        status = queue_status()
        pending = [i for i in todo if i in status["pending"]]
        if not pending:
            break
        if status["blocked"]:
            result["blocked"] = True
            break
        if time.time() - last_note > 60:
            log(f"waiting for the runner: {len(status['pending'])} in the queue")
            last_note = time.time()
        time.sleep(3)
    for video_id in todo:
        if (out_dir / f"{video_id}.json").exists():
            result["ok"].append(video_id)
        elif not result["blocked"]:
            result["failed"].append(video_id)
    return result
