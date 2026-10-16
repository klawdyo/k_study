# Modelo de dados dos arquivos de conteúdo

Formato exato dos arquivos que os agentes escrevem em `content/<slug>/`. O contrato do servidor (banco, API, CLI) está em `arquitetura.md`, no repositório do k_study; este arquivo detalha só os arquivos de conteúdo e é autossuficiente para quem cria trilhas. Se este texto divergir do validador (`src/k_study/validate.py`), vale o validador, e este texto deve ser corrigido.

Regras gerais:

- **Chaves JSON em inglês; valores que o aluno lê em português do Brasil** (títulos, objetivos, explicações). Arquivos em UTF-8, sem BOM.
- **Caminhos são relativos ao arquivo que os cita** e precisam ficar **dentro da pasta da trilha** (`content/<slug>/`). De um `block-N/block.json`, a transcrição é `../transcripts/ID.json` e uma figura é `../figures/x.png`.
- **Ids nunca mudam depois de publicados** (trilha, bloco, item, questão): o progresso dos alunos usa essas chaves. Renomear apaga, na prática, o progresso daquele item.
- Barra invertida em JSON precisa ser escapada (`\\`). Um `\b` ou `\t` mal escapado vira caractere de controle e o validador reprova.
- Sem LaTeX em lugar nenhum (a interface não o renderiza): use Unicode (→ ≤ ≥ × ≈ Σ √ ² μ σ).
- Markdown em linha (negrito, código, itálico) é aceito em títulos de objetivos, avisos, alternativas e explicações.

## 1. `trail.json` (schema `trail/v1`)

```json
{
  "schema": "trail/v1",
  "id": "configuracao-de-switches",
  "title": "Configuração de switches de rede",
  "description": "Texto curto exibido no cartão da trilha.",
  "language": "pt-BR",
  "level": "iniciante",
  "tags": ["redes", "trabalho"],
  "createdAt": "2026-10-16",
  "cover": "cover.webp",
  "blocks": [
    { "id": "block-1", "title": "Bloco 1 · Fundamentos", "file": "block-1/block.json" }
  ]
}
```

| Campo | Obrigatório | Regra |
| :-- | :-: | :-- |
| `schema` | sim | `"trail/v1"` |
| `id` | sim | igual ao nome da pasta; só `a-z`, `0-9`, `-` |
| `title` | sim | título exibido |
| `blocks` | sim | lista ordenada de `{id, title, file}`; `id` igual ao `id` dentro do `block.json` |
| `description`, `language`, `level`, `tags`, `createdAt` | não | exibidos na grade de trilhas e usados em filtros; `level`: `iniciante`, `intermediario` ou `avancado` (convenção, sem validação) |
| `cover` | não | **capa** da trilha: caminho relativo (à pasta da trilha) de uma imagem `png`, `jpg` ou `webp` de **até 1 MB** (recomendado 1200×630), por exemplo `"cover.webp"`. O validador confere que o arquivo existe, o tipo e o tamanho. Aparece no cartão da trilha; sem ela, a interface usa um degradê |

## 2. `block.json` (schema `block/v2`)

```json
{
  "schema": "block/v2",
  "id": "block-1",
  "title": "Bloco 1 · Fundamentos",
  "description": "O que este bloco ensina, em uma ou duas frases.",
  "sections": [
    { "id": "aula-1", "title": "Aula 1 · O que é uma VLAN", "items": [ /* na ordem de estudo */ ] }
  ]
}
```

A ordem de `sections[].items[]` **é a sequência de estudo**. O primeiro item não feito e não opcional recebe a marca "PRÓXIMO". Convenção de ordem dentro de uma aula: **vídeos (na ordem do material) → leitura → questões**.

### 2.1 Campos comuns a todos os itens

| Campo | Obrigatório | Significado |
| :-- | :-: | :-- |
| `id` | sim | único dentro do **bloco** (não da seção). Convenção: `a1-v1` (aula 1, vídeo 1), `a1-read`, `a1-q`, `code-q`. Não renomear depois de publicado. |
| `type` | sim | `video`, `markdown`, `pdf`, `link` ou `questions` |
| `title` | sim | título no menu e na página |
| `goals` | não | lista de "o que você deve sair sabendo" (Markdown em linha); cite o número do slide ou da página do material quando houver |
| `goalsTitle` | não | título alternativo da caixa de objetivos |
| `warnings` | não | lista de pontos em que o item **diverge do material** ou tem armadilha (caixa amarela) |
| `note` | não | texto livre mostrado acima do conteúdo |
| `optional` | não | `true`: a aula é marcada **"Opcional"** (cor própria na interface) e é pulada pelo "PRÓXIMO"; as demais são "Obrigatória". **A barra de progresso conta todas as aulas**, obrigatórias e opcionais |
| `duration` | não | texto exibido (`"17:29"` ou `"10 min"`); é só rótulo |
| `channel` | não | canal/autor, exibido no menu |

