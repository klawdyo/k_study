# CLAUDE.md · k_study

O **k_study** é um servidor local de **trilhas de aprendizagem** (cursos com vídeos, leituras e questões) criadas por agentes de IA a partir de um assunto e do material que a pessoa fornece. Alunos estudam no navegador (login por e-mail, progresso por aluno); o admin vê estatísticas. Só biblioteca padrão do Python; comando `py main.py <comando>` (ou `kstudy` após `pip install -e .`).

## Se a pessoa pediu uma trilha

**Comece pela entrevista em `specs/01-entrevista.md`.** Antes de agir, leia as specs nesta ordem: `specs/00-visao-geral.md`, `01-entrevista.md`, `02-estrutura-do-conteudo.md`, `03-pipeline-de-geracao.md`, e consulte `04` (vídeos e k_transcriptor), `05` (leituras), `06` (questões), `07` (validação e qualidade), `08` (servidor e admin), `09` (templates) quando chegar a hora. Formato dos arquivos: `docs/modelo-de-dados.md`. Contrato técnico: `docs/arquitetura.md`. Exemplo real de qualidade: `content/aprendizagem-de-maquina/`.

## Tarefas em andamento

Há tarefas planejadas e o registro do que já foi feito em `.tasks/`. **Leia `.tasks/00-manifest.md` antes de agir** e siga o protocolo dele (escolher a próxima tarefa disponível, marcar o andamento, comitar de forma atômica, registrar decisões).

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

## Comandos

```bash
py main.py serve [--port 8765] [--lan] [--content-dir D] [--db F]   # alunos: http://localhost:8765/
py main.py admin [--port 8766] [--lan --password P]                   # painel do admin
py main.py new-trail SLUG --title T [--description D]                 # cria content/<slug>/
py main.py validate [slug]       # valida (erros reprovam; avisos só avisam)
py main.py sync                  # reindexa content/ no banco
py main.py trails                # lista trilhas e números
py main.py import-progress --email E --trail SLUG ARQUIVO.json
ktr search|transcribe|text|queue|clean ...                         # k_transcriptor (specs/04)
```

Códigos de saída: 0 ok, 1 problemas de validação, 2 erro de uso ou de ambiente.

## Convenção de idioma

- **Em inglês:** nomes de arquivos de código, módulos, funções, variáveis, tabelas e colunas do banco, **chaves JSON**, comandos e opções do CLI, códigos de erro da API.
- **Em português do Brasil:** specs, `README.md`, este arquivo, a interface, as mensagens vistas por pessoas (saída e erros do CLI, `--help`, erros da API) e o conteúdo gerado. Comentários e docstrings em português.
- Responda à pessoa em português do Brasil.

## Para quem for evoluir o código do k_study

- **Contrato:** `docs/arquitetura.md` manda. Mudou algo (rota, tabela, comando, formato)? Mude o contrato primeiro, depois o código e os docs (`docs/modelo-de-dados.md`, `specs/`, `README.md`).
- **Estrutura:** `src/k_study/` com `cli.py`, `server.py`, `db.py`, `indexer.py`, `validate.py`, `admin/` (servidor e `admin/web/`), `web/` (interface do aluno). Entrada: `main.py` / `python -m k_study`.
- **Somente biblioteca padrão** no núcleo (sqlite3 incluso); sem build do front-end; interface sem frameworks.
- **Testes:** `pip install -e ".[dev]"` e `pytest` (sem rede, sem GPU). Rode antes de commitar; teste de contrato quando mexer em API ou validador.
- **Conteúdo não se edita pela API**; o servidor só lê `content/`. Estado de aluno fica só no banco.
- **Não quebre ids publicados** nem a leitura de trilhas existentes (`content/aprendizagem-de-maquina/` deve continuar válida).
- **Commits:** pequenos, mensagem em português no imperativo, um assunto por commit; o código novo vem com teste. Não faça push sem autorização da pessoa.
- Se mudar o que o validador reprova ou avisa, atualize `specs/07-validacao-e-qualidade.md` e `docs/modelo-de-dados.md`.
