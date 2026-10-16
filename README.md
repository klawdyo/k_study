# k_study

Servidor local de **trilhas de aprendizagem**: cursos com vídeos recortados, leituras explicadas do zero e questões com todas as alternativas comentadas. As trilhas são **criadas por agentes de IA** (como o Claude Code) a partir do assunto que você quer aprender e do material que você tiver. Cada aluno tem o seu progresso; quem administra vê estatísticas de uso.

- Para **estudar**, você só precisa de Python 3.10+. Não instala nada.
- Para **criar uma trilha nova**, você abre um agente de IA nesta pasta e conversa com ele. O agente lê o `CLAUDE.md` e a pasta `specs/` e sabe o que fazer.

## O fluxo completo em passos

1. **Clone o projeto.**

   ```bash
   git clone https://github.com/klawdyo/k_study.git k_study
   cd k_study
   ```

2. **Suba o servidor.**

   ```bash
   py main.py serve
   ```

   No Linux/macOS, use `python3 main.py serve`.

3. **Abra no navegador:** <http://localhost:8765/>. Na primeira vez a tela pede o seu **e-mail**; ele identifica o seu progresso.

4. **Escolha uma trilha** na grade e comece pela primeira aula. A trilha de exemplo (`aprendizagem-de-maquina`) já vem incluída.

5. **Para criar uma trilha nova, abra um agente de IA nesta pasta** (por exemplo, `claude` no terminal) e peça: "quero uma trilha sobre ...". Veja a seção "Criando uma trilha com um agente".

6. **Recarregue a página** quando o agente terminar (ou rode `py main.py sync`). A trilha aparece na grade.

## Requisitos

| Para | Precisa de |
| :-- | :-- |
| Estudar | Python 3.10 ou superior. Nada mais (só a biblioteca padrão) |
| Criar trilhas | um agente de IA com acesso ao terminal (Claude Code); o projeto irmão **k_transcriptor** para transcrever vídeos (ele instala o que precisa) |
| Transcrição rápida (opcional) | placa NVIDIA com CUDA; sem ela roda na CPU, mais devagar |

## Instalação opcional (comando `kstudy`)

```bash
pip install -e .
kstudy serve          # igual a: py main.py serve
kstudy --help
```

Sem instalar nada, `py main.py <comando>` faz tudo.

## O que o aluno vê

- **Login por e-mail.** Você informa o e-mail e pronto: sem senha. O navegador fica vinculado a ele por um cookie. Em outro computador, o mesmo e-mail traz o mesmo progresso.
- **Grade de trilhas** com descrição, nível, número de aulas, minutos e quanto você já fez.
- **Aulas** na ordem de estudo: vídeos (com trechos recomendados e avisos de onde o vídeo diverge do material), leituras explicadas do zero e questões.
- **Vídeos** incorporados do YouTube, com botões para os trechos que importam e um cartão de **transcrição** com horários clicáveis.
- **Questões** com resposta imediata e **explicação de todas as alternativas**, certas e erradas.
- **Anotações** por item e **barra de progresso** da trilha, do bloco e da aula; o botão "PRÓXIMO" aponta o que vem a seguir.
- **Progresso em vários computadores**, pelo mesmo e-mail.

## O que o admin vê

```bash
py main.py admin          # http://127.0.0.1:8766/  (somente nesta máquina)
```

Um painel com cartões de resumo, gráficos e tabelas: alunos ativos, tempo total de estudo, visitas, conclusão por trilha, tempo e abandono por aula, acertos por questão e as questões mais erradas. Serve para melhorar o conteúdo. Detalhes em `specs/08-servidor-e-admin.md`.

## Estudar de outro computador da rede (`--lan`)

```bash
py main.py serve --lan
```

O servidor passa a aceitar computadores da sua rede privada (por exemplo, o notebook do sofá abrindo `http://IP-DO-COMPUTADOR:8765/`). O firewall pode pedir permissão. **Não há senha:** use só em rede em que você confia. O painel do admin só aceita outras máquinas com senha (`py main.py admin --lan --password SENHA`).

Outras opções: `--port`, `--content-dir` (pasta das trilhas, padrão `./content`) e `--db` (arquivo do banco, padrão `./data/k_study.db`).

## Estrutura de pastas

```text
main.py                  py main.py <comando>
CLAUDE.md                instruções de entrada para agentes de IA
README.md                este arquivo
specs/                   instruções detalhadas para agentes (entrevista, pipeline, vídeos, leituras, questões...)
docs/arquitetura.md      o contrato técnico (pastas, banco, API, CLI)
docs/modelo-de-dados.md  formato dos arquivos de uma trilha
src/k_study/             o programa (servidor, banco, validador, painel, interface)
content/<slug>/          uma pasta por trilha (trail.json, blocos, leituras, questões, transcrições)
data/k_study.db          o banco (alunos, progresso; fora do Git)
tests/                   testes (pytest)
```

## Criando uma trilha com um agente

O agente segue as `specs/`. Em resumo, ele conversa com você, propõe uma divisão, busca e confere vídeos, escreve as leituras e as questões, valida e entrega.

**Passo a passo**

1. Abra o agente na pasta do projeto (`claude`) e diga o que quer aprender.
2. O agente faz uma **entrevista curta** (3 rodadas): assunto e objetivo, prazo e tempo por dia, o que você já sabe e o que não sabe, idioma, material que você tem, tipos de questão, formato da avaliação, tom. Para cada pergunta ele sugere um padrão; basta confirmar.
3. Se você tem **material** (slides, PDFs, anotações), ele pede para guardar em `content/<slug>/materials/`.
4. O agente **sugere uma divisão** em blocos e aulas, a partir do material. Você aprova ou ajusta.
5. Ele pede **autorização para baixar o áudio** de vídeos do YouTube (só para transcrever localmente e conferir o que cada vídeo explica).
6. Com o plano aprovado, ele trabalha sozinho: busca vídeos, transcreve, **lê as transcrições inteiras**, escolhe os melhores trechos, escreve a **leitura do zero**, cria as **questões** e monta a trilha. Pode usar vários subagentes em paralelo.
7. Ele roda a validação e uma auditoria própria, e entrega um **relatório** curto: o que ficou pronto, o que não pôde ser verificado, o que você precisa decidir.
8. Você abre <http://localhost:8765/> e estuda.