### 2.2 `video`

```json
{
  "id": "a1-v1", "type": "video",
  "title": "Título do vídeo (como o aluno deve reconhecê-lo)",
  "channel": "Nome do canal", "duration": "17:29",
  "url": "https://www.youtube.com/watch?v=ABCDEFGHIJK",
  "goals": ["..."], "warnings": ["..."],
  "clips": [
    { "start": 24, "end": 196, "slides": "10, 13", "note": "O que este trecho ensina; o que pular." }
  ],
  "transcript": "../transcripts/ABCDEFGHIJK.json",
  "review": {
    "badge": "transcrição lida · só os trechos indicados",
    "covers": ["00:24–03:16 — o que é dito aqui (slides 10, 13)"],
    "notCovered": "O que o vídeo não explica e o material pede.",
    "profile": ["**Nível:** iniciante, só conceito.", "**Qualidade:** fala clara, legenda com erros de grafia."],
    "verdict": "Aprovar só os trechos 00:24–03:16 e 05:06–09:50 (8:00). Item obrigatório."
  },
  "summary": "Markdown opcional exibido abaixo do vídeo."
}
```

- `url`: precisa conter um id de 11 caracteres do YouTube (`watch?v=ID` ou `youtu.be/ID`); é incorporado com `youtube-nocookie`.
- `start` / `end` (segundos, opcionais, no nível do item) **ou** `clips`: `[{start, end, slides, note}]`, um botão por trecho; `end` > `start`. `slides` é texto livre ("10, 13", "30–34"); `note` diz o que o trecho ensina e o que pular.
- `transcript`: caminho do JSON de transcrição (seção 4); o servidor o entrega por id da aula, nunca por caminho. A página mostra um cartão com o começo, "Ver mais" e horários clicáveis; os `clips` ficam em destaque.
- `review`: resultado da leitura da transcrição contra o material. `badge` = etiqueta verde; `covers` = lista de `"mm:ss–mm:ss — assunto (slides)"` (todo horário citado **tem de existir** no vídeo); `notCovered` = texto; `profile` = lista de linhas Markdown; `verdict` = texto. **Um vídeo sem `review` exibe "transcrição ainda não lida"**; `review` exige `transcript`.
- `summary`: Markdown opcional.

### 2.3 `markdown`

`path` (arquivo `.md`, relativo ao `block.json`) **ou** `content` (Markdown dentro do próprio JSON, para textos curtos). Imagens precisam existir e ficar em `figures/` (cite `../figures/nome.png`; o servidor só entrega imagens dessa pasta, com nome só de letras, números, ponto, hífen e sublinhado). **O Markdown é escapado:** HTML bruto vira texto, só links `http`, `https`, `mailto` e âncoras funcionam, e imagens de fora não aparecem. Link para outro arquivo da trilha não funciona (a aula é entregue por id).

### 2.4 `pdf`

`path` para um PDF dentro da pasta da trilha. Ele abre em outra aba (não é incorporado à página).

### 2.5 `link`

`url` e, opcionalmente, `description`.

### 2.6 `questions`

`path` para um arquivo de questões (seção 3). O item vira "feito" automaticamente quando todas as questões forem respondidas.

## 3. Arquivo de questões (schema `questions/v2`)

```json
{
  "schema": "questions/v2",
  "id": "block-1-lesson-1",
  "title": "Aula 1 · Questões",
  "instructions": "Markdown opcional mostrado no topo.",
  "questions": [
    {
      "id": "q01", "label": "tema curto (opcional)",
      "type": "single",
      "prompt": "Markdown; pode ter tabela, bloco de código e imagem ![](../figures/f01.png)",
      "promptFile": "q01-prompt.md",
      "options": [
        { "id": "a", "text": "…", "correct": true,  "explanation": "por que está certa" },
        { "id": "b", "text": "…", "correct": false, "explanation": "por que está errada" }
      ],
      "generalExplanation": "a ideia central da questão"
    }
  ],
  "closing": "Markdown opcional depois da última questão"
}
```

