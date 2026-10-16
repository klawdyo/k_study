# k_study — arquitetura (contrato entre as partes) · revisão 2

Este documento é o **contrato único** do projeto: pastas, formato dos arquivos de conteúdo, banco de dados, autenticação, API, CLI, segurança e quem é dono de cada parte. Todas as partes devem obedecê-lo. Mudou o contrato? Mude aqui primeiro, no mesmo commit.

A revisão 2 substitui a 1: login com senha, admin integrado ao mesmo servidor (sem segunda porta), CSRF, rotas por id (sem acesso a arquivos por caminho), pacotes zip de trilha e de specs.

## 1. O que é

O **k_study** serve **trilhas de aprendizagem** (cursos) criadas por agentes de IA que rodam **localmente** na máquina de quem cria. Cada trilha tem blocos; os blocos têm aulas (vídeos com trechos, leituras, questões). Vários alunos usam o mesmo servidor, cada um com conta e progresso próprios. Um administrador importa trilhas (zip), ativa e desativa trilhas e vê estatísticas.

Um único processo: **`kstudy serve`** (porta 8765). Não existe servidor separado do admin: a área administrativa é uma parte do mesmo servidor, visível só para quem é admin.

Projeto Python normal, **somente biblioteca padrão** (sqlite3, hashlib.scrypt, zipfile): `py main.py serve` funciona sem instalar nada; `pip install -e .` cria o comando `kstudy`. A busca, o download e a transcrição de vídeos são outro projeto (**k_transcriptor**), usado pelo agente local para criar o conteúdo.

## 1.1 Convenção de idioma (vale para o k_study e para o k_transcriptor)

- **Em inglês:** nomes de arquivos de código, módulos, funções, variáveis, classes, constantes, tabelas e colunas do banco, chaves de JSON, nomes de comandos e de opções do CLI, códigos de erro da API (`login_required`).
- **Em português do Brasil:** specs, `README.md`, `CLAUDE.md`, a interface (telas, botões, rótulos), as **mensagens vistas por pessoas** (saída e erros do CLI, `--help`, mensagens de erro da API, logs de operação) e o conteúdo gerado.
- Comentários e docstrings do código: em português (termos técnicos podem ficar em inglês).
- Commits: atômicos, mínimos, em Conventional Commits (tipo em inglês, descrição em português).

## 2. Pastas do repositório

```text
main.py                  py main.py <comando>  (igual a: python -m k_study <comando>)
.env                     segredos locais (NUNCA vai para o git; criado no primeiro uso, ver 5)
CLAUDE.md                ponto de entrada para agentes de IA
README.md                para pessoas
specs/                   instruções para agentes: como criar uma trilha (entrevista, estrutura, pipeline, qualidade)
docs/arquitetura.md      este contrato;  docs/modelo-de-dados.md = formato dos arquivos de conteúdo
src/k_study/             o pacote
  cli.py                 comandos
  server.py              servidor (HTTP, API, arquivos estáticos)
  security.py            .env, senhas, CSRF, limite de tentativas, cabeçalhos, validações
  db.py                  SQLite: esquema, migrações, consultas
  indexer.py             lê content/ e atualiza o índice (trilhas, blocos, aulas, arquivos permitidos)
  packages.py            pacotes zip: importar trilha, empacotar trilha, zip das specs
  validate.py            validador de conteúdo
  admin/queries.py       consultas das estatísticas
  admin/web/             páginas da área administrativa (servidas em /admin/, só para admin)
  web/                   interface do aluno
content/<slug>/          uma pasta por trilha (ver 3)
data/k_study.db          o banco (fora do git)
tests/                   pytest, sem rede
```

Configuração: `--content-dir` (padrão `./content`), `--db` (padrão `./data/k_study.db`), `--env` (padrão `./.env`); variáveis `K_STUDY_CONTENT`, `K_STUDY_DB`, `K_STUDY_ENV`, `K_STUDY_SPECS_ROOT` (pasta de onde saem as specs do zip; padrão: a raiz do projeto), `K_STUDY_HTTPS=1` (marca cookies `Secure` quando houver HTTPS na frente), `K_STUDY_HOST` (endereço em que escuta; `--host`; padrão `127.0.0.1`, em Docker `0.0.0.0`), `K_STUDY_ALLOWED_HOSTS` (nomes de host aceitos no cabeçalho `Host`, separados por vírgula, além de localhost), `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` (entrada com o Google, seção 5.1).

