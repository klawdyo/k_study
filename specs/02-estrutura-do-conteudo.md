# 02 · Estrutura do conteúdo

Resumo operacional. O formato exato dos arquivos está em `docs/modelo-de-dados.md`.

## Pasta de uma trilha

```text
content/<slug>/
  brief.md                     decisões da entrevista (não é lido pela interface)
  trail.json                   manifesto (schema trail/v1)
  cover.webp                   capa opcional (campo "cover" do trail.json; png, jpg ou webp; até 1 MB)
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
- **Capa (opcional):** uma imagem 1200×630 (png, jpg ou webp, até 1 MB) gerada por você ou fornecida pela pessoa, citada em `trail.json` no campo `cover` (`"cover": "cover.webp"`). Veja `03` (etapa de capa) para as regras.
- **Uma trilha por pasta;** o servidor lista todas as pastas de `content/` que tenham `trail.json`.

## Comandos

```bash
kstudy new-trail configuracao-de-switches --title "Configuração de switches de rede" --description "Do zero ao básico de VLAN e trunk."
```

Cria `content/<slug>/` com `trail.json` (sem blocos) e a estrutura mínima. Depois você cria `block-1/` e adiciona o bloco em `trail.json`.

```bash
kstudy validate <slug>     # valida uma trilha (sem argumento: todas). Erros reprovam (saída 1); avisos só avisam
kstudy sync                # reindexa content/ no banco (trilhas, blocos, itens)
kstudy trails              # lista trilhas e números (blocos, itens, itens obrigatórios, minutos)
kstudy pack <slug>         # valida e gera <slug>.zip, o pacote que o administrador importa
```

`kstudy` e `py main.py` (dentro do repositório do k_study) são equivalentes. Subir o servidor (`kstudy serve`) e importar o pacote é trabalho do administrador: veja `08`. Se você tem o repositório do k_study e quer conferir a trilha na interface, `kstudy serve` com um banco e `.env` temporários serve para isso.

## Como o servidor indexa (`sync`)

O banco guarda um **índice** (trilhas, blocos, itens com tipo, título, arquivo, opcional, minutos, **lista de arquivos permitidos**) e o **estado dos alunos**. O **corpo** (Markdown, questões, transcrições, imagens) é lido sob demanda dos arquivos, **sempre por ids** (trilha, bloco, aula): o servidor não serve arquivo por caminho, só os que o índice lista. Por isso: arquivos fora da pasta da trilha, com extensão não permitida ou não citados pelo `block.json` (e fora de `figures/`) não chegam ao aluno. Quem importa a trilha (o administrador) já a vê indexada; o `kstudy sync` serve a quem edita a pasta direto no servidor.

- Item que **some** do conteúdo: o progresso dele **não é apagado** (se voltar, o aluno recupera).
- Trilha removida da pasta: some do índice no próximo `sync`; os dados dos alunos permanecem no banco.

## Ordem para criar uma trilha

1. Entrevista aprovada e `brief.md` gravado (`01`).
2. `kstudy new-trail ...`.
3. Para cada bloco: criar `block-N/`, produzir os itens (pipeline em `03`) e escrever o `block.json`.
4. Registrar o bloco em `trail.json` (`blocks[]`: `id`, `title`, `file`).
5. `kstudy validate <slug>` e depois `kstudy sync`.
6. `kstudy pack <slug>` e entregar o `.zip` ao administrador (`07`, "Empacotar e entregar").

## Armadilhas

- Gravar arquivos grandes com a ferramenta de escrita de arquivos, não com heredoc do shell (acentos e tamanho quebram).
- No Windows, `PYTHONIOENCODING=utf-8` ao imprimir acentos; aspas e barras invertidas em JSON.
- IDs do YouTube que começam com `-` exigem `--` antes do argumento.
- JSON válido: depois de editar, valide (`kstudy validate`); uma vírgula sobrando derruba a trilha toda.
- Nunca edite o banco (`data/k_study.db`) nem arquivos de progresso de alunos.
