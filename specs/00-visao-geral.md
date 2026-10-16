# 00 · Visão geral

## O que é o k_study

O **k_study** é um servidor local de **trilhas de aprendizagem**. Uma trilha é um curso sobre qualquer assunto (um protocolo de rede, uma prova de faculdade, um instrumento musical) feito por um agente de IA a partir do que a pessoa precisa aprender e do material que ela tem. O servidor exibe a trilha para um ou vários alunos: vídeos com trechos marcados, leituras explicadas do zero e questões com todas as alternativas comentadas. Cada aluno tem conta própria (e-mail e senha) e o próprio progresso; o administrador importa trilhas, ativa e desativa trilhas e vê estatísticas.

O formato exato dos arquivos de conteúdo está em [`docs/modelo-de-dados.md`](../docs/modelo-de-dados.md). O contrato técnico do servidor (banco, API) fica no repositório do k_study, em `docs/arquitetura.md`; **você não precisa dele**: tudo o que importa para criar uma trilha está nestas specs. Estas specs dizem **como o agente trabalha**.

## O fluxo ponta a ponta

A criação acontece **fora do servidor**, no computador de quem cria. O servidor não tem botão de criar trilha: ele só **importa** pacotes prontos.

1. O administrador do servidor abre `/admin/` e baixa o **zip das specs** (`CLAUDE.md`, `specs/**` e `docs/modelo-de-dados.md`: exatamente os arquivos que você está lendo).
2. Ele abre um agente de IA (você) numa **pasta vazia**, descompacta o zip nela e pede: "quero uma trilha sobre ...".
3. Você confere o ambiente (abaixo), conduz a **entrevista** (`01`), cria `content/<slug>/` (`kstudy new-trail`, ou à mão com os templates de `09`), produz vídeos, leituras e questões (`03` a `06`), valida e audita (`07`).
4. Você **empacota** (`kstudy pack <slug>`) e entrega o arquivo `<slug>.zip` (regras do pacote em `07`).
5. O administrador envia o `.zip` em **Importar trilha** (`/admin/`). Se a trilha for nova, ela aparece para os alunos; se o slug já existir, ele escolhe "substituir" (o progresso dos alunos é mantido).

Você **não tem acesso ao servidor** e não precisa dele para trabalhar.

## Ambiente (confira antes de começar)

| Preciso de | Como conferir e instalar |
| :-- | :-- |
| **Python 3.10 ou superior** | `py --version` (Windows) ou `python3 --version`. Se faltar, **peça à pessoa para instalar** (python.org) e espere; não siga sem ele |
| **`kstudy`** (valida, cria e empacota) | `kstudy --version`. Se não existir: `git clone https://github.com/klawdyo/k_study.git ../k_study` e `pip install -e ../k_study` (em Windows, `py -m pip`). Dentro do repositório do k_study, `py main.py <comando>` é equivalente. Sem conseguir instalar: crie a trilha à mão com os templates de `09` e siga a checklist de `07` (inclusive para gerar o zip) |
| **k_transcriptor (`ktr`)** | só para transcrever vídeos (`04`): clone `https://github.com/klawdyo/k_transcriptor.git` e rode `py main.py setup` na pasta dele |
| Internet | para buscar e baixar o áudio dos vídeos; o servidor, depois, só precisa dela para os vídeos do YouTube |

## O que você, agente, deve entregar

Quando a pessoa pedir uma trilha, você entrega uma pasta `content/<slug>/` **e o pacote `<slug>.zip`**. A pasta:

1. passa em `kstudy validate <slug>` sem erros (e vira um pacote que o servidor aceita);
2. cobre **100% do material e dos objetivos** que a pessoa declarou, na ordem lógica de pré-requisitos;
3. para cada aula: vídeos **realmente lidos por transcrição** (com trechos e avisos de divergência), uma **leitura do zero** e **questões** com toda alternativa explicada;
4. traz `brief.md` (as decisões da entrevista) e fichas de conferência dos vídeos, para que qualquer pessoa ou agente retome o trabalho depois (esses arquivos são **registro**: ficam na pasta, mas veja em `07` o que entra no pacote);
5. foi **auditada por você mesma** conforme `07-validacao-e-qualidade.md`: o validador "OK" **não prova qualidade**.