| Campo | Regra |
| :-- | :-- |
| `questions[].id` | único no arquivo; convenção `q01`, `q02`…; nunca muda |
| `type` | `single` (exatamente 1 `correct: true`, botões de rádio) ou `multiple` (2 ou mais corretas; só é acerto se o conjunto marcado for igual ao correto) |
| `prompt` / `promptFile` | enunciado no próprio JSON (**recomendado**). `promptFile` (`.md` ao lado) é aceito pelo validador, mas o servidor ainda **não o entrega** (a interface mostra um aviso): para enunciados longos com código, use `prompt` |
| `options[]` | `{id, text, correct, explanation}`; `id` único na questão (`a`, `b`, `c`, `d`…) |
| `options[].explanation` | **obrigatória em toda alternativa**, certa ou errada (o aprendizado está nelas) |
| `generalExplanation` | **obrigatória**: a ideia central, que ensina |
| `label`, `instructions`, `closing` | opcionais |

Imagens citadas em `prompt`, `promptFile`, `explanation` e `generalExplanation` precisam existir.

## 4. Transcrição (`transcripts/<videoId>.json`)

Formato do k_transcriptor (`ktr transcribe … --copy-to content/<slug>/transcripts`):

```json
{ "lang": "pt", "generated": true, "duration": 314, "title": "…",
  "source": "transcribed locally with faster-whisper (small, cuda) …",
  "segments": [[0, "primeira fala"], [4, "segunda fala"]] }
```

`segments` é uma lista de pares `[segundo, texto]`; `duration` em segundos (é a duração real usada nas conferências de horário). A interface lê `segments`, `lang`, `generated` e `source`. **O arquivo é uma transcrição automática de terceiros: serve ao estudo do aluno e à conferência do agente, não é redistribuído como obra.**

## 5. Outros arquivos da trilha (não são lidos pela interface)

| Arquivo | Para quê |
| :-- | :-- |
| `brief.md` | respostas da entrevista (decisões); retomar o trabalho depois. Ver `specs/01-entrevista.md` e `specs/09-templates.md` |
| `block-N/validacao-videos-aula-N.md` | ficha de conferência dos vídeos (matriz tópico × vídeo, descartados, lacunas); registro, não aparece na interface |
| `block-N/guia-*.md` | opcional: guia de leitura de código; entra no bloco como item `markdown` |
| `materials/` | material que a pessoa forneceu (**não** é lido pela interface; só entra no pacote se a pessoa quiser distribuí-lo) |
| `figures/` | imagens usadas nas leituras e questões (`png`, `jpg`, `webp` ou `gif`; é a única pasta de imagens que o servidor entrega) |
| `cover.webp` | a capa, se houver (`cover` do `trail.json`) |

## 6. O que o validador confere

Ver `specs/07-validacao-e-qualidade.md`. Em resumo: **erros** (reprovam, saída 1) para estrutura, ids, caminhos, imagens, capa (existência, tipo e tamanho), URL de vídeo, trechos com fim ≤ início, transcrição inexistente, `review` sem `transcript`, questões sem alternativa certa/explicação e caracteres de controle; **avisos** (heurísticas) para trecho além do fim do vídeo, LaTeX, posição/tamanho da alternativa correta, explicações curtas e leituras curtas.

## 7. Pacote zip da trilha

O que o administrador importa. Um `.zip` com **uma única pasta de topo `<slug>/`** que contém a trilha como descrita acima. Gere com `kstudy pack <slug>`. Regras (o servidor recusa o pacote inteiro se alguma falhar; detalhes e checklist em `specs/07-validacao-e-qualidade.md`):

- caminhos normalizados, sem `..`, sem `\`, sem links simbólicos;
- só as extensões `.json .md .png .jpg .jpeg .webp .gif .pdf .txt` (nada de SVG, HTML ou JS);
- até 100 MB compactado, 300 MB descompactado, 5000 arquivos;
- sem conteúdo ativo (`<script`, `<iframe`, `javascript:`, atributos `onerror=`...) em `.md`, `.json` e `.txt`;
- `kstudy validate` precisa passar sem problemas.

## 8. Progresso dos alunos

Não é arquivo: fica no banco (`data/k_study.db`) e só a API grava, para a conta de quem está logado. Formato devolvido por `GET /api/trails/<slug>/progress`: `{items, answers, notes}`, com chaves `"<bloco>/<item>"`. Para importar um `progress.json` do formato antigo para uma conta existente: `kstudy import-progress --email E --trail SLUG ARQUIVO.json`.
