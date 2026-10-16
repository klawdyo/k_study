# 02 · Estrutura do conteúdo

Resumo operacional. O contrato completo está em `docs/arquitetura.md` (seções 2, 3 e 8) e o formato exato dos arquivos em `docs/modelo-de-dados.md`.

## Pasta de uma trilha

```text
content/<slug>/
  brief.md                     decisões da entrevista (não é lido pela interface)
  trail.json                   manifesto (schema trail/v1)
  materials/                   o que a pessoa forneceu (+ materials/_text/ com o texto extraído, cache seu)
  block-1/
    block.json                 sequência de estudo (schema block/v2)
    aula-1-do-zero.md          leituras
    lesson-1-questions.json    questões (schema questions/v2)
    code-questions.json        questões de código, se houver
    guia-ler-codigo.md         opcional
    validacao-videos-aula-1.md fichas de conferência dos vídeos (registro)
  transcripts/<videoId>.json   transcrições dos vídeos usados e dos avaliados
  figures/                     imagens usadas pelas leituras e questões
```

- **`slug`**: só `a-z`, `0-9` e `-`; é o nome da pasta e o `id` da trilha. Curto e sem acento (`configuracao-de-switches`).
- **Nomes de arquivos em inglês** para os que o código lê (`trail.json`, `block.json`, `lesson-N-questions.json`, `code-questions.json`). Os `.md` que o aluno lê podem ter nome em português (`aula-1-do-zero.md`).
- **Caminhos relativos** ao arquivo que os cita, sempre dentro da pasta da trilha: do `block-1/block.json`, `aula-1-do-zero.md`, `../transcripts/ID.json`, `../figures/f01.png`. Nunca caminho absoluto, nunca `G:\...`.
- **Ids estáveis.** Ids de trilha, bloco (`block-1`), seção (`aula-1`), item (`a1-v1`) e questão (`q01`) **nunca mudam depois de publicados**: o progresso dos alunos usa essas chaves. Se precisar substituir um vídeo, crie um id novo e marque o antigo como `optional` ou remova só se ninguém o usou (na dúvida, não remova). Convenção de ids de item: `a<N>-v<M>` vídeo, `a<N>-read` leitura, `a<N>-q` questões, `code-q` código, `guide` guia.
- **Imagens:** só as que você gerou ou descreveu; fica em `figures/`, citada como `../figures/nome.png`. Nomes em inglês, minúsculos, sem espaço. Nunca copie figura de slide/livro de terceiros (ver `05`).
- **Uma trilha por pasta;** o servidor lista todas as pastas de `content/` que tenham `trail.json`.

## Comandos

```bash
py main.py new-trail configuracao-de-switches --title "Configuração de switches de rede" --description "Do zero ao básico de VLAN e trunk."
```

Cria `content/<slug>/` com `trail.json` (sem blocos) e a estrutura mínima. Depois você cria `block-1/` e adiciona o bloco em `trail.json`.

```bash
py main.py validate <slug>     # valida uma trilha (sem argumento: todas). Erros reprovam (saída 1); avisos só avisam
py main.py sync                # reindexa content/ no banco (trilhas, blocos, itens)
py main.py trails              # lista trilhas e números (blocos, itens, itens obrigatórios, minutos)
py main.py serve               # http://localhost:8765/  (--lan, --content-dir, --db)
```

`kstudy` e `py main.py` são equivalentes (`pip install -e .` cria `kstudy`).

## Como o servidor indexa (`sync`)

O banco guarda um **índice** (trilhas, blocos, itens com tipo, título, caminho, opcional, minutos) e o **estado dos alunos**. O **corpo** (Markdown, questões, transcrições, imagens) é lido sob demanda dos arquivos. `kstudy sync` lê `trail.json` e cada `block.json` e atualiza o índice; o servidor também sincroniza ao iniciar. Se você mudar um `block.json`, rode `sync` (ou reinicie o servidor) para a grade e os contadores refletirem.

- Item que **some** do conteúdo: o progresso dele **não é apagado** (se voltar, o aluno recupera).
- Trilha removida da pasta: some do índice no próximo `sync`; os dados dos alunos permanecem no banco.

## Ordem para criar uma trilha

1. Entrevista aprovada e `brief.md` gravado (`01`).
2. `py main.py new-trail ...`.
3. Para cada bloco: criar `block-N/`, produzir os itens (pipeline em `03`) e escrever o `block.json`.
4. Registrar o bloco em `trail.json` (`blocks[]`: `id`, `title`, `file`).
5. `py main.py validate <slug>` e depois `py main.py sync`.
6. `py main.py serve` e olhar a trilha no navegador (um vídeo com trechos, uma leitura com imagem, uma questão, o cartão de transcrição).

## Armadilhas

- Gravar arquivos grandes com a ferramenta de escrita de arquivos, não com heredoc do shell (acentos e tamanho quebram).
- No Windows, `PYTHONIOENCODING=utf-8` ao imprimir acentos; aspas e barras invertidas em JSON.
- IDs do YouTube que começam com `-` exigem `--` antes do argumento.
- JSON válido: depois de editar, valide (`py main.py validate`); uma vírgula sobrando derruba a trilha toda.
- Nunca edite o banco (`data/k_study.db`) nem arquivos de progresso de alunos.
