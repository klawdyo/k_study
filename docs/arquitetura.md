# k_study — arquitetura (contrato entre as partes)

Este documento é o **contrato único** do projeto: pastas, formato dos arquivos de conteúdo, banco de dados, API, CLI e quem é dono de cada parte. Todas as partes (servidor, interface do aluno, painel do admin, specs) devem obedecê-lo. Mudou o contrato? Mude aqui primeiro.

## 1. O que é

O **k_study** serve **trilhas de aprendizagem** (cursos) criadas por agentes de IA a partir de material que uma pessoa fornece. Cada trilha tem blocos, os blocos têm aulas (vídeos com trechos, leituras, questões). Vários alunos usam o mesmo servidor; cada um tem seu próprio progresso. O admin vê estatísticas num painel à parte.

Dois processos:

| Comando | Porta | Quem usa |
| :-- | :-: | :-- |
| `kstudy serve` | 8765 | alunos (interface de estudo) |
| `kstudy admin` | 8766 | o admin (painel de estatísticas), só em `127.0.0.1` por padrão |

Projeto Python normal, **somente biblioteca padrão** (sqlite3 incluso): `py main.py serve` funciona sem instalar nada; `pip install -e .` cria o comando `kstudy`. Quem só quer estudar baixa o projeto e roda `py main.py`. Quem quer criar conteúdo abre um agente de IA no diretório: o `CLAUDE.md` e a pasta `specs/` dizem tudo o que o agente precisa. A busca, o download e a transcrição de vídeos são outro projeto (**k_transcriptor**), que o agente baixa do GitHub quando precisa (ver `specs/`).

## 1.1 Convenção de idioma (vale para o k_study e para o k_transcriptor)

- **Em inglês:** nomes de arquivos de código, módulos, funções, variáveis, classes, constantes, tabelas e colunas do banco, chaves de JSON, nomes de comandos e de opções do CLI, códigos de erro da API (`login_required`).
- **Em português do Brasil:** specs, `README.md`, `CLAUDE.md`, a interface (telas, botões, rótulos), as **mensagens vistas por pessoas** (saída e erros do CLI, textos de `--help`, mensagens de erro da API, logs de operação) e o conteúdo gerado.
- Comentários e docstrings do código: em português (termos técnicos podem ficar em inglês).
- Nomes de arquivos de documentação (`specs/*.md`, `docs/*.md`) podem ser em português.

## 2. Pastas do repositório

```text
main.py                  py main.py <comando>  (igual a: python -m k_study <comando>)
CLAUDE.md                ponto de entrada para agentes de IA
README.md                para pessoas (como rodar)
specs/                   instruções para agentes: como gerar conteúdo (entrevista, estrutura, pipeline, qualidade)
docs/arquitetura.md      este contrato;  docs/modelo-de-dados.md = formato dos arquivos de conteúdo
src/k_study/             o pacote
  cli.py                 comandos
  server.py              servidor dos alunos (HTTP + API + arquivos estáticos)
  db.py                  SQLite: esquema, migrações, consultas
  indexer.py             lê content/ e atualiza o índice no banco
  validate.py            validador de conteúdo
  admin/                 servidor e interface do painel do admin
  web/                   interface do aluno (HTML, JS, CSS)
content/<slug>/          uma pasta por trilha (ver 3)
data/k_study.db          o banco (fora do git)
tests/                   pytest, sem rede
```

Configuração: `--content-dir` (padrão `./content`) e `--db` (padrão `./data/k_study.db`), ou as variáveis `K_STUDY_CONTENT` e `K_STUDY_DB`. Não há mais tela de escolha de pasta nem `progress.json` global.

## 3. Uma trilha em disco (o que os agentes escrevem)

```text
content/<slug>/
  trail.json             manifesto da trilha (schema trail/v1)
  materials/             o que a pessoa forneceu (slides, textos), se ela quiser guardar
  block-1/block.json     um bloco (schema block/v2: seções e itens, ver docs/modelo-de-dados.md)
  block-1/*.md           leituras;  block-1/*.json  questões (schema questions/v2)
  block-1/validacao-videos-*.md   fichas de conferência dos vídeos
  transcripts/<id>.json  transcrições dos vídeos usados (formato do k_transcriptor)
  figures/               imagens usadas nas leituras
```

`slug`: só `a-z`, `0-9` e `-`; é também o nome da pasta e o id da trilha. Caminhos dentro de `block.json` são relativos à pasta do bloco (por exemplo `../transcripts/ID.json`, `../figures/x.png`).

`trail.json` (schema `trail/v1`):

```json
{ "schema": "trail/v1", "id": "aprendizagem-de-maquina", "title": "Aprendizado de Máquina",
  "description": "Quatro blocos para estudar para a prova de AM.", "language": "pt-BR", "level": "iniciante",
  "tags": ["ia", "prova"], "createdAt": "2026-10-16",
  "blocks": [ { "id": "block-1", "title": "Bloco 1 · A base e os dados", "file": "block-1/block.json" } ] }
```

