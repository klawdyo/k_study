# study-app

A small local study app: a **web UI + HTTP API** that serves lessons (videos, readings, question sets) from a **data folder** and stores your progress in **one file**. It also ships the **CLI tools** used to build the lessons (YouTube search, captions, local transcription, content validation).

- The app itself uses **only the Python standard library**. Heavy dependencies (speech recognition) are optional extras.
- **Code and data are separate.** This repository holds code only. The data folder (lessons, figures, transcripts, `progress.json`) lives elsewhere (e.g. a synced folder) and is selected with an environment variable.
- **Single source of truth.** The web UI keeps no state: content and progress are read and written only through the API; the API owns `progress.json`.
- Code, identifiers, file names and JSON keys are in English. The UI text and the Markdown the student reads are in Portuguese.

## Install

```bash
git clone git@github.com:klawdyo/estudos.git
cd estudos
python -m venv .venv && .venv\Scripts\activate          # Windows (use source .venv/bin/activate on Linux/macOS)
pip install -e .                                         # the app only
pip install -e ".[all]"                                  # + captions + local transcription (yt-dlp, faster-whisper)
```

Extras: `captions` (youtube-transcript-api), `transcribe` (yt-dlp + faster-whisper), `dev` (pytest).

## Configure

```bash
set STUDY_DATA_DIR=G:\path\to\data            # Windows;  export STUDY_DATA_DIR=/path/to/data  elsewhere
```

| Variable | Meaning |
| :-- | :-- |
| `STUDY_DATA_DIR` | **Required.** Folder with `config.json`, `progress.json`, `transcripts/`, `figures/` and one folder per block. Any command also accepts `--data-dir`. |
| `STUDY_WORK_DIR` | Temporary folder for downloaded audio (default: system temp). Never put it inside a synced folder. |

## Commands

```bash
study serve [--port 8765]            # API + web UI at http://localhost:8765/
study validate                       # check the data folder (run before calling a block done)
study search TERMS...                # search YouTube: id | duration | channel | title | views
study captions ID... [--pause 6]     # download YouTube captions into <data>/transcripts (rate-limited by YouTube)
study captions --text ID             # print a stored transcript with timestamps
study transcribe ID... [--model small] [--pause 20] [--overwrite]
                                     # local speech recognition, ONE video at a time; the audio is deleted afterwards
```

`python -m study_app <command>` works too (set `PYTHONPATH=src` when running from a clone without installing).

### About `study transcribe`

For each video it downloads **only the audio** (m4a, about 1 MB per minute) into `STUDY_WORK_DIR`, transcribes it with faster-whisper on the CPU, writes `<data>/transcripts/<id>.json` and **deletes the audio**. Measured: about 4x the video duration with the `small` model on a 16-core CPU; the first run downloads the model (~0.5 GB, cached by Hugging Face). A YouTube `403` can be transient: retry that video alone. YouTube's terms generally forbid downloading videos without the author's permission: use it for personal study, few videos, never keep or share the audio.

`study captions` is much faster but YouTube blocks the IP after roughly 15 consecutive requests (`IpBlocked`); use `transcribe` when that happens.

## Data folder

```
config.json                   list of blocks
progress.json                 written ONLY by the API
transcripts/<videoId>.json    {lang, generated, duration, source, title, segments: [[second, "text"], ...]}
figures/                      images used by readings and questions
block-1/block.json            sections -> items (video | markdown | pdf | link | questions)
block-1/*.md, *.pdf           readings
block-1/*-questions.json      question sets
```

Every path is relative to the file that contains it and must stay inside the data folder. Full schema: [docs/data-model.md](docs/data-model.md).

## API

| Route | Does |
| :-- | :-- |
| `GET /api/config` | returns `config.json` |
| `GET /api/content/<path>` | reads a file inside the data folder (never outside it) |
| `GET /api/progress` | full state `{items, answers, notes}` |
| `PUT /api/progress/items/<block>/<item>` | `{"done": true}` |
| `PUT /api/progress/answers/<block>/<item>/<question>` | `{"chosen": ["a"], "correct": true}` |
| `DELETE /api/progress/answers/<block>/<item>/<question>` | removes the answer |
| `PUT /api/progress/notes/<block>/<item>` | `{"text": "..."}` (empty text deletes the note) |

Every write saves `progress.json` atomically and returns the full updated state. **Limits (by design):** localhost only (`127.0.0.1`), no authentication, one user, last write wins. Renaming an item or question id drops its progress (the key changes). The API does not edit content; content is edited as files. Transcription is deliberately a CLI, not an API route.

## UI behaviour

Opening an item by click marks it done (it can be unmarked on the page); optional items do not count and are skipped by "PRÓXIMO"; when the tab regains focus the UI re-reads the API state; if the API is down the UI shows a red banner and saves nothing.

## Develop

```bash
pip install -e ".[dev]"
pytest
```
