# 01 · Núcleo seguro: banco v2, contas com senha, CSRF, rotas por id, CLI

**Depende de:** nada (só do contrato). **É a base das tarefas 03, 04 e 06.**

## Leia primeiro

`docs/arquitetura.md` (revisão 2, o contrato), `CLAUDE.md`, `docs/modelo-de-dados.md`, o código atual em `src/k_study/` (`server.py`, `db.py`, `indexer.py`, `validate.py`, `cli.py`, `admin/queries.py`) e `tests/`. Regras gerais: `.tasks/00-manifest.md`.

## Arquivos desta tarefa

`main.py`, `pyproject.toml`, `src/k_study/{cli,server,security,db,indexer,validate,__init__,__main__}.py`, `tests/` (exceto `test_packages.py` e `test_admin.py`, de outras tarefas).

## O que fazer

1. **`security.py`:**
   - carregar ou criar o `.env` (`K_STUDY_SECRET` com `secrets.token_hex(32)`, permissão `0600` quando possível, parser próprio que não sobrescreve o ambiente, segredo nunca impresso nem logado);
   - hash de senha scrypt + HMAC-SHA256 com o segredo (formato `scrypt$n$r$p$sal$hash`), verificação em tempo constante, política (8 a 128 caracteres, diferente do e-mail), hash fictício quando o e-mail não existe;
   - validação e normalização de e-mail e de nome;
   - CSRF: token por sessão e token pré-login com o cookie `kstudy_pre` (HMAC);
   - limite de tentativas (tabela `login_attempts`: 5 falhas em 15 min por e-mail+IP, 30 por IP, `429` com `Retry-After`);
   - cabeçalhos de segurança da seção 6 do contrato; leitura segura de corpo (1 MB).
2. **`db.py`:**
   - esquema v2 exatamente como na seção 4 do contrato e migração v1→v2 por `meta.schema_version` (contas antigas sem senha ficam com `password_hash=''` e cadastram senha e nome no próximo login);
   - tabelas `assets`, `audit_log` e `login_attempts`; colunas `students.name/password_hash/is_admin`, `sessions.csrf_token/expires_at`, `trails.cover/active`, `items.transcript`;
   - o PRIMEIRO cadastro vira admin dentro de uma transação (`BEGIN IMMEDIATE`), sem corrida (teste com threads);
   - sessões com validade deslizante de 30 dias e absoluta de 90, token novo a cada login, logout apaga no servidor.
3. **`indexer.py`:** preencher `assets` (lista PERMITIDA de arquivos servíveis: `block.json`, arquivos de aula, transcrições, `figures/`, capa), `trails.cover` e `items.transcript`; preservar `trails.active` entre reindexações; recusar arquivo fora da pasta da trilha ou com extensão não permitida.
4. **`server.py`:** TODAS as rotas da seção 7 (auth, trails, cover, blocks, items/content, items/transcript, figures, progress, track, admin).
   - **Não pode existir rota que sirva arquivo por caminho:** o conteúdo é pedido por ids e traduzido por consulta ao índice; `figures` só aceita nome `[A-Za-z0-9._-]+` presente em `assets`; trilha inativa dá `404` ao aluno.
   - Sessão obrigatória (`401`), admin (`403`), CSRF em toda escrita (exceto `track` por beacon, com `csrf` no corpo), `Origin`/`Host`/`--lan` como hoje, `Content-Type` exigido, `413`, mensagens de erro em português com códigos em inglês, sem traceback ao cliente.
   - Servir `/` (`web/`) e `/admin/` (`admin/web/`, `403` para não admin).
   - As rotas admin usam `admin/queries.py` e, para importar e gerar o zip das specs, `packages.py` (tarefa 02); enquanto não existir, importe de forma preguiçosa e responda `501 not_available`; teste essas rotas com um `packages` falso.
   - `audit_log` de logins e de ações do admin.
5. **`cli.py` e `main.py`:** remover o comando `admin`; manter `serve` (`--lan`, `--port`, `--content-dir`, `--db`, `--env`), `validate`, `sync`, `trails`, `new-trail`; acrescentar `pack` e `import-trail` (chamam `packages.py` quando existir), `set-admin EMAIL` e `reset-password EMAIL` (senha pedida no terminal sem eco, `getpass`); adaptar `import-progress` (exige conta existente). `--help` e saídas em português. Remover `src/k_study/admin/server.py` se existir.
6. **`validate.py`:** aceitar `cover` em `trail.json` (arquivo existe, png/jpg/webp, até 1 MB).
7. **Testes:**
   - auth (check/login/register, primeiro admin, e-mail inválido e normalização, senha curta, confirmação diferente, hash diferente entre contas);
   - sessões (flags do cookie, rotação no login, expiração, logout);
   - CSRF (sem token, token errado, pré-login, beacon);
   - rate limit; cabeçalhos;
   - rotas por id (inclusive `..`, `%2e%2e`, nomes fora da lista, trilha inativa);
   - isolamento entre alunos; admin (`401`/`403`); migração v1→v2; `.env` (criação, permissões, não sobrescreve); CLI.
8. **Teste de fumaça:** `py main.py validate aprendizagem-de-maquina` e o servidor com banco e `.env` temporários, exercitando o cadastro do primeiro admin e de um aluno por requisições HTTP reais.

## Aceite

- Suíte inteira verde, várias vezes seguidas.
- Nenhuma rota serve arquivo por caminho; nenhuma escrita passa sem CSRF; nenhuma senha em texto puro no banco ou no log.
- O comando `admin` não existe mais.

## Ao terminar

Atualize a linha 01 do manifesto e o "Registro" (rotas finais, decisões, lacunas do contrato).
