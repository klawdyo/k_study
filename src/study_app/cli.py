"""Command line:  study <command>

  study serve       [--port 8765] [--lan]  run the API and the web UI (asks for the data folder on first run)
  study data-dir    [PATH]                  show / save the data folder for this computer
  study validate                            validate the data folder
  study search      TERMS...                search YouTube
  study captions    ID... | --text ID        download YouTube captions / print one with timestamps
  study transcribe  ID...                   add to the shared queue and transcribe locally (GPU if available; waits until done)
  study queue                               show the shared transcription queue (pending / failed / runner)
  study clean                               delete leftover temporary audio (nothing else deletes it)

The data folder comes from --data-dir, else STUDY_DATA_DIR, else the folder saved for this computer
(chosen in the web UI on first run or with `study data-dir PATH`).
"""
import argparse
import json
import sys

from . import paths


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main(argv=None) -> int:
    _stdout_utf8()
    ap = argparse.ArgumentParser(prog="study", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", help=f"data folder (default: ${paths.ENV_DATA})")
    sub = ap.add_subparsers(dest="command", required=True)

    s = sub.add_parser("serve", help="run the API and the web UI")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--lan", action="store_true",
                   help="also accept other computers on your private network (no password; the firewall may ask to allow it)")

    s = sub.add_parser("data-dir", help="show or save the data folder for this computer")
    s.add_argument("path", nargs="?")

    sub.add_parser("validate", help="validate the data folder")

    s = sub.add_parser("search", help="search YouTube")
    s.add_argument("terms", nargs="+")

    s = sub.add_parser("captions", help="download YouTube captions")
    s.add_argument("videos", nargs="*")
    s.add_argument("--text", metavar="ID", help="print the stored transcript with timestamps")
    s.add_argument("--pause", type=int, default=6)

    s = sub.add_parser("transcribe", help="transcribe locally (parallel downloads and transcriptions)")
    s.add_argument("videos", nargs="+")
    s.add_argument("--model", default="small", help="tiny, base, small (default), medium, large-v3")
    s.add_argument("--language", default="pt", help="pt (default), en, ... or auto")
    s.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    s.add_argument("--downloads", type=int, default=1, help="videos downloaded at the same time (default 1: one by one)")
    s.add_argument("--workers", type=int, default=2, help="videos transcribed at the same time (default 2)")
    s.add_argument("--pause", type=int, default=4, help="seconds each downloader waits between its downloads")
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--no-wait", action="store_true", help="only queue the videos and return (default: wait until they are done)")

    s = sub.add_parser("queue", help="show the shared transcription queue (same view as `study transcribe`)")
    s.add_argument("--watch", action="store_true", help="keep redrawing until Ctrl+C (open it in another terminal)")

    s = sub.add_parser("clean", help="delete the temporary audio (the only thing that ever deletes it)")
    s.add_argument("--force", action="store_true", help="even if a transcription runner seems to be active")

    args = ap.parse_args(argv)
    try:
        if args.command == "search":
            from .youtube.search import search
            for row in search(" ".join(args.terms)):
                print(" | ".join(row))
            return 0

        if args.command == "data-dir":
            from pathlib import Path
            from . import settings
            if args.path:
                target = Path(args.path).expanduser().resolve()
                if not paths.is_data_dir(target):
                    raise paths.ConfigError(f"{target} does not look like a data folder (config.json not found).")
                settings.save_data_dir(target)
                print(f"saved: {target}")
                print(f"settings file: {settings.settings_file()}")
            else:
                found, source = paths.resolve(args.data_dir)
                print(f"data folder: {found or '(not set)'}  (source: {source})")
                print(f"settings file: {settings.settings_file()}")
            return 0
        if args.command == "queue":
            import time

            from .youtube.jobs import snapshot
            from .youtube.view import Watcher, enable_windows_ansi, render, use_color
            if args.watch:
                watcher = Watcher(snapshot, []).start()
                try:
                    while True:
                        time.sleep(3600)
                except KeyboardInterrupt:
                    watcher.stop()
                return 0
            color = use_color()
            if color:
                enable_windows_ansi()
            print(chr(10).join(render(snapshot(), set(), None, color)))
            return 0
        if args.command == "clean":
            from .youtube.jobs import runner_active
            from .youtube.transcribe import clean_work
            if runner_active() and not args.force:
                print("a transcription runner is active; its audio would be deleted. Wait for it or use --force.")
                return 1
            print(f"removed {clean_work()} leftover folder(s) from {paths.work_dir()}")
            return 0
        if args.command == "serve":
            from .server import serve
            found, source = paths.resolve(args.data_dir)
            serve(found, args.port, source, args.lan)
            return 0

        data = paths.data_dir(args.data_dir)
        if args.command == "validate":
            from .validate import inspect
            summary, problems, warnings = inspect(data)
            print("\n".join(summary))
            print("PROBLEMS:" if problems else "OK: no problems.")
            for p in problems:
                print(" -", p)
            if warnings:
                print(f"WARNINGS ({len(warnings)}; heuristics, they never fail the validation; check them):")
                for w in warnings:
                    print(" ~", w)
            return 1 if problems else 0
        elif args.command == "captions":
            from .youtube import extract_id
            from .youtube.captions import fetch, fetch_many
            out = paths.transcripts_dir(data)
            if args.text:
                doc = fetch(extract_id(args.text), out)
                if "error" in doc:
                    print("error:", doc["error"])
                    return 1
                for second, text in doc["segments"]:
                    print(f"[{second // 60:02d}:{second % 60:02d}] {text}")
            else:
                fetch_many([extract_id(v) for v in args.videos], out, args.pause)
        elif args.command == "transcribe":
            from .youtube.jobs import submit
            result = submit(args.videos, paths.transcripts_dir(data), args.model, args.language, args.pause,
                            args.overwrite, args.device, args.downloads, args.workers, wait=not args.no_wait)
            return 3 if result["blocked"] else (1 if result["failed"] else 0)
    except paths.ConfigError as exc:
        print("error:", exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
