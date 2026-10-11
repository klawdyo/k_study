"""Local transcription (extra: pip install study-app[transcribe]).

For ONE video at a time: downloads only the AUDIO into a temporary folder OUTSIDE the data folder, transcribes it
with faster-whisper on the CPU, writes <data>/transcripts/<id>.json and DELETES the audio. Nothing accumulates.

Measured (16-core CPU, model "small", int8): about 4x the video duration. The first run downloads the model (~0.5 GB,
cached by Hugging Face outside the repository).
YouTube's terms generally forbid downloading videos without the author's permission: use for personal study,
few videos, never keep or share the audio.
"""
import json
import shutil
import time
from pathlib import Path

from ..paths import work_dir
from . import extract_id

_models: dict = {}


def download_audio(video_id: str, folder: Path):
    import yt_dlp
    options = {"format": "bestaudio[ext=m4a]/bestaudio", "outtmpl": str(folder / "%(id)s.%(ext)s"),
               "noplaylist": True, "quiet": True, "no_warnings": True, "noprogress": True}
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info("https://www.youtube.com/watch?v=" + video_id, download=True)
    return next(folder.iterdir()), info


def recognize(audio: Path, model: str = "small", language: str = "pt") -> tuple[list[list], str]:
    """Returns (segments, language). language="auto" lets Whisper detect it."""
    from faster_whisper import WhisperModel
    if model not in _models:
        _models[model] = WhisperModel(model, device="cpu", compute_type="int8")
    wanted = None if language in (None, "auto") else language
    segments, info = _models[model].transcribe(str(audio), language=wanted, vad_filter=True, beam_size=5)
    return [[round(s.start), s.text.strip()] for s in segments], (wanted or info.language)


def transcribe_one(entry: str, out_dir: Path, model: str = "small", language: str = "pt",
                   overwrite: bool = False, log=print) -> Path:
    video_id = extract_id(entry)
    target = out_dir / f"{video_id}.json"
    if target.exists() and not overwrite:
        log(f"{video_id}: already in {target}; skipping")
        return target
    folder = work_dir() / video_id
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    t0 = time.time()
    try:
        audio, info = download_audio(video_id, folder)
        t1 = time.time()
        log(f"{video_id}: downloaded {audio.stat().st_size / 1e6:.1f} MB in {t1 - t0:.0f}s - {info.get('title')} ({info.get('duration')}s)")
        segments, detected = recognize(audio, model, language)
        log(f"{video_id}: transcribed in {time.time() - t1:.0f}s ({len(segments)} segments, language: {detected})")
        out_dir.mkdir(parents=True, exist_ok=True)
        doc = {"lang": detected, "generated": True, "duration": info.get("duration"), "title": info.get("title"),
               "source": f"transcribed locally with faster-whisper ({model}) from the video audio", "segments": segments}
        target.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        return target
    finally:
        shutil.rmtree(folder, ignore_errors=True)            # the audio never stays on disk
        log(f"{video_id}: audio deleted")


def transcribe_many(entries: list[str], out_dir: Path, model: str = "small", language: str = "pt",
                    pause: int = 20, overwrite: bool = False, log=print) -> None:
    for n, entry in enumerate(entries):
        try:
            transcribe_one(entry, out_dir, model, language, overwrite, log)
        except Exception as exc:                              # one failing video does not stop the others
            log(f"{entry}: ERROR {type(exc).__name__}: {str(exc)[:200]}")
        if n < len(entries) - 1:
            time.sleep(pause)
