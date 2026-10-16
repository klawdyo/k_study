# 09 · Templates

Esqueletos para copiar. Troque o conteúdo, mantenha as chaves. Comentários `//` e `<...>` **não existem em JSON válido**: remova antes de gravar.

## `trail.json`

```json
{
  "schema": "trail/v1",
  "id": "<slug>",
  "title": "<Título da trilha>",
  "description": "<1 a 2 frases: o que a pessoa vai saber ao final>",
  "language": "pt-BR",
  "level": "iniciante",
  "tags": ["<assunto>", "<objetivo>"],
  "createdAt": "<AAAA-MM-DD>",
  "cover": "cover.webp",
  "blocks": [
    { "id": "block-1", "title": "Bloco 1 · <tema>", "file": "block-1/block.json" }
  ]
}
```

`cover` é opcional (imagem 1200×630, png, jpg ou webp, até 1 MB, dentro da pasta da trilha); remova a linha se não houver capa.

## `block-1/block.json` (um item de cada tipo)

```json
{
  "schema": "block/v2",
  "id": "block-1",
  "title": "Bloco 1 · <tema>",
  "description": "<o que o bloco ensina>",
  "sections": [
    {
      "id": "aula-1",
      "title": "Aula 1 · <tema>",
      "items": [
        {
          "id": "a1-v1",
          "type": "video",
          "title": "<título do vídeo>",
          "channel": "<canal>",
          "duration": "12:30",
          "url": "https://www.youtube.com/watch?v=<ID de 11 caracteres>",
          "goals": ["<o que sair sabendo> (slide 5)."],
          "warnings": ["<onde o vídeo diverge do material ou simplifica>"],
          "clips": [
            { "start": 24, "end": 196, "slides": "5–6", "note": "<o que ensina; o que pular>" }
          ],
          "transcript": "../transcripts/<ID>.json",
          "review": {
            "badge": "transcrição lida · só os trechos indicados",
            "covers": ["00:24–03:16 — <o que é explicado> (slides 5–6)"],
            "notCovered": "<o que o vídeo não explica e o material pede>",
            "profile": ["**Nível:** iniciante.", "**Qualidade:** <fala, legenda, ritmo>."],
            "verdict": "Aprovar só o trecho 00:24–03:16 (2:52). Item obrigatório."
          }
        },
        {
          "id": "a1-v2",
          "type": "video",
          "title": "<vídeo complementar>",
          "url": "https://www.youtube.com/watch?v=<ID>",
          "optional": true,
          "note": "Opcional: outro exemplo do mesmo assunto.",
          "start": 0,
          "end": 600
        },
        { "id": "a1-read", "type": "markdown", "title": "Leitura: Aula 1 do zero", "path": "aula-1-do-zero.md" },
        { "id": "a1-extra", "type": "markdown", "title": "Resumo", "content": "Markdown curto dentro do próprio JSON." },
        { "id": "a1-pdf", "type": "pdf", "title": "Folha de apoio", "path": "../materials/folha.pdf", "optional": true },
        { "id": "a1-link", "type": "link", "title": "Documentação oficial", "url": "https://exemplo.org/doc", "description": "Para consulta.", "optional": true },
        { "id": "a1-q", "type": "questions", "title": "Questões da Aula 1", "path": "lesson-1-questions.json" }
      ]
    }
  ]
}
```

Ordem dentro da aula: vídeos (na ordem do material) → leitura → questões. Um bloco de código/guia entra como seção própria ("Fechamento de código").

## `lesson-1-questions.json` (uma questão de cada tipo)