Obrigatórios: `schema`, `id` (igual ao nome da pasta), `title`, `blocks`. Os demais são opcionais. Os ids de bloco, de item e de questão **nunca mudam depois de publicados** (o progresso dos alunos depende deles).

## 4. Banco de dados (SQLite, modo WAL)

O banco guarda **estado** (índice do conteúdo, alunos, progresso, estatísticas). O **corpo** das aulas (markdown, questões, transcrições, imagens) continua em arquivos e é lido sob demanda; o servidor não varre arquivos para guardar estado.

```sql
PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
CREATE TABLE meta      (key TEXT PRIMARY KEY, value TEXT);                       -- schema_version
-- índice do conteúdo (reconstruído por `kstudy sync`)
CREATE TABLE trails    (slug TEXT PRIMARY KEY, title TEXT, description TEXT, language TEXT, level TEXT,
                        tags TEXT, manifest_mtime REAL, synced_at TEXT);
CREATE TABLE blocks    (trail TEXT, block_id TEXT, title TEXT, position INTEGER, file TEXT,
                        PRIMARY KEY (trail, block_id));
CREATE TABLE items     (trail TEXT, block_id TEXT, item_id TEXT, section TEXT, position INTEGER, type TEXT,
                        title TEXT, path TEXT, optional INTEGER DEFAULT 0, minutes REAL,
                        PRIMARY KEY (trail, block_id, item_id));              -- type: video|markdown|pdf|link|questions
-- alunos
CREATE TABLE students  (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, created_at TEXT, last_seen_at TEXT);
CREATE TABLE sessions  (token_hash TEXT PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id),
                        created_at TEXT, last_seen_at TEXT, user_agent TEXT);
-- progresso (por aluno)
CREATE TABLE progress  (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, done INTEGER, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
CREATE TABLE answers   (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, question_id TEXT,
                        chosen TEXT, correct INTEGER, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id, question_id));   -- chosen: JSON ["a","c"]
CREATE TABLE notes     (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, text TEXT, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
-- estatísticas: uma linha por visita a um item
CREATE TABLE visits    (id INTEGER PRIMARY KEY, student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT,
                        started_at TEXT, seconds INTEGER DEFAULT 0, last_beat_at TEXT);
CREATE INDEX visits_student ON visits(student_id, trail); CREATE INDEX visits_item ON visits(trail, block_id, item_id);
```

Datas em ISO 8601 UTC (`2026-10-16T14:03:00+00:00`). Progresso e respostas **não** são apagados quando um item some do conteúdo (se ele voltar, o aluno recupera). Migrações: `meta.schema_version` e uma lista de funções em `db.py`.

## 5. Identidade do aluno (cookie + e-mail)

- Cookie `kstudy_sid`: token aleatório (32 bytes, `secrets.token_urlsafe`), `HttpOnly; SameSite=Lax; Path=/; Max-Age=31536000`. O banco guarda só o **hash SHA-256** do token (`sessions`).
- Sem cookie válido, a interface mostra a tela "Informe seu e-mail". `POST /api/login {email}`: se o e-mail existe, **vincula este navegador** a ele; se não existe, **cadastra**. Assim o aluno acompanha o progresso de várias máquinas informando o mesmo e-mail. E-mail normalizado (`strip` e minúsculas) e validado de forma simples.
- **Não há verificação do e-mail** (nem senha): quem digita o e-mail de outra pessoa vê o progresso dela. É aceitável para estudo; está documentado no README. Verificação por código pode vir depois.
- Rotas de progresso e de rastreio exigem login (`401 login_required`).

## 6. API do aluno (servidor `kstudy serve`)

JSON UTF-8. Erros: `{"error": "<codigo>", "message": "<texto>"}` com o status HTTP adequado. Sem cache (`Cache-Control: no-store`).

| Rota | Corpo / resposta |
| :-- | :-- |
| `GET /api/me` | `{"student": {"email": "..."} \| null}` |
| `POST /api/login` `{email}` | `{"student": {...}, "created": true\|false}` e cabeçalho `Set-Cookie` |
| `POST /api/logout` | `{"ok": true}`; apaga a sessão e o cookie |
| `GET /api/trails` | lista de `{slug,title,description,language,level,tags,blocks,items,requiredItems,minutes, done (itens feitos pelo aluno logado, 0 se anônimo)}` |
| `GET /api/trails/<slug>` | o `trail.json` |
| `GET /api/trails/<slug>/files/<caminho>` | qualquer arquivo dentro da pasta da trilha (blocos, markdown, questões, transcrições, imagens); `404` se sair da pasta |
| `GET /api/trails/<slug>/progress` | `{items, answers, notes}` do aluno (formato abaixo) |
| `PUT /api/trails/<slug>/progress/items/<block>/<item>` `{done}` | estado completo atualizado |
| `PUT /api/trails/<slug>/progress/answers/<block>/<item>/<question>` `{chosen, correct}` | idem |
| `DELETE …/progress/answers/<block>/<item>/<question>` | idem |
| `PUT …/progress/notes/<block>/<item>` `{text}` | idem (texto vazio apaga a anotação) |
| `POST /api/track` | rastreio de tempo (abaixo) |

