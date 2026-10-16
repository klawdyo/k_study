# Manifesto de tarefas

Este arquivo é o **índice e o registro de andamento** das tarefas do projeto. Cada tarefa é um arquivo desta pasta, **autossuficiente**: quem a executa não precisa de nenhuma conversa anterior. Mantenha este manifesto atualizado: ele é a memória do trabalho.

## Como um agente usa esta pasta

1. Leia este manifesto inteiro, depois `docs/arquitetura.md` (o contrato) e `CLAUDE.md`.
2. Escolha a **primeira tarefa `pendente` cujas dependências estejam `feita`** (ou a que o usuário indicar). Tarefas sem dependência entre si podem ser feitas em paralelo, cada uma em sua sessão e sua branch/worktree.
3. **Marque como `em andamento`** (na linha da tabela e com a data) e comite só isso: `chore(tasks): inicia a tarefa NN`.
4. Execute a tarefa **somente** nos arquivos que ela declara como seus. Siga as regras gerais abaixo.
5. Ao terminar, rode os testes e a checagem de aceite da tarefa; marque como `feita` na tabela, anote o último commit e acrescente, na seção "Registro", o que decidiu, o que encontrou e o que ficou pendente: `chore(tasks): conclui a tarefa NN`.
6. Se não puder concluir, marque `bloqueada` com o motivo e o que falta. **Não** deixe a tarefa como `em andamento` sem alguém trabalhando nela.
7. Tarefas marcadas **(usuário)** exigem uma ação ou autorização da pessoa dona do projeto: o agente prepara tudo, explica o passo e **espera**; nunca decide por ela.

Para começar uma sessão nova, basta dizer ao agente: *"Leia `.tasks/00-manifest.md` e execute a próxima tarefa disponível."*

## Regras gerais (valem para todas as tarefas)