## 3. Uma trilha em disco (o que os agentes escrevem)

```text
content/<slug>/
  trail.json             manifesto (schema trail/v1)
  cover.webp|png|jpg     capa opcional da trilha (campo "cover" do manifesto; até 1 MB)
  materials/             o que a pessoa forneceu, se quiser guardar
  block-1/block.json     um bloco (schema block/v2; ver docs/modelo-de-dados.md)
  block-1/*.md           leituras;  block-1/*.json  questões (questions/v2)
  block-1/validacao-videos-*.md   fichas de conferência dos vídeos
  transcripts/<id>.json  transcrições dos vídeos usados
  figures/               imagens usadas nas leituras e questões
```

`trail.json` (`trail/v1`): obrigatórios `schema`, `id` (= nome da pasta, só `a-z0-9-`), `title`, `blocks`; opcionais `description`, `language`, `level`, `tags`, `createdAt`, **`cover`** (caminho relativo de uma imagem dentro da pasta da trilha; png, jpg ou webp; 1200×630 recomendado). Ids de bloco, item e questão **nunca mudam depois de publicados**.

### 3.1 Pacote zip de uma trilha (importação)

Um `.zip` com **uma única pasta de topo `<slug>/`** que contém a trilha exatamente como em 3. Regras (o importador recusa o pacote inteiro se alguma falhar):
- entradas só com caminho relativo normalizado: sem `..`, sem `/` inicial, sem `\`, sem letra de unidade, sem bytes de controle; sem links simbólicos; sem entradas fora de `<slug>/`;
- extensões permitidas: `.json .md .png .jpg .jpeg .webp .gif .pdf .txt` (SVG, HTML, JS e executáveis são recusados);
- limites: ≤ 100 MB compactado, ≤ 300 MB descompactado, ≤ 5000 arquivos, razão de compressão por arquivo ≤ 200;
- depois de extrair numa pasta temporária, `validate` precisa passar **sem problemas** (avisos são mostrados); o conteúdo de `.md` e `.json` é varrido e recusado se tiver `<script`, `<iframe`, `javascript:`, `data:text/html`, `onerror=`/`onload=`;
- se o slug já existir, é recusado, a menos que o admin peça `replace` (a trilha é trocada de forma atômica; o progresso dos alunos é mantido).

## 4. Banco de dados (SQLite, modo WAL, esquema v2)

O banco guarda **estado**. O **corpo** das aulas (markdown, questões, transcrições, imagens) continua em arquivos, lidos sob demanda **somente pelas rotas por id** (seção 7).

```sql
PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
CREATE TABLE meta      (key TEXT PRIMARY KEY, value TEXT);                       -- schema_version = 2
-- índice do conteúdo (reconstruído por `kstudy sync`)
CREATE TABLE trails    (slug TEXT PRIMARY KEY, title TEXT, description TEXT, language TEXT, level TEXT, tags TEXT,
                        cover TEXT, active INTEGER NOT NULL DEFAULT 1, manifest_mtime REAL, synced_at TEXT);
CREATE TABLE blocks    (trail TEXT, block_id TEXT, title TEXT, position INTEGER, file TEXT, PRIMARY KEY (trail, block_id));
CREATE TABLE items     (trail TEXT, block_id TEXT, item_id TEXT, section TEXT, position INTEGER, type TEXT, title TEXT,
                        path TEXT, transcript TEXT, optional INTEGER DEFAULT 0, minutes REAL,
                        PRIMARY KEY (trail, block_id, item_id));              -- type: video|markdown|pdf|link|questions
CREATE TABLE assets    (trail TEXT, path TEXT, kind TEXT, size INTEGER, PRIMARY KEY (trail, path));
                        -- lista PERMITIDA de arquivos servíveis: kind = block|item|transcript|figure|cover
-- contas
CREATE TABLE students  (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
                        password_hash TEXT NOT NULL, is_admin INTEGER NOT NULL DEFAULT 0, created_at TEXT, last_seen_at TEXT);