## Ordem de leitura das specs

| # | Arquivo | Leia quando |
| :-: | :-- | :-- |
| 00 | `00-visao-geral.md` | sempre, primeiro |
| 01 | `01-entrevista.md` | antes de criar qualquer coisa: o que perguntar à pessoa |
| 02 | `02-estrutura-do-conteudo.md` | ao criar a pasta e os arquivos |
| 03 | `03-pipeline-de-geracao.md` | o passo a passo de ponta a ponta e como paralelizar |
| 04 | `04-videos-e-k_transcriptor.md` | ao buscar, transcrever e escolher vídeos |
| 05 | `05-leituras.md` | ao escrever a leitura de cada aula |
| 06 | `06-questoes.md` | ao escrever as questões |
| 07 | `07-validacao-e-qualidade.md` | antes de dar a trilha como pronta; lista do que nunca fazer |
| 07 | (continuação) | **empacotar e entregar o zip**: regras do pacote |
| 08 | `08-servidor-e-admin.md` | para explicar à pessoa como o servidor, as contas e a administração funcionam |
| 09 | `09-templates.md` | para copiar esqueletos prontos |

Um agente que leia só estas specs deve conseguir trabalhar sem perguntar o que já está dito aqui. Pergunte à pessoa apenas o que a entrevista (`01`) manda perguntar ou o que estiver realmente bloqueado.

## Princípios que atravessam tudo

- **Honestidade acima de volume.** Nunca invente fato, timestamp, número, referência ou o que um vídeo diz. O que não foi verificado fica marcado ("a verificar") ou fora.
- **Explicar do zero.** O leitor-alvo é descrito na entrevista (o que já sabe, o que não sabe). Toda ideia vem com analogia do mundo dele e exemplo antes do termo técnico.
- **Aprender é responder.** O valor das questões está nas explicações de todas as alternativas.
- **Autonomia com registro.** Depois da entrevista aprovada, decida e siga; registre decisões em `brief.md`. Só pare se estiver bloqueado.
- **Direitos de terceiros.** Vídeos são só linkados (YouTube incorporado); transcrições servem a estudo pessoal; nada de material de terceiros copiado literalmente.

## Glossário

| Termo | Significado |
| :-- | :-- |
| **Trilha** (`trail`) | um curso completo; uma pasta `content/<slug>/` com `trail.json` |
| **Bloco** (`block`) | agrupamento de aulas relacionadas (`block-1/block.json`); unidade de entrega e de paralelização |
| **Seção / aula** | `sections[]` de um bloco; uma aula = um tema do material. Contém itens |
| **Item** | uma peça da aula, em ordem de estudo: `video`, `markdown`, `pdf`, `link` ou `questions` |
| **Leitura** | item `markdown` escrito do zero pelo agente (`aula-N-do-zero.md`) |
| **Conjunto de questões** | arquivo `questions/v2` ligado a um item `questions` |
| **Ficha** | `validacao-videos-aula-N.md`: registro da conferência dos vídeos de uma aula (matriz tópico × vídeo, descartados, lacunas) |
| **Trecho** (`clip`) | intervalo `start`–`end` (segundos) de um vídeo que cobre um tópico; um botão na interface |
| **Transcrição** | JSON `transcripts/<ID>.json` com `segments` `[segundo, texto]`, gerado pelo k_transcriptor |
| **Capa** (`cover`) | imagem opcional da trilha (1200×630; png, jpg ou webp; até 1 MB) citada em `trail.json`; aparece no cartão |
| **Pacote** | o `.zip` da trilha, com uma única pasta de topo `<slug>/`; gerado por `kstudy pack` e importado pelo administrador |
| **Material** | o que a pessoa fornece (slides, textos, ementa); fica em `materials/` e define o escopo e a ordem |
| **Brief** | `content/<slug>/brief.md`: respostas da entrevista e decisões do projeto |
| **`kstudy` / `py main.py`** | o CLI do k_study (iguais): `new-trail`, `validate`, `pack` e outros |
| **`ktr`** | o CLI do k_transcriptor (outro repositório): busca, baixa áudio, transcreve |