- **Idioma:** código (arquivos, módulos, funções, variáveis, classes, tabelas, colunas, chaves JSON, comandos e opções) em **inglês**; specs, README, interface, mensagens vistas por pessoas, logs de operação, comentários e docstrings em **português do Brasil**.
- **Commits:** atômicos e mínimos (uma mudança lógica por commit), em Conventional Commits (`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `build`; **nunca** `!` nem `BREAKING CHANGE:` sem autorização explícita do usuário), tipo em inglês e descrição em português, terminando com a linha em branco e `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. A versão do projeto é calculada pelos commits (SemVer): não edite a versão à mão.
- **Nunca** faça `push`, nem crie ou apague repositórios remotos, sem autorização explícita do usuário.
- **Só biblioteca padrão** do Python no servidor (3.10+). Sem rede nos testes.
- **Testes:** `python -c "import sys,os; sys.path[:0]=['src', os.path.expanduser('~/.local/lib/pylibs')]; import pytest; sys.exit(pytest.main(['-q','-p','no:cacheprovider']))"` na raiz do repositório (ou `pytest`, se instalado). Rode a suíte várias vezes quando mexer em concorrência.
- **Contrato:** `docs/arquitetura.md` manda. Achou lacuna ou contradição? Siga o espírito dele, registre no "Registro" abaixo e, se a tarefa não for a dona do contrato, **não** edite o contrato.
- **Segurança:** SQL sempre parametrizado, nenhuma rota por caminho de arquivo, nenhum segredo em código, log ou commit (`.env`, `data/` e `*.db` ficam fora do git).
- **Não cite ferramentas internas** de versionamento ou comandos exclusivos da máquina do autor em arquivos do projeto.
- **Dono dos arquivos:** cada tarefa lista os arquivos que pode editar; os testes dela ficam junto. Não mexa nos arquivos de outra tarefa.

## Tarefas

Base de todas: branch `trilhas`, commit do contrato revisão 2 (`docs: atualiza o contrato com login por senha, admin integrado, CSRF, rotas por id e pacotes zip`).

| NN | Arquivo | Título | Depende de | Status | Último commit |
| :-: | :-- | :-- | :-- | :-- | :-- |
| 01 | `01-nucleo-seguro.md` | Núcleo seguro: banco v2, contas com senha, CSRF, rotas por id, CLI | — | feita (2026-10-16) | (sem commit ainda) |
| 02 | `02-pacotes-zip.md` | Pacotes zip: importar trilha, empacotar trilha, zip das specs | — | feita (2026-10-16) | (sem commit ainda) |
| 03 | `03-interface-aluno.md` | Interface do aluno: login em etapas, nome, cores, rotas por id | contrato | feita (2026-10-16) | (sem commit ainda) |
| 04 | `04-area-admin.md` | Área administrativa: estatísticas, ativar, importar zip, baixar specs | contrato | feita (2026-10-16) | (sem commit ainda) |
| 05 | `05-specs-e-docs.md` | Specs e documentação da revisão 2 | contrato | feita (2026-10-16) | (sem commit ainda) |
| 06 | `06-auditoria-seguranca.md` | Auditoria OWASP e varredura de segredos | 01 a 05 unidas | feita (2026-10-16) | (sem commit ainda) |
| 07 | `07-renomear-diretorio.md` | Renomear a pasta `estudos` para `k_study` **(usuário)** | — | feita (2026-10-16) | |
| 08 | `08-importar-progresso-antigo.md` | Importar o progresso antigo para a conta do usuário **(usuário)** | 01 | pendente | |
| 09 | `09-publicar.md` | Unir `trilhas` ao `main` e publicar no GitHub **(usuário)** | 01 a 06 | pendente | |
| 10 | `10-limpar-o-drive.md` | Limpar do Drive o que migrou para o projeto **(usuário)** | 08, 09 | pendente | |

Status possíveis: `pendente`, `em andamento (AAAA-MM-DD)`, `feita (AAAA-MM-DD)`, `bloqueada (motivo)`. "Unidas" significa que os commits da tarefa já estão na branch de trabalho comum (`trilhas`).

Paralelismo: **01 a 05 podem rodar ao mesmo tempo** (arquivos diferentes; 01, 03 e 04 conversam pela API do contrato e só se encaixam depois de unidas). **06 só depois** de 01 a 05 unidas. A 07 já foi feita.

## Registro

Acrescente aqui, por tarefa, em ordem cronológica: decisões, lacunas do contrato, riscos, pendências. Formato: `### NN · AAAA-MM-DD · título curto` e uma lista.

### 00 · 2026-10-16 · Estado de partida

- Branch `trilhas` com a reestruturação para trilhas já feita (pacote `k_study`, banco SQLite, painel do admin separado, interface com e-mail, specs, trilha inicial de aprendizagem de máquina). 93 testes passando.
- Revisão 2 do contrato decidida e documentada em `docs/arquitetura.md`: login com senha (scrypt + segredo no `.env`), primeiro cadastro vira administrador, admin integrado ao `kstudy serve` (sem segunda porta, sem comando `admin`), CSRF, rotas por ids sem acesso a arquivo por caminho, pacotes zip de trilha, zip das specs para download, capa da trilha, barra de progresso contando tudo, marcas obrigatória/opcional coloridas.
- O projeto irmão `k_transcriptor` (busca, download e transcrição) está pronto em outro repositório; não faz parte destas tarefas.
- Pendências conhecidas fora das tarefas: nada foi enviado (`push`); o remoto `origin` já aponta para `klawdyo/k_study`.
- A pasta local foi renomeada de `estudos` para `k_study` pelo usuário (tarefa 07) e o comando `kstudy` foi reinstalado. Cuidado: programas que gravam no caminho antigo recriam a pasta `estudos`; use sempre `k_study`.

### 01 · 2026-10-16 · Núcleo seguro

- Feito: `security.py` novo; `db.py` com migração v2 (v1 vira conta sem senha; sessões antigas descartadas; trilhas reindexadas); `indexer.py` com `assets`, `cover`, `items.transcript` (caminhos de `items.path`/`transcript` agora relativos à PASTA DA TRILHA) e `active` preservado; `server.py` com todas as rotas da seção 7; CLI sem `admin`, com `pack`, `import-trail`, `set-admin`, `reset-password`, `--env`; `validate` aceita `cover`; `admin/server.py` removido; `.env` no `.gitignore`.
- Decisões: `POST /api/auth/check` devolve também `needsSetup` (conta v1 sem senha: a tela mostra o cadastro). Só falhas de login contam no limite (check não conta, para não travar uma sala atrás do mesmo IP). Admin enxerga trilha inativa nas rotas de conteúdo; anônimo em `/admin/` recebe 401, aluno comum 403. `Content-Type: application/json` é exigido em toda escrita (inclusive sem corpo); o beacon deve enviar Blob `application/json` com `csrf` no corpo.
- `GET /api/trails` agora exige sessão (401 sem login). `list_trails` devolve também `requiredDone` e `active`.
- Pendências: `tests/test_admin.py` ainda é o da revisão 1 (tarefa 04 reescreve; rode a suíte com `--ignore=tests/test_admin.py`). `packages.py` (tarefa 02) é importado de forma preguiçosa; rotas e CLI foram testadas com módulo falso. A interface em `web/` ainda fala a API antiga (tarefa 03). Nenhum commit foi feito a pedido do usuário.

### 02 · 2026-10-16 · Pacotes zip

- Feito: `packages.py` (`import_trail_zip`, `pack_trail`, `build_specs_zip`, `PackageError`) e `tests/test_packages.py` (22 testes, incluindo ida e volta com `content/aprendizagem-de-maquina`).
- Decisões: `onXXX=` é varrido por lista de eventos conhecidos (e não `on\w+=`) para não recusar texto como `one = 1`; o `zipfile` do Python já normaliza `\` (no Windows) e corta o nome no NUL ao ler, então esses dois casos chegam como nomes comuns e inofensivos; bytes realmente lidos são contados na extração e `BadZipFile`/CRC viram `PackageError`; pastas temporárias `.import-*` e `.backup-*` ficam dentro de `content_dir` e são ignoradas pelo indexador (nome começa com ponto).
- Pendências: nenhuma. Nenhum commit foi feito a pedido do usuário.

### 03 · 2026-10-16 · Interface do aluno

- Feito: `web/app.js`, `index.html`, `style.css`: login em etapas (check, senha ou cadastro; aviso de primeira conta administradora; 429 com "tente de novo em N minutos"), nome e e-mail no topo, botão "Administração" para admin, grade com capa (degradê com a inicial se não houver), barra `done/items`, chips "Obrigatória" (cor de destaque) e "Opcional" (âmbar) com texto no menu e no cabeçalho da aula, conteúdo por ids, markdown seguro (HTML escapado, links só http/https/mailto/âncora/rota interna, imagens só pela rota de figuras), CSRF (cabeçalho, retry em `csrf_failed`, beacon com `csrf` no corpo).
- Testado de verdade contra o servidor real (`py main.py serve` com banco, `.env` e conteúdo temporários, incluindo uma trilha hostil com `<script>`, `onerror`, `javascript:`): cadastro do primeiro admin pela interface, trilha real abrindo (61 aulas no bloco 1), questão respondida (PUT com CSRF 200), mobile escuro, console sem erros; nenhum vídeo foi tocado.
- Decisões e lacunas: PDF não usa mais iframe (a CSP só libera YouTube em `frame-src`); abre em outra aba. `promptFile` de questões não é carregável pelas rotas por id (a trilha real não usa); a interface mostra um aviso no lugar. Link relativo em markdown vira só texto. "Lista do bloco" não existe como tela separada: os chips estão no menu lateral e no cabeçalho.

### 04 · 2026-10-16 · Área administrativa

- Feito: `admin/queries.py` adaptado ao esquema v2 (`name` em alunos e atividade recente; `cover` e `active` nas trilhas); `tests/test_admin.py` agora testa só as consultas contra o DDL exato da seção 4; `admin/web/` reescrito sem `innerHTML` nem script inline (`h()`/`s()` criam nós; `theme.js` separado); telas: visão geral, alunos (nome e e-mail), detalhe do aluno, trilhas com capa, estado Ativa/Desativada e botão com confirmação, trilha (mapa de calor), **Importar trilha** (seletor e arrastar-e-soltar, caixa `replace`, XHR com progresso, avisos ou lista de problemas) e **baixar specs** com instruções; link "← Voltar às trilhas"; nome e e-mail do admin no topo.
- Servidor (arquivo da tarefa 01, ajuste necessário): `/admin/` sem sessão redireciona (302) para `/`, `/admin` redireciona para `/admin/`; aluno comum recebe 403.
- Testado no navegador contra o servidor real (banco, `.env` e conteúdo temporários): visão geral, alunos, detalhe, trilhas, desativar/reativar (persistiu), importação de zip válido, zip inválido (lista de problemas), mobile. Nenhum vídeo tocou. Único erro de console foi o 400 esperado do zip inválido.
- Limitação: o caminho "substituir se já existir" e o arrastar-e-soltar real não foram exercitados na interface (o `replace` tem teste de servidor e de pacote).

### 05 · 2026-10-16 · Specs e documentação

- Feito: `CLAUDE.md` e `README.md` reescritos; `specs/00` (fluxo ponta a ponta, ambiente, glossário com capa e pacote), `02`, `03` (etapas de capa e de empacotar), `04` (`py main.py setup`, `ktr where`), `07` (seção "Empacotar e entregar" com as regras do pacote e checklist), `08` (reescrita: servidor único, contas, `.env`, administração), `09` (`cover`) e `docs/modelo-de-dados.md` (`cover`, `optional` conta na barra, imagens só em `figures/`, pacote zip, progresso por conta). Comandos `py main.py ...` das specs viraram `kstudy ...` (o agente pode estar numa pasta vazia). O zip das specs foi gerado com `build_specs_zip` e lista os 12 arquivos esperados.
- Lacunas e divergências do contrato (não editei `docs/arquitetura.md`): (1) o código também varre `.txt` por conteúdo ativo, além de `.md` e `.json`; (2) `POST /api/auth/check` devolve também `needsSetup`; `GET /api/trails` devolve `requiredDone` e `active` além do contrato; (3) `promptFile` de questões é aceito pelo validador mas não é servido pelas rotas por id (não há asset para ele); (4) PDF não pode ser incorporado em iframe com a CSP do contrato (`frame-src` só YouTube), abre em outra aba; (5) `/admin/` sem sessão responde 302 para `/` (o contrato só diz "mandar para /"); (6) a spec 08 e o README citam `docs/seguranca.md`, criado pela tarefa 06.
- O agente numa pasta vazia instala o `kstudy` com `pip install -e ../k_study` depois de clonar `https://github.com/klawdyo/k_study.git`; isso depende de o repositório estar publicado (tarefa 09, do usuário).

### 06 · 2026-10-16 · Auditoria de segurança

- Condição "01 a 05 unidas": o trabalho de 01 a 05 está **no working tree da branch `trilhas`, sem commits** (a pedido do usuário); auditei esse estado. Os commits atômicos ainda precisam ser feitos.
- Segredos: nenhum achado real nos dois repositórios (árvore e histórico completo; scanner próprio, sem gitleaks). Informativo: nome e e-mail do autor nos metadados dos commits. Recomendação: `.env` no `.gitignore` do k_transcriptor (não alterei o outro repositório).
- Correções (com teste em `tests/test_exploits.py`, 21 testes de exploração): e-mail restrito a `atext`; `Handler.timeout` de 60 s e descarte de corpo com espera de 2 s; limite de 60 cadastros por endereço em 15 min (novo, fora do contrato); importação de zip serializada; `OPTIONS` e `PATCH` respondem 405 JSON.
- Entregável: `docs/seguranca.md` (modelo de ameaças, tabela OWASP A01 a A10, achados, riscos residuais, recomendações); linhas no `CLAUDE.md`, `README.md` e `specs/08`.
- Riscos residuais e o que depende do usuário: sem HTTPS próprio (proxy), `check` revela contas, conta antiga sem senha pode ser reivindicada, versão do `marked` (12.0.2) sem consulta a banco de avisos (sem rede), reescrita do histórico só se quiser esconder o e-mail do autor antes de publicar. Divergências do contrato a levar ao coordenador: limite de cadastros por endereço e regex de e-mail mais estrita.
- Suíte completa: 165 testes verdes, 3 execuções seguidas.

### Extra · 2026-10-16 · Entrada com o Google e Docker

- Pedido do usuário (fora das tarefas numeradas): `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` vazias no `.env` (com comentário de como informar a URI de retorno no Google); botão só aparece se as duas estiverem preenchidas; `.env.example`; `Dockerfile`.
- Feito: `oauth.py` (fluxo de código com PKCE, `state` em cookie assinado, `nonce`, `aud`/`iss`/`exp`/`email_verified`), rotas `/auth/oauth/google/start` e `/callback` (retorno FIXO no sistema, nunca no `.env`), `oauth` em `/api/auth/me`, botão na tela de entrada, `--host`, `K_STUDY_HOST`, `K_STUDY_ALLOWED_HOSTS`, `SIGTERM` limpo, `Dockerfile` e `.dockerignore`; contrato (`docs/arquitetura.md` 5.1), `docs/seguranca.md`, README e spec 08 atualizados. 28 testes novos em `tests/test_oauth.py` (Google falso, sem rede).
- Decisões: contas criadas pelo Google recebem o hash `oauth$google` (não confere como senha e não é "conta sem senha", então não dá para reivindicá-las com `register`); o primeiro cadastro por qualquer meio é admin; `K_STUDY_ALLOWED_HOSTS` é necessário para domínio atrás de proxy.
- Não testado: o fluxo real com o Google (precisa de credenciais suas); o fluxo foi testado com um Google falso e a URL de autorização foi conferida.