Formato do estado de progresso (igual ao `progress.json` antigo, escopo trilha+aluno): `{"items": {"block/item": {"done": true, "at": "..."}}, "answers": {"block/item": {"q01": {"chosen": ["a"], "correct": true, "at": "..."}}}, "notes": {"block/item": "texto"}}`.

Rastreio (`POST /api/track`, exige login):
- `{"event":"open","trail":"..","block":"..","item":".."}` → cria uma `visit` e responde `{"visit": 123}`.
- `{"event":"beat","visit":123,"seconds":10}` → soma `seconds` (limitado a 1..30 por chamada) à visita do próprio aluno.
- `{"event":"leave","visit":123,"seconds":3}` → idem a `beat` (enviado com `navigator.sendBeacon` ao sair).
- A interface envia `beat` a cada 10 s **somente com a aba visível e em foco**. "Só abriu e saiu" = visita com `seconds < 10`.

Arquivos estáticos da interface (`web/`) em `/`. `GET /` serve `index.html`. A interface é uma SPA com rotas por hash: `#/` (grade de trilhas), `#/t/<slug>` (trilha: bloco, aula, etc.).

Segurança do servidor dos alunos: verifica o cabeçalho `Host` (localhost, `127.0.0.1`, `::1`; com `--lan` também IPs e o nome do computador); com `--lan` só aceita clientes de redes privadas; protege contra caminho fora da pasta; sem CORS. `--lan` escuta em todas as interfaces e **continua existindo**.

## 7. Painel do admin (`kstudy admin`)

Servidor separado, porta 8766, **somente `127.0.0.1`** por padrão. Com `--lan` exige `--password` (ou a variável `K_STUDY_ADMIN_PASSWORD`) e pede login. Lê o mesmo banco (somente leitura). Interface própria em `src/k_study/admin/web/`: dashboard com cartões de resumo, gráficos (SVG/canvas escritos à mão, sem bibliotecas externas), tabelas ordenáveis, tema claro/escuro.

API (JSON, usada só pelo painel):

| Rota | Conteúdo |
| :-- | :-- |
| `GET /api/admin/overview` | totais: alunos, ativos em 7 dias, tempo total, visitas, trilhas; série diária de tempo e de alunos ativos (30 dias); trilhas com conclusão média |
| `GET /api/admin/students` | por aluno: e-mail, cadastro, última atividade, tempo total, itens feitos, acerto em questões |
| `GET /api/admin/students/<id>` | por trilha: itens feitos, tempo por item, visitas, "só abriu e saiu", acertos por questão |
| `GET /api/admin/trails` | por trilha: alunos, conclusão média, tempo médio |
| `GET /api/admin/trails/<slug>` | por bloco e item: alunos que abriram, tempo médio, taxa de abandono (visitas < 10 s), conclusão, acerto médio das questões (e as questões mais erradas) |

## 8. CLI

`kstudy <comando>` ou `py main.py <comando>` (sem comando = `serve`). O admin só precisa de `serve` e `admin`; o resto é para agentes.

| Comando | Para quem | O que faz |
| :-- | :-- | :-- |
| `serve [--port 8765] [--lan] [--content-dir D] [--db F]` | aluno/admin | sobe o servidor dos alunos |
| `admin [--port 8766] [--lan --password P]` | admin | sobe o painel |
| `validate [slug]` | agente | valida a estrutura de uma trilha (ou de todas); erros reprovam, heurísticas só avisam |
| `sync` | agente | reindexa `content/` no banco |
| `trails` | agente | lista as trilhas e seus números |
| `new-trail SLUG --title T [--description D]` | agente | cria `content/<slug>/` com `trail.json` e a estrutura mínima |
| `import-progress --email E --trail SLUG ARQUIVO.json` | admin | importa um `progress.json` antigo para o aluno E |

Códigos de saída: 0 ok, 1 problemas de validação, 2 erro de uso ou de ambiente.

## 9. Conteúdo inicial

O repositório já traz uma trilha pronta: `content/aprendizagem-de-maquina/` (os quatro blocos gerados para estudar aprendizado de máquina), como exemplo e conteúdo inicial. **Sem** os slides da professora (nunca distribuídos) e **sem** progresso pessoal. O admin pode apagar a pasta quando quiser (`kstudy sync` tira a trilha do índice).

## 10. Quem é dono de quê (desenvolvimento em paralelo)

| Parte | Arquivos |
| :-- | :-- |
| Servidor e CLI | `main.py`, `pyproject.toml`, `src/k_study/{cli,server,db,indexer,validate,__init__,__main__}.py`, `tests/` |
| Interface do aluno | `src/k_study/web/**` |
| Painel do admin | `src/k_study/admin/**` (servidor `admin/server.py` com `run(db_path, port, lan, password)` e `admin/web/**`) e testes `tests/test_admin.py` |
| Specs para agentes | `CLAUDE.md`, `README.md`, `specs/**`, `docs/modelo-de-dados.md` |
| Conteúdo inicial | `content/**` |

Este arquivo (`docs/arquitetura.md`) é do coordenador.
