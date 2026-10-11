# Data model

All files live in the data folder (`STUDY_DATA_DIR`). Paths are relative to the file that contains them and must stay inside the folder. JSON keys are English; the **values the student reads** (titles, goals, explanations) are Portuguese.

## config.json

```json
{
  "schema": "config/v2",
  "title": "Estudo · Aprendizado de Máquina",
  "blocks": [ { "id": "block-1", "title": "Bloco 1 · …", "file": "block-1/block.json" } ]
}
```

## block.json

```json
{
  "schema": "block/v2", "id": "block-1", "title": "…", "description": "…",
  "sections": [ { "id": "lesson-1", "title": "Aula 1 · …", "items": [ /* in study order */ ] } ]
}
```

The order of `sections[].items[]` **is the study sequence**. The first item that is not done (and not optional) is marked "PRÓXIMO".

### Items

| Field | Required | Meaning |
| :-- | :-- | :-- |
| `id` | yes | Unique within the block. It is the progress key (`<block>/<item>`): **do not rename after publishing**. |
| `type` | yes | `video`, `markdown`, `pdf`, `link` or `questions` |
| `title` | yes | Menu and page title |
| `goals` / `goalsTitle` | no | List of "what you should leave knowing" (inline Markdown) / custom heading |
| `warnings` | no | List of points where a video diverges from the course slides (yellow box) |
| `note` | no | Free-text box shown above the content |
| `optional` | no | `true`: not counted in the progress bar and skipped by "PRÓXIMO" |
| `duration`, `channel` | no | Shown in the menu |

By type:

- **`video`** — `url` (YouTube; embedded with youtube-nocookie), `start`/`end` in seconds (optional) **or** `clips`: `[{ "start", "end", "slides", "note" }]` (one button per clip); `transcript`: path to a transcript JSON (the page shows a card with the beginning, "Ver mais" and clickable timestamps; clips are highlighted); `review`: result of reading the transcript against the slides: `{ "badge", "covers": [..], "notCovered", "profile": [..], "verdict" }` — the `badge` is the green label (e.g. "transcrição lida · só os trechos indicados"); a video **without `review`** shows "transcrição ainda não lida"; `summary`: optional Markdown below the video.
- **`markdown`** — `path` to a `.md` file **or** `content` (Markdown inside the JSON). Images and links inside are relative to the `.md`.
- **`pdf`** — `path`.
- **`link`** — `url`, optional `description`.
- **`questions`** — `path` to a question-set JSON. The item becomes done automatically when every question is answered.

## Question sets (`*-questions.json`)

```json
{
  "schema": "questions/v2", "id": "block-1-lesson-1", "title": "…", "instructions": "optional Markdown",
  "questions": [
    {
      "id": "q01", "label": "short topic (optional)",
      "type": "single",
      "prompt": "Markdown; may contain tables and images: ![](../figures/f01.png)",
      "promptFile": "q01-prompt.md",
      "options": [
        { "id": "a", "text": "…", "correct": true,  "explanation": "why it is right" },
        { "id": "b", "text": "…", "correct": false, "explanation": "why it is wrong" }
      ],
      "generalExplanation": "the central idea of the question"
    }
  ],
  "closing": "optional Markdown after the last question"
}
```

- `type: "single"` — exactly one `correct: true` (radio buttons). `type: "multiple"` — two or more correct; it only counts as right if the chosen set equals the correct set.
- Use `prompt` (inline) **or** `promptFile` (a `.md` file with images); the file wins if both exist.
- **Every option must have an `explanation`, right or wrong**, and every question a `generalExplanation`: after answering, the UI shows the explanation of all options, because that is where the learning happens. `study validate` enforces this.
- Option text and explanations accept inline Markdown.

## Transcript files (`transcripts/<videoId>.json`)

```json
{ "lang": "pt", "generated": true, "duration": 314, "source": "transcribed locally with faster-whisper (small) …",
  "title": "…", "segments": [[0, "text"], [4, "text"]] }
```

Written by `study captions` (YouTube captions) or `study transcribe` (local Whisper); the UI reads `segments`, `lang`, `generated` and `source`.

## progress.json (owned by the API; never edit by hand)

```json
{
  "items":   { "block-1/a1-v1": { "done": true, "at": "2026-10-11T13:04:00+00:00" } },
  "answers": { "block-1/a1-q":  { "q01": { "chosen": ["b"], "correct": true, "at": "…" } } },
  "notes":   { "block-1/a1-v1": "free text" }
}
```

## Adding a block

1. Create `block-N/block.json` (copy another block) and its `.md` / `*-questions.json` files.
2. Add the block to `config.json`.
3. Copy any figures into `figures/`; reference them as `../figures/x.png` from inside a block folder.
4. Run `study validate`.
