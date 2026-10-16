# CLAUDE.md · k_study

O **k_study** é um servidor local de **trilhas de aprendizagem** (cursos com vídeos, leituras e questões). Quem cria as trilhas é você, um agente de IA, rodando **no computador da pessoa, fora do servidor**: você entrega um **pacote `.zip`** que o administrador importa em `/admin/`. Só biblioteca padrão do Python 3.10+; comando `kstudy <comando>` (ou `py main.py <comando>` dentro do repositório do k_study).

Responda à pessoa em **português do Brasil**.

## Se a pessoa pediu uma trilha

**Comece pela entrevista em `specs/01-entrevista.md`.** Leia as specs nesta ordem antes de agir: `specs/00-visao-geral.md` (inclui o fluxo ponta a ponta e o ambiente), `01-entrevista.md`, `02-estrutura-do-conteudo.md`, `03-pipeline-de-geracao.md`; consulte `04` (vídeos e k_transcriptor), `05` (leituras), `06` (questões), `07` (validação, qualidade e **empacotamento**), `08` (como o servidor é usado: contas, administração), `09` (templates). Formato exato dos arquivos: `docs/modelo-de-dados.md`. Exemplo real de qualidade: `content/aprendizagem-de-maquina/` (só existe dentro do repositório do k_study).

Você **não tem acesso ao servidor**: a entrega é a pasta `content/<slug>/` validada e o arquivo `<slug>.zip` gerado por `kstudy pack <slug>`. O administrador o envia em "Importar trilha".

## Regras inegociáveis

1. Não crie nada antes da entrevista aprovada; grave as decisões em `content/<slug>/brief.md`.
2. Depois da aprovação, seja autônomo: decida, registre e siga; só pare se bloqueado.
3. Nunca invente fato, timestamp, número, referência ou o que um vídeo diz.
4. Vídeo só entra depois de **ler a transcrição inteira**; nunca decida pelo título; todo `mm:ss` existe na transcrição.
5. Nunca remova um vídeo nem rode `ktr clean` sem ler a transcrição e registrar o veredito na ficha.
6. Um vídeo bom por tópico; o mais didático **para o nível da pessoa**; só remova duplicado com 100% de certeza.
7. Leitura do zero (350 a 700 linhas, cobertura 100% declarada, código executado, sem LaTeX, sem callouts, sem emojis); nada atribuído ao material que ele não diga.
8. Toda alternativa de questão tem explicação com o porquê; sem citar alternativa por letra; gabaritos conferidos.
9. Nunca altere ids publicados, o banco (`data/k_study.db`) nem o progresso de alunos; nunca embaralhe questões já respondidas.
10. Não copie material de terceiros literalmente (slides, figuras, livros); `validate` OK **não** prova qualidade: faça a auditoria de `specs/07`.
11. O pacote zip segue **exatamente** as regras de `specs/07` (uma pasta de topo `<slug>/`, extensões permitidas, sem HTML, JS, SVG nem links simbólicos); nunca ponha segredos, `.env`, banco ou áudio nele.

## Comandos

```bash
kstudy new-trail SLUG --title T [--description D]   # cria content/<slug>/
kstudy validate [slug]       # valida (erros reprovam; avisos só avisam)
kstudy pack SLUG [--out F]   # valida e gera o pacote .zip importável
kstudy import-trail ZIP [--replace]   # importa um pacote (o mesmo que o admin faz pela interface)
kstudy serve [--port 8765] [--lan] [--content-dir D] [--db F] [--env F]   # alunos em /, administração em /admin/
kstudy sync | trails | set-admin EMAIL | reset-password EMAIL | import-progress --email E --trail SLUG ARQ.json
ktr search|transcribe|text|queue|clean ...           # k_transcriptor (specs/04)
```

Sem instalar nada, dentro do repositório: `py main.py <comando>`. Se você está numa pasta vazia só com as specs, instale o `kstudy` (`specs/00-visao-geral.md`). Códigos de saída: 0 ok, 1 problemas de validação, 2 erro de uso ou de ambiente.

## Convenção de idioma

- **Em inglês:** nomes de arquivos de código, módulos, funções, variáveis, tabelas e colunas do banco, **chaves JSON**, comandos e opções do CLI, códigos de erro da API.
- **Em português do Brasil:** specs, `README.md`, este arquivo, a interface, as mensagens vistas por pessoas (saída e erros do CLI, `--help`, erros da API) e o conteúdo gerado. Comentários e docstrings em português.

## Tarefas em andamento (só no repositório do k_study)

Se a pasta `.tasks/` existir, há tarefas planejadas e o registro do que já foi feito nela. **Leia `.tasks/00-manifest.md` antes de agir** e siga o protocolo dele (escolher a próxima tarefa disponível, marcar o andamento, comitar de forma atômica, registrar decisões).

## Para quem for evoluir o código do k_study

- **Contrato:** `docs/arquitetura.md` manda. Mudou algo (rota, tabela, comando, formato)? Mude o contrato primeiro, depois o código e os docs (`docs/modelo-de-dados.md`, `specs/`, `README.md`).
- **Estrutura:** `src/k_study/` com `cli.py`, `server.py`, `security.py`, `db.py`, `indexer.py`, `packages.py`, `validate.py`, `admin/` (consultas e `admin/web/`, servidos em `/admin/`), `web/` (interface do aluno). Entrada: `main.py` / `python -m k_study`.
- **Somente biblioteca padrão** no núcleo (sqlite3 e zipfile inclusos); sem build do front-end; interface sem frameworks, sem `innerHTML` com dados de fora e sem script inline (CSP).
- **Segurança:** auditoria e riscos residuais em `docs/seguranca.md`; SQL parametrizado; nenhuma rota serve arquivo por caminho; toda escrita exige CSRF; senhas só com scrypt e o segredo do `.env` (nunca versionado). Nunca registre senhas, tokens nem o segredo.
- **Testes:** `pip install -e ".[dev]"` e `pytest` (sem rede, sem GPU). Rode antes de commitar; teste de contrato quando mexer em API ou validador.
- **Conteúdo não se edita pela API**; o servidor só lê `content/`. Estado de aluno fica só no banco.
- **Não quebre ids publicados** nem a leitura de trilhas existentes (`content/aprendizagem-de-maquina/` deve continuar válida).
- **Commits:** atômicos, Conventional Commits (tipo em inglês, descrição em português no imperativo), um assunto por commit; o código novo vem com teste. A versão é calculada pelos commits: não edite à mão. Não faça push sem autorização da pessoa.
- **Dados reais** (`content/` com material de terceiros, transcrições) não devem ir para um repositório público: veja o README.
- Se mudar o que o validador reprova ou avisa, atualize `specs/07-validacao-e-qualidade.md` e `docs/modelo-de-dados.md`.