CREATE TABLE sessions  (token_hash TEXT PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                        csrf_token TEXT NOT NULL, created_at TEXT, last_seen_at TEXT, expires_at TEXT, user_agent TEXT);
CREATE TABLE login_attempts (key TEXT NOT NULL, at TEXT NOT NULL);               -- limite de tentativas (key = hash de e-mail+IP, ou do IP)
CREATE TABLE audit_log (id INTEGER PRIMARY KEY, at TEXT, student_id INTEGER, action TEXT, detail TEXT, ip TEXT);
-- progresso (por aluno), respostas, anotações, visitas: iguais à revisão 1
CREATE TABLE progress  (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, done INTEGER, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
CREATE TABLE answers   (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, question_id TEXT, chosen TEXT,
                        correct INTEGER, at TEXT, PRIMARY KEY (student_id, trail, block_id, item_id, question_id));
CREATE TABLE notes     (student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT, text TEXT, at TEXT,
                        PRIMARY KEY (student_id, trail, block_id, item_id));
CREATE TABLE visits    (id INTEGER PRIMARY KEY, student_id INTEGER, trail TEXT, block_id TEXT, item_id TEXT,
                        started_at TEXT, seconds INTEGER DEFAULT 0, last_beat_at TEXT);
```

Migração v1 → v2: contas antigas (sem senha) ficam com `password_hash=''` e `name=''`; no próximo login precisam **definir senha e nome** (fluxo de cadastro). Datas em ISO 8601 UTC. Progresso nunca é apagado quando um item some do conteúdo. SQL **sempre parametrizado**.

## 5. Contas, senhas e sessões

- **`.env`**: se não existir (ou não tiver `K_STUDY_SECRET`), o servidor o cria no primeiro uso com `K_STUDY_SECRET=<64 hex de secrets.token_hex(32)>`, permissões `0600` quando o sistema permitir. **Está no `.gitignore`.** É lido por um parser próprio (`CHAVE=valor`, comentários `#`), sem sobrescrever variáveis já definidas no ambiente. O segredo nunca é impresso nem logado. Se o segredo mudar, as senhas existentes deixam de valer (documentar: fazer backup do `.env` junto com o banco).
- **Senhas (nunca em texto puro, nunca reversíveis):** `scrypt` (`hashlib.scrypt`, n=2^15, r=8, p=1, sal aleatório de 16 bytes por conta) aplicado a `HMAC-SHA256(K_STUDY_SECRET, senha)` (o segredo age como *pepper*); formato guardado `scrypt$n$r$p$<sal b64>$<hash b64>`; comparação com `hmac.compare_digest`; rehash se os parâmetros mudarem. Política: 8 a 128 caracteres, diferente do e-mail. Quando o e-mail não existe, fazer um hash fictício para igualar o tempo de resposta do login.
- **E-mail:** `strip`, minúsculas, validação simples (uma `@`, domínio com ponto, ≤ 254 caracteres, sem espaços nem controle). **Nome:** 1 a 80 caracteres, sem controle.
- **Fluxo do aluno (sem confirmação por e-mail):**
  1. A tela pede só o e-mail → `POST /api/auth/check {email}` → `{exists, firstUser}`.
  2. Se existe: pede a senha → `POST /api/auth/login`.
  3. Se não existe: pede senha, confirmação da senha e nome → `POST /api/auth/register`.
  4. **Se ainda não há nenhuma conta, o primeiro cadastro vira administrador (`is_admin = 1`)**, decidido dentro de uma transação (sem corrida). Depois disso ninguém vira admin pela interface (CLI local `kstudy set-admin EMAIL` existe para recuperação).
- **Sessão:** cookie `kstudy_sid` (token de 32 bytes; o banco guarda só o SHA-256), `HttpOnly; SameSite=Strict; Path=/; Max-Age=2592000` (+ `Secure` com `K_STUDY_HTTPS=1`); validade deslizante de 30 dias e absoluta de 90; o token é **trocado a cada login** (fixação de sessão); logout apaga a sessão no servidor.
- **Mostrar sempre nome e e-mail** em qualquer lugar que identifique o aluno (cabeçalho, tabelas do admin, detalhes).
- **Limite de tentativas:** `check`, `login` e `register` limitados a 5 falhas por 15 min por (e-mail+IP) e 30 por IP → `429 too_many_attempts` com `Retry-After`.

### 5.1 Entrada com o Google (OAuth 2.0 / OpenID Connect, opcional)

- **Só existe se `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` estiverem preenchidas** (no `.env` ou no ambiente). `GET /api/auth/me` devolve `oauth: {"google": bool}` e a tela de entrada só mostra o botão "Entrar com o Google" quando for `true`. Sem as duas variáveis, as rotas respondem `404`. O `.env` criado pelo servidor traz as duas **vazias**, com o comentário de como configurar; o `.env.example` mostra o mesmo.
- **O endereço de retorno é fixo no sistema: `/auth/oauth/google/callback`. Ele NÃO é variável de ambiente nem vai no `.env`.** Quem configura o Google informa lá, em "URIs de redirecionamento autorizados", o endereço do servidor seguido desse caminho (por exemplo `http://localhost:8765/auth/oauth/google/callback`). O servidor monta o `redirect_uri` com `http` (ou `https` com `K_STUDY_HTTPS=1`) e o `Host` da requisição, que já passou pela validação de host.
- Rotas (sem sessão, `GET`): `/auth/oauth/google/start` (redireciona ao Google) e `/auth/oauth/google/callback` (recebe `code` e `state`; responde `302` para `/`, ou para `/?oauth_error=<chave>` com as chaves `denied`, `invalid_state`, `failed`, `unverified`, `too_many`; a interface só mostra mensagens fixas).
- Fluxo de código com **PKCE (S256)**, `state` e `nonce`, guardados num cookie assinado com HMAC do segredo (`kstudy_oauth`; `HttpOnly; SameSite=Lax; Path=/auth/oauth/; Max-Age=600`; Lax porque o Google devolve a pessoa por redirecionamento de outro site). O código é trocado por `id_token` no endpoint de token do Google (única requisição de saída do servidor, a endereços fixos) e conferido: `aud`, `iss`, `exp`, `nonce` e `email_verified`.
- A conta é achada pelo e-mail (normalizado). Se não existir, é criada com o nome do Google e o hash de senha `oauth$google` (nunca confere como senha e **não** é "conta sem senha": não pode ser reivindicada por `register`); o primeiro cadastro, por qualquer meio, vira administrador. Conta existente com senha entra sem mudar a senha; conta antiga sem senha passa a ter o hash `oauth$google`. Auditoria: `login_oauth` e `login_oauth_failed`; falhas contam no limite por endereço.

## 6. CSRF e cabeçalhos

- Toda requisição que muda estado (`POST`, `PUT`, `PATCH`, `DELETE`) exige o cabeçalho **`X-CSRF-Token`** igual ao token da sessão (`sessions.csrf_token`), comparado com `hmac.compare_digest`; sem ele, `403 csrf_failed`. `GET /api/auth/me` devolve `csrfToken`.
- Antes do login (check, login, register) vale um **token pré-login**: o servidor define o cookie `kstudy_pre` (valor aleatório; `HttpOnly; SameSite=Strict`) e o token é `HMAC(K_STUDY_SECRET, valor)`, também devolvido por `/api/auth/me`; o mesmo cabeçalho é exigido.
- Exceção: `POST /api/track` com `navigator.sendBeacon` (que não envia cabeçalhos) aceita o token no corpo JSON (campo `csrf`).
- Cabeçalho `Origin` (quando presente) deve ser o próprio host; escritas exigem `Content-Type: application/json` (exceto o upload do zip: `application/zip`); corpo JSON ≤ 1 MB (`413`).
- Todas as respostas: `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-src https://www.youtube-nocookie.com https://www.youtube.com; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` (o player do YouTube exige o cabeçalho `Referer`; para outros sites sai só a origem), `Cross-Origin-Resource-Policy: same-origin`, `Cache-Control: no-store` nas rotas de API.
- Host: localhost, `127.0.0.1`, `::1` e os nomes de `K_STUDY_ALLOWED_HOSTS`; com `--lan` também IPs e o nome do computador, e só clientes de rede privada. `--lan` continua escutando em `0.0.0.0`; `--host` escolhe o endereço de escuta sem restringir clientes (uso em Docker e atrás de proxy).

## 7. API (JSON UTF-8; erros `{"error": "<codigo>", "message": "<texto em português>"}`)

**Não existe rota que sirva arquivo por caminho.** O conteúdo é pedido por **ids** (trilha, bloco, aula); o servidor traduz o id em arquivo consultando o índice (`items.path`, `items.transcript`, `assets`), nunca a partir de texto do usuário. Arquivos só são entregues se estiverem na lista permitida (`assets`) e com tipo conhecido; `figures/<nome>` aceita só nomes `[A-Za-z0-9._-]+` presentes na lista. Trilha inativa devolve `404` para alunos.

| Rota | Quem | Resposta |
| :-- | :-- | :-- |
| `GET /api/auth/me` | todos | `{"student": {"email","name","isAdmin"} \| null, "csrfToken": "..."}` |
| `POST /api/auth/check` `{email}` | todos | `{"exists": bool, "firstUser": bool}` |
| `POST /api/auth/login` `{email, password}` | todos | `{"student": {...}, "csrfToken"}` + `Set-Cookie` |
| `POST /api/auth/register` `{email, password, passwordConfirm, name}` | todos | `{"student": {...}, "csrfToken", "isFirstAdmin": bool}` + `Set-Cookie` |
| `POST /api/auth/logout` | logado | `{"ok": true}` |
| `GET /api/trails` | logado | trilhas ATIVAS: `{slug,title,description,language,level,tags,cover (URL ou null),blocks,items,requiredItems,minutes,done,requiredDone}`; **`done` conta TODA aula feita (obrigatória ou opcional)**; a barra de progresso é `done/items` |
| `GET /api/trails/<slug>` | logado | o `trail.json` |
| `GET /api/trails/<slug>/cover` | logado | a imagem de capa |
| `GET /api/trails/<slug>/blocks/<block>` | logado | o `block.json` |
| `GET /api/trails/<slug>/blocks/<block>/items/<item>/content` | logado | o arquivo da aula (markdown, questões ou pdf), tipo pelo item |
| `GET /api/trails/<slug>/blocks/<block>/items/<item>/transcript` | logado | a transcrição do vídeo |
| `GET /api/trails/<slug>/figures/<name>` | logado | imagem de `figures/` |
| `GET /api/trails/<slug>/progress` | logado | `{items, answers, notes}` do aluno (formato da revisão 1) |
| `PUT /api/trails/<slug>/progress/items/<block>/<item>` `{done}` etc. | logado | idem revisão 1 (itens, respostas, anotações) |
| `POST /api/track` | logado | rastreio de tempo (open/beat/leave) como na revisão 1 |
| `GET /api/admin/overview`, `/students`, `/students/<id>`, `/trails`, `/trails/<slug>` | **admin** | estatísticas (formato da revisão 1; alunos com `name` e `email`; `trails` com `active`) |
| `POST /api/admin/trails/<slug>/active` `{active: bool}` | **admin** | desativa ou reativa uma trilha (alunos deixam de vê-la; progresso fica) |
| `POST /api/admin/trails/import?replace=0\|1` corpo `application/zip` | **admin** | importa o pacote (3.1): `{"slug", "warnings": [...], "replaced": bool}` ou erro `400 invalid_package` com a lista de problemas |
| `GET /api/admin/specs.zip` | **admin** | zip gerado na hora com `CLAUDE.md`, `specs/**` e `docs/modelo-de-dados.md` lidos de `K_STUDY_SPECS_ROOT` (os MESMOS arquivos que o agente local usa) |

Sem sessão: `401 login_required`; sessão sem permissão: `403 forbidden`. Ações do admin e falhas de login vão para `audit_log`. Estáticos: `/` (interface do aluno) e `/admin/` (páginas administrativas; `403` para quem não é admin).

Rastreio (igual à revisão 1): `{"event":"open","trail","block","item"}` → `{"visit": id}`; `{"event":"beat","visit","seconds"}` (1 a 30 por chamada); `{"event":"leave","visit","seconds"}`; uma visita soma no máximo 4 h.

## 8. Interface (regras para quem a escreve)

- Rotas por hash: `#/` grade de trilhas (com **botão "Administração"** para admin), `#/t/<slug>[/<bloco>[/<aula>]]`, `#/admin...` (páginas de `/admin/`).
- Login em etapas (seção 5), com mensagens em português; sempre mostrar **nome e e-mail** do aluno.
- **Aula obrigatória × opcional:** a marca "Opcional" tem **cor própria** (chip âmbar/neutro distinto) e "Obrigatória" usa a cor de destaque; a diferença aparece no menu e no cabeçalho da aula. A **barra de progresso conta tudo** (aulas obrigatórias e opcionais).
- **Markdown seguro:** nunca inserir HTML bruto vindo do conteúdo: o renderizador escapa HTML, só aceita links `http`, `https`, `mailto`, âncoras e rotas internas, e imagens só por `/api/trails/<slug>/figures/<nome>` (reescrever `../figures/x.png` para essa rota). A CSP (seção 6) é a segunda barreira.
- Toda escrita envia `X-CSRF-Token`. Sem `localStorage` para estado.

## 9. CLI

`kstudy <comando>` ou `py main.py <comando>` (sem comando = `serve`).

| Comando | Para quem | O que faz |
| :-- | :-- | :-- |
| `serve [--port 8765] [--host H] [--lan] [--content-dir D] [--db F] [--env F]` | todos | sobe o servidor (cria o `.env` no primeiro uso); `SIGTERM` encerra limpo (Docker) |
| `validate [slug]` | agente | valida uma trilha (ou todas); erros reprovam, heurísticas só avisam |
| `new-trail SLUG --title T [--description D]` | agente | cria `content/<slug>/` com estrutura mínima |
| `pack SLUG [--out FILE]` | agente | valida e gera o pacote zip importável (3.1) |
| `import-trail FILE.zip [--replace]` | admin local | importa um pacote pela mesma rotina do upload |
| `sync [--force]` | agente | reindexa `content/` |
| `trails` | agente | lista trilhas e números |
| `set-admin EMAIL` | admin local | torna uma conta existente administradora (recuperação) |
| `reset-password EMAIL` | admin local | pede a nova senha no terminal (sem eco) e a grava |
| `import-progress --email E --trail SLUG ARQUIVO.json` | admin local | importa um `progress.json` antigo para uma conta existente |

Não existe mais o comando `admin` nem a porta 8766. Códigos de saída: 0 ok, 1 problemas de validação, 2 erro de uso ou de ambiente.

## 10. Segurança: requisitos não negociáveis (OWASP Top 10)

A01 acesso: toda rota de dados exige sessão; rotas admin exigem `is_admin`; filtros por `student_id` da sessão (nunca de parâmetro); nenhuma rota por caminho de arquivo; lista permitida de arquivos. A02 criptografia: scrypt + pepper, tokens com `secrets`, `.env` fora do git e 0600, sem segredos em log. A03 injeção: SQL parametrizado, sem `shell=True`, sem `eval`, saída HTML escapada, CSP. A04 desenho: limites de tamanho e de taxa, importação de zip em quarentena. A05 configuração: cabeçalhos de segurança, sem listagem de diretório, sem traceback ao cliente, `Server` sem versão. A06 componentes: dependências vendorizadas (`marked`) em versão sem CVE conhecida. A07 autenticação: política de senha, limite de tentativas, sessão trocada no login, expiração, logout no servidor, mensagem genérica de erro de login. A08 integridade: validação do pacote antes de registrar, extração em pasta temporária e troca atômica. A09 registro: `audit_log` de logins e ações do admin, sem senhas nem tokens. A10 SSRF: o servidor não faz requisições de saída com dados do usuário; a única saída é a troca do código OAuth, a um endereço fixo do Google, e só com o login do Google configurado.

## 11. Quem é dono de quê

| Parte | Arquivos |
| :-- | :-- |
| Núcleo (banco, segurança, rotas, indexador, CLI) | `main.py`, `pyproject.toml`, `src/k_study/{cli,server,security,db,indexer,validate,__init__,__main__}.py`, `tests/` (exceto os abaixo) |
| Pacotes zip | `src/k_study/packages.py`, `tests/test_packages.py` |
| Interface do aluno | `src/k_study/web/**` |
| Área administrativa (páginas e estatísticas) | `src/k_study/admin/**`, `tests/test_admin.py` |
| Specs e documentação | `CLAUDE.md`, `README.md`, `specs/**`, `docs/modelo-de-dados.md` |

Este arquivo (`docs/arquitetura.md`) é do coordenador.

### 11.1 Assinaturas que ligam as partes

```python
# packages.py  (stdlib apenas)
def import_trail_zip(content_dir: Path, data: bytes, replace: bool = False) -> dict   # {"slug", "warnings", "replaced"}; levanta PackageError(problems: list[str])
def pack_trail(content_dir: Path, slug: str, out_file: Path) -> list[str]               # devolve avisos; levanta PackageError se validar com problemas
def build_specs_zip(root: Path) -> bytes                                                # CLAUDE.md + specs/** + docs/modelo-de-dados.md
class PackageError(Exception): problems: list[str]
# security.py
def load_env(path: Path) -> None; def ensure_secret(path: Path) -> str
def hash_password(password: str, secret: str) -> str; def verify_password(password: str, stored: str, secret: str) -> bool
# admin/queries.py: as mesmas consultas da revisão 1, com students.name e trails.active
```