**Exemplo de conversa**

> **Você:** Quero uma trilha sobre configuração de switches de rede.
>
> **Agente:** Antes de criar, algumas perguntas (sugiro o padrão em negrito): 1) Objetivo? **trabalho** / prova / hobby. 2) Prazo e horas por dia? **sem prazo, 1 h/dia**. 3) O que você já sabe de redes e o que não sabe? 4) Idioma? **português**. 5) Tem material (apostila, slides)? 6) Cai em alguma prova ou certificação?
>
> **Você:** Trabalho, 3 semanas, 1 h por dia. Sou desenvolvedor, sei HTTP e IP, não sei nada de VLAN nem de camada 2. Tenho um PDF da empresa. Sem prova.
>
> **Agente:** Proponho 3 blocos: (1) Fundamentos de camada 2 e VLAN; (2) Trunk, STP e roteamento entre VLANs; (3) Segurança e boas práticas. Cada aula tem vídeos em português, leitura com analogias de software e ~15 questões. Posso baixar o áudio dos vídeos para transcrever e conferir? Aprova a divisão?
>
> **Você:** Aprovado, pode baixar.
>
> **Agente:** (depois de algum tempo) Pronto: 3 blocos, 9 aulas, 41 vídeos (alguns só em trechos), 9 leituras e 135 questões, cerca de 1 h 40 por aula. Não consegui vídeo bom sobre STP rápido; a leitura cobre. Abra `http://localhost:8765/#/t/configuracao-de-switches`.

O agente também registra tudo em `content/<slug>/brief.md`, para você ou outro agente retomar depois.

## A trilha de exemplo

`content/aprendizagem-de-maquina/` traz quatro blocos para estudar aprendizado de máquina do zero, incluindo vídeos conferidos por transcrição, leituras e questões comentadas. É o padrão de qualidade que o agente tenta repetir. Os slides da disciplina original **não** são distribuídos. Para removê-la:

```bash
rm -r content/aprendizagem-de-maquina       # Windows PowerShell: Remove-Item -Recurse content\aprendizagem-de-maquina
py main.py sync
```

## O projeto irmão: k_transcriptor

Busca vídeos no YouTube, baixa **só o áudio** e transcreve localmente com o Whisper, para que o agente leia o que cada vídeo realmente diz antes de recomendá-lo. É outro repositório (`ktr` é o comando). O agente o clona e instala quando precisa (`specs/04-videos-e-k_transcriptor.md`); o repositório é `https://github.com/klawdyo/k_transcriptor.git`.

## Perguntas frequentes

**O que acontece com o meu e-mail?** Fica só no banco local (`data/k_study.db`). Nada é enviado a lugar nenhum. Não há verificação nem senha: quem digitar o seu e-mail vê o seu progresso, então não use o e-mail de outra pessoa nem exponha o servidor à internet.

**Onde ficam os meus dados?** No arquivo `data/k_study.db` (alunos, progresso, respostas, anotações, tempos). O conteúdo das trilhas fica em `content/`.

**Como faço backup?** Com o servidor parado, copie `data/k_study.db`. Com ele rodando, use `sqlite3 data/k_study.db ".backup backup.db"`. O `content/` está no Git.

**Como importo um progresso antigo?** `py main.py import-progress --email voce@exemplo.com --trail aprendizagem-de-maquina progress.json`.

**Como removo uma trilha?** Apague `content/<slug>/` e rode `py main.py sync`. O progresso dos alunos permanece no banco (se a pasta voltar, ele volta).

**Posso mudar a ordem ou o texto de uma aula?** Sim, editando os arquivos em `content/<slug>/`. Não mude os `id` já publicados: o progresso dos alunos depende deles.

**O agente errou algo no conteúdo.** Conserte o arquivo (ou peça ao agente). A validação (`py main.py validate`) confere a estrutura, não a qualidade; peça uma auditoria seguindo `specs/07-validacao-e-qualidade.md`.

**Preciso de internet?** O servidor roda local. Os vídeos são incorporados do YouTube e exigem internet.

## Limitações

- E-mail sem verificação nem senha; pensado para uso pessoal ou em grupo de confiança. Não é um serviço para a internet.
- O conteúdo é gerado por IA a partir de fontes que o agente leu: confira o que for crítico. A transcrição automática tem erros.
- A API não edita conteúdo; trilhas se editam em arquivo.
- A transcrição e a busca de vídeos dependem do YouTube, que pode bloquear o IP temporariamente (o k_transcriptor orienta o que fazer).

## Aviso sobre direitos de terceiros

Vídeos são apenas **linkados** (incorporados do YouTube); o k_study não os hospeda. As transcrições servem ao estudo pessoal e à conferência do conteúdo e não devem ser redistribuídas. Material de terceiros (slides, livros) **não** deve ser copiado literalmente nem publicado: o agente é instruído a parafrasear, gerar as próprias figuras e a citar o link original. Os termos do YouTube em geral proíbem baixar vídeos sem autorização do autor: use o k_transcriptor só para estudo, com poucos vídeos, e nunca compartilhe o áudio. Se você publicar este repositório, decida se `materials/` e `transcripts/` ficam fora dele (`.gitignore`).
