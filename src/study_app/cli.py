"""Command line:  study <command>

  study serve       [--port 8765]          run the API and the web UI
  study validate                            validate the data folder
  study search      TERMS...                search YouTube
  study captions    ID... | --text ID        download YouTube captions / print one with timestamps
  study transcribe  ID...                   transcribe locally (one video at a time, audio deleted afterwards)

The data folder comes from the STUDY_DATA_DIR environment variable (or --data-dir).
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

    sub.add_parser("validate", help="validate the data folder")

    s = sub.add_parser("search", help="search YouTube")
    s.add_argument("terms", nargs="+")

    s = sub.add_parser("captions", help="download YouTube captions")
    s.add_argument("videos", nargs="*")
    s.add_argument("--text", metavar="ID", help="print the stored transcript with timestamps")
    s.add_argument("--pause", type=int, default=6)

    s = sub.add_parser("transcribe", help="transcribe locally, one video at a time")
    s.add_argument("videos", nargs="+")
    s.add_argument("--model", default="small", help="tiny, base, small (default), medium, large-v3")
    s.add_argument("--language", default="pt")
    s.add_argument("--pause", type=int, default=20)
    s.add_argument("--overwrite", action="store_true")

    args = ap.parse_args(argv)
    try:
        if args.command == "search":
            from .youtube.search import search
            for row in search(" ".join(args.terms)):
                print(" | ".join(row))
            return 0

        data = paths.data_dir(args.data_dir)
        if args.command == "serve":
            from .server import serve
            serve(data, args.port)
        elif args.command == "validate":
            from .validate import validate
            summary, problems = validate(data)
            print("\n".join(summary))
            print("PROBLEMS:" if problems else "OK: no problems.")
            for p in problems:
                print(" -", p)
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
            from .youtube.transcribe import transcribe_many
            transcribe_many(args.videos, paths.transcripts_dir(data), args.model, args.language, args.pause, args.overwrite)
    except paths.ConfigError as exc:
        print("error:", exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