```json
{
  "schema": "questions/v2",
  "id": "block-1-lesson-1",
  "title": "Aula 1 · Questões",
  "instructions": "Responda **antes** de ler qualquer explicação. Depois, leia a explicação de **todas** as alternativas, inclusive das que você acertou.",
  "questions": [
    {
      "id": "q01", "label": "Conceito", "type": "single",
      "prompt": "<cenário explicado> Qual afirmação está **correta**?",
      "options": [
        { "id": "a", "text": "<distrator plausível>", "correct": false, "explanation": "<por que parece certa e não é; 60 caracteres ou mais>" },
        { "id": "b", "text": "<correta>", "correct": true, "explanation": "<por que está certa>" },
        { "id": "c", "text": "<distrator plausível>", "correct": false, "explanation": "<o erro de raciocínio>" },
        { "id": "d", "text": "<distrator plausível>", "correct": false, "explanation": "<o erro de raciocínio>" }
      ],
      "generalExplanation": "**Ideia central:** <regra que ensina>."
    },
    {
      "id": "q02", "label": "Várias corretas", "type": "multiple",
      "prompt": "Quais **duas ou mais** afirmações estão corretas?",
      "options": [
        { "id": "a", "text": "…", "correct": true, "explanation": "…" },
        { "id": "b", "text": "…", "correct": true, "explanation": "…" },
        { "id": "c", "text": "…", "correct": false, "explanation": "…" },
        { "id": "d", "text": "…", "correct": false, "explanation": "…" }
      ],
      "generalExplanation": "…"
    },
    {
      "id": "q03", "label": "Tabela", "type": "single",
      "prompt": "A tabela mostra os dados abaixo (cenário nosso, ilustrativo).\n\n| item | valor | situação |\n| :-- | --: | :-- |\n| A | 10 | ok |\n| B | — | ausente |\n\nQual o tratamento adequado para `B`?",
      "options": [ { "id": "a", "text": "…", "correct": true, "explanation": "…" }, { "id": "b", "text": "…", "correct": false, "explanation": "…" } ],
      "generalExplanation": "…"
    },
    {
      "id": "q04", "label": "Código com erro de lógica", "type": "single",
      "promptFile": "q04-prompt.md",
      "options": [ { "id": "a", "text": "…", "correct": true, "explanation": "…" }, { "id": "b", "text": "…", "correct": false, "explanation": "…" } ],
      "generalExplanation": "**Ideia central:** <a regra>.\n\n```python\n# código corrigido (executado por você)\n```"
    },
    {
      "id": "q05", "label": "Ordem das ações", "type": "single",
      "prompt": "Um colega propôs esta sequência:\n\n1. <passo>\n2. <passo>\n3. <passo>\n\nA ordem está correta?",
      "options": [ { "id": "a", "text": "…", "correct": false, "explanation": "…" }, { "id": "b", "text": "…", "correct": true, "explanation": "…" } ],
      "generalExplanation": "…"
    }
  ],
  "closing": "Se errou algo, volte à seção correspondente da leitura."
}
```

(Os `options` de `q03`–`q05` aparecem abreviados com duas alternativas por economia; no arquivo real use 4, com toda alternativa explicada.) `q04-prompt.md` contém o enunciado com o bloco de código e a pergunta.

## Ficha de vídeo (`block-1/validacao-videos-aula-1.md`)

```markdown
# Validação dos vídeos da Aula 1 pela transcrição

Método: li a transcrição **inteira** de cada candidato (k_transcriptor, Whisper `small`, com erros de grafia) e comparei com os <N> tópicos de `materials/<arquivo>`. Os `mm:ss` vêm dos carimbos da transcrição (margem de poucos segundos). Não conferi nada fora das transcrições e do material. Tópicos só com figura não foram conferidos pelo texto.

Legenda: **B** cobre bem · **P** parcial · **–** não cobre · **X** diverge ou erra.

| Sigla | ID | Canal / título | Duração | Idioma |
| :-- | :-- | :-- | :-: | :-: |
| AB | <ID> | <canal> — <título> | 12:30 | pt |

## 1. Matriz tópico × vídeo

| Tópico (slides) | AB | CD |
| :-- | :-: | :-: |
| <tópico> (5–6) | B | – |

## 2. Fichas por vídeo

### <ID> — <canal> — <título> (<duração>) — aprovar só trechos

- **Cobre:** 00:24–03:16 <o que>; …
- **Não cobre:** …
- **Divergências com o material:** hh:mm <o que diz diferente>.
- **Nível e foco:** iniciante; só conceito.
- **Idioma/qualidade:** pt; fala clara; legenda com erros de grafia.
- **Trechos recomendados:** 00:24–03:16 (2:52 no total).
- **Veredito: `aprovar só os trechos acima`** — <motivo>.

## 3. Descartados e redundantes

| ID | Veredito | Motivo |
| :-- | :-- | :-- |
| <ID> | descartar | <idioma errado / não cobre / erra X em hh:mm> |
| <ID> | redundante | cobre o mesmo que <ID>, sem nada a mais |

## 4. Lacunas

Tópicos sem vídeo bom (cobertos pela leitura), com as duas rodadas de busca registradas: <lista>.
```

## `brief.md`

```markdown
# Brief da trilha <slug>

Atualizado em <AAAA-MM-DD>.

## Decisões da entrevista
| Tema | Decisão |
| :-- | :-- |
| Assunto e objetivo | <…> |
| Prazo e tempo por dia | <data; horas/dia> |
| Perfil (sabe / não sabe; profissão; analogias de qual área) | <…> |
| Idioma | pt-BR |
| Material | <arquivos em materials/; numeração usada> |
| Divisão aprovada | <bloco → aulas → tópicos> |
| Vídeos | <qtd por tópico; idioma; duração máx.; didáticos para o nível> |
| Autorização de áudio | "<frase da pessoa>" em <data> |
| Leituras | <tamanho; área das analogias> |
| Questões | <qtd por aula; tipos; com/sem cálculo; dificuldade> |
| Avaliação real | <formato; o que cobra; o que NÃO é foco> |
| Tom | <…> |
| Já estudado | <…> |

## Meta de tempo por aula
| Aula | Vídeo obrig. | Leitura | Questões | Total |
| :-- | --: | --: | --: | --: |

## Decisões durante a geração
- <AAAA-MM-DD> <decisão e motivo>

## Pendências / o que não foi verificado
- <figuras não abertas; lacunas; transcrições ilegíveis>

## Totais entregues
<blocos, aulas, vídeos (obrigatórios/opcionais), leituras, questões, tempo obrigatório>

## Auditoria
<data; achados; correções>
```
