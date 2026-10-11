# Modelo de dados

Todos os arquivos ficam na pasta de dados. Os caminhos são relativos ao arquivo que os contém e precisam ficar dentro da pasta. As **chaves JSON são em inglês**; os **valores que o estudante lê** (títulos, objetivos, explicações) são em português.

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
  "sections": [ { "id": "lesson-1", "title": "Aula 1 · …", "items": [ /* na ordem de estudo */ ] } ]
}
```

A ordem de `sections[].items[]` **é a sequência de estudo**. O primeiro item que não está feito (e não é opcional) recebe a marca "PRÓXIMO".

### Itens

| Campo | Obrigatório | Significado |
| :-- | :-- | :-- |
| `id` | sim | Único dentro do bloco. É a chave do progresso (`<bloco>/<item>`): **não renomeie depois de publicado**. |
| `type` | sim | `video`, `markdown`, `pdf`, `link` ou `questions` |
| `title` | sim | Título no menu e na página |
| `goals` / `goalsTitle` | não | Lista de "o que você deve sair sabendo" (Markdown em linha) / título alternativo da caixa |
| `warnings` | não | Lista de pontos em que um vídeo diverge dos slides da disciplina (caixa amarela) |
| `note` | não | Caixa de texto livre mostrada acima do conteúdo |
| `optional` | não | `true`: não entra na barra de progresso e é pulado pelo "PRÓXIMO" |
| `duration`, `channel` | não | Mostrados no menu |

Por tipo:

- **`video`** — `url` (YouTube; incorporado com youtube-nocookie); `start`/`end` em segundos (opcionais) **ou** `clips`: `[{ "start", "end", "slides", "note" }]` (um botão por trecho); `transcript`: caminho de um JSON de transcrição (a página mostra um cartão com o começo, "Ver mais" e horários clicáveis; os trechos recomendados ficam em destaque); `review`: resultado da leitura da transcrição comparada aos slides: `{ "badge", "covers": [..], "notCovered", "profile": [..], "verdict" }`, onde `badge` é a etiqueta verde (ex.: "transcrição lida · só os trechos indicados"); um vídeo **sem `review`** mostra "transcrição ainda não lida"; `summary`: Markdown opcional abaixo do vídeo.
- **`markdown`** — `path` de um arquivo `.md` **ou** `content` (Markdown dentro do próprio JSON). Imagens e links são relativos ao `.md`.
- **`pdf`** — `path`.
- **`link`** — `url` e, opcionalmente, `description`.
- **`questions`** — `path` de um conjunto de questões. O item vira "feito" automaticamente quando todas as questões forem respondidas.

## Conjuntos de questões (`*-questions.json`)

```json
{
  "schema": "questions/v2", "id": "block-1-lesson-1", "title": "…", "instructions": "Markdown opcional",
  "questions": [
    {
      "id": "q01", "label": "tema curto (opcional)",
      "type": "single",
      "prompt": "Markdown; pode ter tabela e imagem: ![](../figures/f01.png)",
      "promptFile": "q01-prompt.md",
      "options": [
        { "id": "a", "text": "…", "correct": true,  "explanation": "por que está certa" },
        { "id": "b", "text": "…", "correct": false, "explanation": "por que está errada" }
      ],
      "generalExplanation": "a ideia central da questão"
    }
  ],
  "closing": "Markdown opcional, depois da última questão"
}
```

- `type: "single"` — exatamente uma `correct: true` (botões de rádio). `type: "multiple"` — duas ou mais corretas; só conta como acerto se o conjunto marcado for igual ao conjunto correto.
- Use `prompt` (no próprio JSON) **ou** `promptFile` (um `.md`, com imagens); se houver os dois, vale o arquivo.
- **Toda alternativa precisa de `explanation`, certa ou errada**, e toda questão de `generalExplanation`: depois de responder, a interface mostra a explicação de todas as alternativas, porque é nelas que está o aprendizado. `study validate` confere isso.
- Texto das alternativas e explicações aceita Markdown em linha.

## Transcrições (`transcripts/<videoId>.json`)

```json
{ "lang": "pt", "generated": true, "duration": 314, "source": "transcribed locally with faster-whisper (small) …",
  "title": "…", "segments": [[0, "texto"], [4, "texto"]] }
```

Gravadas por `study captions` (legendas do YouTube) ou `study transcribe` (Whisper local). A interface lê `segments`, `lang`, `generated` e `source`.

## progress.json (da API; nunca edite à mão)

```json
{
  "items":   { "block-1/a1-v1": { "done": true, "at": "2026-10-11T13:04:00+00:00" } },
  "answers": { "block-1/a1-q":  { "q01": { "chosen": ["b"], "correct": true, "at": "…" } } },
  "notes":   { "block-1/a1-v1": "texto livre" }
}
```

## Como acrescentar um bloco

1. Crie `block-N/block.json` (copie o de outro bloco) e os arquivos `.md` e `*-questions.json` que ele cita.
2. Inclua o bloco em `config.json`.
3. Copie as figuras para `figures/`; dentro da pasta de um bloco, cite-as como `../figures/x.png`.
4. Rode `study validate`.
