# 00 · Visão geral

## O que é o k_study

O **k_study** é um servidor local de **trilhas de aprendizagem**. Uma trilha é um curso sobre qualquer assunto (um protocolo de rede, uma prova de faculdade, um instrumento musical) feito por um agente de IA a partir do que a pessoa precisa aprender e do material que ela tem. O servidor exibe a trilha para um ou vários alunos: vídeos com trechos marcados, leituras explicadas do zero e questões com todas as alternativas comentadas. Cada aluno tem o próprio progresso (identificado por e-mail), e o admin vê estatísticas.

O contrato técnico (pastas, banco, API, CLI) está em [`docs/arquitetura.md`](../docs/arquitetura.md). O formato exato dos arquivos de conteúdo está em [`docs/modelo-de-dados.md`](../docs/modelo-de-dados.md). Estas specs dizem **como o agente trabalha**.

## O que você, agente, deve entregar

Quando a pessoa pedir uma trilha, você entrega uma pasta `content/<slug>/` que:

1. abre no servidor (`py main.py serve`) e passa em `kstudy validate <slug>` sem erros;
2. cobre **100% do material e dos objetivos** que a pessoa declarou, na ordem lógica de pré-requisitos;
3. para cada aula: vídeos **realmente lidos por transcrição** (com trechos e avisos de divergência), uma **leitura do zero** e **questões** com toda alternativa explicada;
4. traz `brief.md` (as decisões da entrevista) e fichas de conferência dos vídeos, para que qualquer pessoa ou agente retome o trabalho depois;
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
| 08 | `08-servidor-e-admin.md` | ao rodar, testar e administrar o servidor |
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
| **Material** | o que a pessoa fornece (slides, textos, ementa); fica em `materials/` e define o escopo e a ordem |
| **Brief** | `content/<slug>/brief.md`: respostas da entrevista e decisões do projeto |
| **`kstudy` / `py main.py`** | o CLI do k_study (iguais) |
| **`ktr`** | o CLI do k_transcriptor (outro repositório): busca, baixa áudio, transcreve |
