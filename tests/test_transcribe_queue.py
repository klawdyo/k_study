"""The shared transcription queue (jobs.py): many calls, one runner; nothing is cleaned automatically."""
import os
import threading

import pytest

from study_app.youtube import jobs
from study_app.youtube import transcribe as tr

IDS = ["aaaaaaaaaa1", "aaaaaaaaaa2", "aaaaaaaaaa3", "aaaaaaaaaa4", "aaaaaaaaaa5"]


@pytest.fixture(autouse=True)
def fast(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDY_WORK_DIR", str(tmp_path / "work"))
    monkeypatch.setattr(tr.time, "sleep", lambda s: None)
    monkeypatch.setattr(tr, "pick_device", lambda device="auto": ("cpu", "int8"))
    monkeypatch.setattr(tr, "recognize", lambda *a, **k: ([[0, "x"]], "pt"))


def fake_download(calls=None, fail_with=None):
    def download(video_id, folder):
        if calls is not None:
            calls.append(video_id)
        if fail_with:
            raise fail_with
        audio = folder / f"{video_id}.m4a"
        audio.write_bytes(b"audio")
        return audio, {"title": "t", "duration": 1}
    return download


def test_the_pipeline_never_cleans_other_folders_automatically(monkeypatch, tmp_path):
    monkeypatch.setattr(tr, "download_audio", fake_download())
    stale = tr.work_dir() / "someone-elses-audio"
    stale.mkdir(parents=True)
    (stale / "a.m4a").write_bytes(b"x")
    tr.transcribe_many(IDS[:2], tmp_path / "t", log=lambda m: None)
    assert (stale / "a.m4a").exists()


def test_clean_work_keeps_the_queue():
    jobs.enqueue([IDS[0]], "small", "pt", False)
    (tr.work_dir() / "stale").mkdir()
    assert tr.clean_work() == 1
    assert jobs.queue_status()["pending"] == [IDS[0]]


def test_concurrent_calls_share_one_queue_and_one_runner(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(tr, "download_audio", fake_download(calls))
    running, peak, lock = [0], [0], threading.Lock()
    real = jobs.transcribe_many

    def tracked(*args, **kwargs):
        with lock:
            running[0] += 1
            peak[0] = max(peak[0], running[0])
        threading.Event().wait(0.1)
        try:
            return real(*args, **kwargs)
        finally:
            with lock:
                running[0] -= 1

    monkeypatch.setattr(jobs, "transcribe_many", tracked)
    out = tmp_path / "t"
    results = {}

    def call(name, ids):
        results[name] = jobs.submit(ids, out, log=lambda m: None)

    threads = [threading.Thread(target=call, args=("a", IDS[:3])), threading.Thread(target=call, args=("b", IDS[2:]))]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=60)
    assert peak[0] == 1                                              # never two pipelines at once
    assert sorted(calls) == sorted(IDS)                              # each video once (IDS[2] was in both calls)
    assert sorted(results["a"]["ok"]) == sorted(IDS[:3]) and sorted(results["b"]["ok"]) == sorted(IDS[2:])
    assert jobs.queue_status()["pending"] == [] and not jobs.runner_active()


def test_a_crashed_runners_stale_lock_is_taken_over(monkeypatch, tmp_path):
    monkeypatch.setattr(tr, "download_audio", fake_download())
    assert jobs._acquire_runner()
    old = jobs.time.time() - 3600
    os.utime(jobs._lock_file(), (old, old))                          # its heartbeat stopped long ago
    result = jobs.submit(IDS[:1], tmp_path / "t", log=lambda m: None)
    assert result["ok"] == [IDS[0]]


def test_no_wait_only_queues_when_another_runner_is_active(tmp_path):
    assert jobs._acquire_runner()                                    # someone else is the runner
    result = jobs.submit(IDS[:2], tmp_path / "t", wait=False, log=lambda m: None)
    assert result["queued"] == 2 and jobs.queue_status()["pending"] == IDS[:2]


def test_a_youtube_block_is_reported_and_the_next_call_resumes(monkeypatch, tmp_path):
    monkeypatch.setattr(tr, "download_audio", fake_download(fail_with=RuntimeError("HTTP Error 429: Too Many Requests")))
    result = jobs.submit(IDS[:2], tmp_path / "t", log=lambda m: None)
    assert result["blocked"] is True and jobs.queue_status()["blocked"]
    monkeypatch.setattr(tr, "download_audio", fake_download())      # the user changed network
    result = jobs.submit(IDS[:2], tmp_path / "t", log=lambda m: None)
    assert sorted(result["ok"]) == sorted(IDS[:2]) and not jobs.queue_status()["blocked"]


def test_a_video_that_fails_is_marked_and_does_not_block_the_others(monkeypatch, tmp_path):
    def download(video_id, folder):
        if video_id == IDS[0]:
            raise RuntimeError("Video unavailable")
        return fake_download()(video_id, folder)

    monkeypatch.setattr(tr, "download_audio", download)
    result = jobs.submit(IDS[:3], tmp_path / "t", log=lambda m: None)
    assert result["failed"] == [IDS[0]] and sorted(result["ok"]) == sorted(IDS[1:3])
    assert jobs.queue_status()["failed"] == [IDS[0]]
