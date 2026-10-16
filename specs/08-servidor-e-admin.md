# 08 · Servidor e admin

## Rodar o servidor dos alunos

```bash
py main.py serve                          # http://localhost:8765/
py main.py serve --port 9000
py main.py serve --lan                    # aceita outros computadores da rede privada (sem senha)
py main.py serve --content-dir D:\cursos --db D:\cursos\k_study.db
```

- Padrões: `--content-dir ./content`, `--db ./data/k_study.db`; ou variáveis `K_STUDY_CONTENT` e `K_STUDY_DB`.
- Sem instalar nada: `py main.py serve` usa só a biblioteca padrão. Com `pip install -e .` existe o comando `kstudy`.
- O servidor sincroniza o índice ao iniciar; depois de mexer em `block.json`/`trail.json`, rode `py main.py sync` (ou reinicie).
- **`--lan`:** escuta em todas as interfaces, mas só aceita clientes de redes privadas, e verifica o cabeçalho `Host`. O firewall pode pedir permissão. **Sem senha**: use só em rede confiável. Quem acessa vê/edita o progresso do e-mail que digitar.
- Rotas: interface em `/` (SPA com hash: `#/` grade de trilhas, `#/t/<slug>`); API em `/api/...` (ver `docs/arquitetura.md`, seção 6).

## Identidade do aluno

- Ao abrir, o aluno informa o **e-mail**. Um cookie `kstudy_sid` (HttpOnly, 1 ano) vincula aquele navegador ao e-mail; o banco guarda só o hash do token. Informar o mesmo e-mail em outro computador traz o mesmo progresso.
- **Não há verificação do e-mail nem senha:** quem digita o e-mail de outra pessoa vê o progresso dela. É aceitável para estudo pessoal ou em grupo de confiança; documente isso à pessoa. A verificação por código pode vir depois.
- O e-mail é normalizado (espaços removidos, minúsculas). Fica só no banco local; nada sai da máquina.

## Painel do admin

```bash
py main.py admin                          # http://127.0.0.1:8766/  (somente esta máquina)
py main.py admin --lan --password SENHA   # outra máquina da rede; exige senha (ou K_STUDY_ADMIN_PASSWORD)
```

O admin lê o mesmo banco (somente leitura). Ele vê:

- **Visão geral:** alunos, ativos nos últimos 7 dias, tempo total de estudo, visitas, trilhas; séries diárias de tempo e de alunos ativos (30 dias); conclusão média por trilha.
- **Alunos:** por aluno, cadastro, última atividade, tempo total, itens feitos, acerto em questões; detalhe por trilha (tempo por item, visitas, "só abriu e saiu" = visita com menos de 10 s, acertos por questão).
- **Trilhas:** alunos, conclusão média, tempo médio; por bloco e item: quantos abriram, tempo médio, **taxa de abandono** (visitas < 10 s), conclusão e acerto médio, e as **questões mais erradas**.

Use isso para melhorar o conteúdo: uma questão que quase todos erram pode ter gabarito errado ou enunciado confuso; um vídeo com abandono alto pode ser fraco.

Como o tempo é medido: a interface envia um sinal a cada 10 s **somente com a aba visível e em foco**.

## Importar progresso antigo

Para trazer um `progress.json` do formato antigo (app de arquivo único):

```bash
py main.py import-progress --email aluno@exemplo.com --trail aprendizagem-de-maquina caminho/progress.json
```

O arquivo antigo tem `items`, `answers` e `notes`. O comando grava no banco para aquele e-mail. Rode antes de reorganizar o conteúdo e **nunca edite o banco à mão**.

## Backup

O estado dos alunos está em **um arquivo**: `data/k_study.db` (SQLite em modo WAL; podem existir `-wal` e `-shm` ao lado enquanto o servidor roda). Para fazer backup com o servidor parado, copie o `.db`. Com o servidor rodando, use `sqlite3 data/k_study.db ".backup backup.db"` ou copie os três arquivos juntos. O conteúdo (`content/`) é versionado no Git.

## Remover uma trilha

1. Apague a pasta `content/<slug>/` (o Git guarda o histórico).
2. `py main.py sync`: a trilha sai do índice e da grade.
3. O progresso dos alunos **permanece** no banco; se a pasta voltar, eles recuperam.

Para remover a trilha de exemplo: `rm -r content/aprendizagem-de-maquina` seguido de `py main.py sync`.

## Limitações

- E-mail sem verificação (ver acima).
- Servidor pensado para uso local ou pequeno grupo; não é um serviço de internet. Não o exponha diretamente na internet.
- Transcrição de vídeos é CLI (k_transcriptor), não rota da API; a API não edita conteúdo.
- Anotações e respostas são por aluno, mas o banco é um só: a última escrita vence.
