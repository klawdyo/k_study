# k_study

Servidor local de **trilhas de aprendizagem**: cursos com vídeos recortados, leituras explicadas do zero e questões com todas as alternativas comentadas. As trilhas são **criadas por agentes de IA** (como o Claude Code) que rodam no computador de quem cria, a partir do assunto que a pessoa quer aprender e do material que ela tiver. Cada aluno tem conta e progresso próprios; o administrador importa trilhas, ativa e desativa trilhas e vê estatísticas de uso.

- Para **estudar** ou **administrar**, você só precisa de Python 3.10+. Não instala nada.
- Para **criar uma trilha nova**, o administrador baixa as **specs** pelo próprio servidor, abre um agente de IA numa pasta vazia e pede a trilha. O agente entrega um pacote `.zip`, que o administrador **importa** pelo servidor.

## O fluxo completo

```text
 servidor (/admin/)            computador de quem cria              servidor (/admin/)
 ─────────────────             ────────────────────────             ──────────────────
 1. Baixar specs  ──────────►  2. Abrir um agente de IA numa
    (um .zip)                     pasta vazia e descompactar
                                  as specs; pedir a trilha
                               3. O agente faz a entrevista, busca
                                  e transcreve vídeos, escreve
                                  leituras e questões, valida
                               4. kstudy pack <slug>  ───────────►  5. Importar trilha (.zip)
                                  gera <slug>.zip                      (e ativar para os alunos)
```

A criação acontece **fora do servidor**: ele não tem botão de criar trilha, só de **importar**.

## Começando (para estudar e administrar)

1. **Clone o projeto.**

   ```bash
   git clone https://github.com/klawdyo/k_study.git k_study
   cd k_study
   ```

2. **Suba o servidor.**

   ```bash
   py main.py serve
   ```

   No Linux/macOS, use `python3 main.py serve`. Na primeira vez ele cria o arquivo `.env` com um segredo (veja "Contas e segurança").

3. **Abra no navegador:** <http://localhost:8765/>. A tela pede o seu **e-mail**. Como ainda não existe nenhuma conta, você cria a sua (nome, senha e confirmação): **a primeira conta criada vira a administradora**.

4. **Escolha uma trilha** na grade e comece pela primeira aula. A trilha de exemplo (`aprendizagem-de-maquina`) já vem incluída.

5. **Administradora?** Na grade de trilhas aparece o botão **Administração** (`/admin/`): estatísticas, ativar e desativar trilhas, importar trilhas e baixar as specs.

## Requisitos

| Para | Precisa de |
| :-- | :-- |
| Estudar e administrar | Python 3.10 ou superior. Nada mais (só a biblioteca padrão) |
| Criar trilhas | um agente de IA com acesso ao terminal (Claude Code), o comando `kstudy` (instala-se com `pip install -e .`) e o projeto irmão **k_transcriptor** para transcrever vídeos (ele instala o que precisa) |
| Transcrição rápida (opcional) | placa NVIDIA com CUDA; sem ela roda na CPU, mais devagar |

## Comandos

Sem instalar nada: `py main.py <comando>`. Com `pip install -e .` o comando `kstudy` faz o mesmo (`kstudy --help` lista tudo, em português).

| Comando | Para quê |
| :-- | :-- |
| `serve [--port 8765] [--host H] [--lan] [--content-dir D] [--db F] [--env F]` | sobe o servidor (alunos em `/`, administração em `/admin/`) |
| `validate [slug]` | valida uma trilha (ou todas); erros reprovam, avisos só avisam |
| `new-trail SLUG --title T [--description D]` | cria `content/<slug>/` com a estrutura mínima |
| `pack SLUG [--out FILE]` | valida e gera o pacote `.zip` importável |
| `import-trail ARQUIVO.zip [--replace]` | importa um pacote (o mesmo que o administrador faz pela interface) |
| `sync [--force]` | reindexa `content/` no banco |
| `trails` | lista as trilhas e seus números |
| `set-admin EMAIL` | torna uma conta existente administradora (recuperação) |
| `reset-password EMAIL` | define uma nova senha para uma conta (digitada no terminal, sem eco) |
| `import-progress --email E --trail SLUG ARQUIVO.json` | importa um `progress.json` antigo para uma conta existente |

Códigos de saída: 0 ok, 1 problemas de validação, 2 erro de uso ou de ambiente.

## Contas e segurança

- **Entrar:** a tela pede o e-mail (e, se o Google estiver configurado, mostra também o botão **Entrar com o Google**); se a conta existe, pede a senha; se não existe, pede senha, confirmação e nome. **Não há confirmação por e-mail.** O nome e o e-mail aparecem juntos no topo e nas telas do administrador.
- **O primeiro cadastro vira administrador.** Depois, ninguém vira administrador pela interface; quem tem acesso ao computador usa `py main.py set-admin EMAIL`.
- **Senhas:** 8 a 128 caracteres, diferentes do e-mail; guardadas só como hash (`scrypt` combinado com um segredo do servidor).
- **O segredo fica no `.env`** (`K_STUDY_SECRET`), criado automaticamente no primeiro uso e **nunca versionado** (está no `.gitignore`). **Faça backup do `.env` junto com o banco**: sem o mesmo segredo, as senhas deixam de valer (cada pessoa recebe uma nova com `reset-password`).
- **Limite de tentativas**, sessão com validade e logout no servidor, proteção contra CSRF, política de segurança de conteúdo e conteúdo das trilhas sempre escapado: a auditoria completa (modelo de ameaças, OWASP, riscos residuais) está em `docs/seguranca.md`.
- **Rede local (`--lan`):** `py main.py serve --lan` aceita também computadores da sua rede privada (por exemplo, o notebook do sofá abrindo `http://IP-DO-COMPUTADOR:8765/`). O firewall pode pedir permissão. Todos entram com e-mail e senha.
- **HTTPS:** o servidor fala HTTP. Para uso fora do seu computador, ponha um proxy reverso com HTTPS na frente e defina `K_STUDY_HTTPS=1` (cookies `Secure`). **Não o exponha direto na internet.**

Outras opções: `--port`, `--content-dir` (pasta das trilhas, padrão `./content`), `--db` (arquivo do banco, padrão `./data/k_study.db`) e `--env` (arquivo do segredo, padrão `./.env`).

## Entrar com o Google (opcional)

O botão **Entrar com o Google** só aparece quando o servidor está configurado para isso. As duas variáveis nascem **vazias** no `.env` (e estão no `.env.example`); enquanto estiverem vazias, a tela de entrada não mostra o botão.

1. No [console do Google](https://console.cloud.google.com/apis/credentials), crie um **ID do cliente OAuth** do tipo "Aplicativo da Web".
2. Em **URIs de redirecionamento autorizados**, informe o endereço do seu servidor seguido de `/auth/oauth/google/callback`. Por exemplo:
   - `http://localhost:8765/auth/oauth/google/callback`
   - `https://estudos.seudominio.com/auth/oauth/google/callback`
3. Preencha no `.env` (ou como variáveis de ambiente) `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` e reinicie o servidor. Ao subir, ele diz se a entrada com o Google está ativa.

O endereço de retorno **não vai no `.env`**: ele é fixo no sistema (`/auth/oauth/google/callback`) e só é informado no Google. A pessoa entra com o e-mail verificado pelo Google; a conta criada assim não tem senha (e não pode ser "reivindicada" por quem souber o e-mail). Detalhes de segurança em `docs/seguranca.md`.

## Docker (para subir em um servidor)

O `Dockerfile` roda o servidor sem precisar de Python na máquina. Não há dependências para instalar.

```bash
docker build -t k_study .
docker run -d --name k_study -p 8765:8765 -v k_study_data:/data k_study
```

Abra <http://localhost:8765/>: o primeiro cadastro vira administrador. Tudo o que precisa sobreviver fica no volume `/data`: o banco (`k_study.db`), o `.env` com o segredo (criado no primeiro uso) e as trilhas importadas (`/data/content`). Importe trilhas em `/admin/` (ou monte uma pasta existente com `-v ./content:/data/content`). Detalhes:

| O quê | Como |
| :-- | :-- |
| Entrada com o Google | `-e GOOGLE_CLIENT_ID=... -e GOOGLE_CLIENT_SECRET=...` (no Google, a URI de retorno é `<endereço do servidor>/auth/oauth/google/callback`) |
| Atrás de um domínio com HTTPS (proxy reverso) | `-e K_STUDY_ALLOWED_HOSTS=estudos.seudominio.com -e K_STUDY_HTTPS=1`. Sem isso o servidor só aceita `localhost` no cabeçalho `Host` |
| Segredo fixo em vez do arquivo | `-e K_STUDY_SECRET=...` (64 caracteres hexadecimais; o ambiente vale mais que o `.env`) |
| Backup | copie o volume `/data` inteiro (banco **e** `.env`), por exemplo `docker run --rm -v k_study_data:/data -v "$PWD":/backup alpine tar czf /backup/k_study.tgz /data` |
| Saúde e parada | a imagem tem `HEALTHCHECK`; `docker stop` encerra em menos de um segundo |

O contêiner roda como usuário sem privilégios (uid 10001) e o servidor fala **HTTP**: para expor na internet, ponha um proxy reverso com HTTPS na frente (veja `docs/seguranca.md`). O `.dockerignore` mantém `.env`, `data/` e `content/` fora da imagem.

## O que o aluno vê

- **Entrada por e-mail e senha**, com o progresso guardado na conta (o mesmo em qualquer computador).
- **Grade de trilhas** com capa, descrição, nível, número de aulas, minutos e quanto você já fez (a barra conta todas as aulas, obrigatórias e opcionais).
- **Aulas** na ordem de estudo, cada uma marcada **Obrigatória** ou **Opcional** (com cores diferentes): vídeos (com trechos recomendados e avisos de onde o vídeo diverge do material), leituras explicadas do zero e questões.
- **Vídeos** incorporados do YouTube, com botões para os trechos que importam e um cartão de **transcrição** com horários clicáveis.
- **Questões** com resposta imediata e **explicação de todas as alternativas**, certas e erradas.
- **Anotações** por aula e **barra de progresso** da trilha e do bloco; o botão "Próxima aula" aponta o que vem a seguir.

## O que o administrador faz (`/admin/`)

- **Visão geral, Alunos e Trilhas:** alunos ativos, tempo total de estudo, visitas, conclusão por trilha, tempo e abandono por aula, acertos por questão e as questões mais erradas, sempre com **nome e e-mail**. Serve para melhorar o conteúdo.
- **Ativar e desativar trilhas:** uma trilha desativada some para os alunos; o progresso deles fica guardado.
- **Importar trilha:** envia o `.zip` gerado pelo agente. O servidor confere tudo antes de registrar (caminhos, extensões, tamanho, conteúdo ativo, validação). Se a trilha já existir, é preciso marcar "substituir" (o progresso dos alunos é mantido).
- **Baixar specs:** o zip que o agente local usa para criar trilhas.

Detalhes em `specs/08-servidor-e-admin.md`.

## Estrutura de pastas

```text
main.py                  py main.py <comando>
.env                     segredo local e credenciais do Google (criado no primeiro uso; fora do Git)
.env.example             modelo do .env, sem segredos (este vai para o Git)
Dockerfile               imagem para subir o servidor (veja a seção Docker)
CLAUDE.md, AGENTS.md, GEMINI.md, OPENCODE.md  instruções de entrada para agentes de IA
README.md                este arquivo
specs/                   instruções detalhadas para agentes (entrevista, pipeline, vídeos, leituras, questões, pacote...)
docs/arquitetura.md      o contrato técnico (pastas, banco, API, CLI, segurança)
docs/modelo-de-dados.md  formato dos arquivos de uma trilha
src/k_study/             o programa (servidor, segurança, banco, pacotes, validador, interface do aluno e administração)
content/<slug>/          uma pasta por trilha (trail.json, blocos, leituras, questões, transcrições, capa)
data/k_study.db          o banco (contas, progresso; fora do Git)
tests/                   testes (pytest)
.tasks/                  tarefas planejadas e o registro do trabalho feito
```

## Criando uma trilha com um agente

O agente segue as `specs/`. Em resumo, ele conversa com você, propõe uma divisão, busca e confere vídeos, escreve as leituras e as questões, valida, empacota e entrega um `.zip`.

**Passo a passo**

1. No servidor, a administradora baixa as **specs** em `/admin/` e as descompacta numa **pasta vazia** do computador de quem vai criar.
2. Nessa pasta, abre um agente de IA (por exemplo, `claude`) e diz o que quer aprender. O agente confere o ambiente (Python 3.10+, `kstudy`, k_transcriptor); se faltar algo, ele explica o que instalar.
3. O agente faz uma **entrevista curta** (3 rodadas): assunto e objetivo, prazo e tempo por dia, o que você já sabe e o que não sabe, idioma, material que você tem, tipos de questão, formato da avaliação, tom, se quer uma capa. Para cada pergunta ele sugere um padrão; basta confirmar.
4. Se você tem **material** (slides, PDFs, anotações), ele pede para guardar em `content/<slug>/materials/`.
5. O agente **sugere uma divisão** em blocos e aulas, a partir do material. Você aprova ou ajusta.
6. Ele pede **autorização para baixar o áudio** de vídeos do YouTube (só para transcrever localmente e conferir o que cada vídeo explica).
7. Com o plano aprovado, ele trabalha sozinho: busca vídeos, transcreve, **lê as transcrições inteiras**, escolhe os melhores trechos, escreve a **leitura do zero**, cria as **questões** e monta a trilha. Pode usar vários subagentes em paralelo. Se você quiser, gera uma **capa** (1200×630, até 1 MB).
8. Ele roda a validação e uma auditoria própria, **empacota** (`kstudy pack`) e entrega um **relatório** curto: o que ficou pronto, o que não pôde ser verificado, o que você precisa decidir, e onde está o `.zip`.
9. A administradora abre `/admin/` → **Importar trilha** e envia o `.zip`. Os alunos já podem estudar.

**Exemplo de conversa**

> **Você:** Quero uma trilha sobre configuração de switches de rede.
>
> **Agente:** Antes de criar, algumas perguntas (sugiro o padrão em negrito): 1) Objetivo? **trabalho** / prova / hobby. 2) Prazo e horas por dia? **sem prazo, 1 h/dia**. 3) O que você já sabe de redes e o que não sabe? 4) Idioma? **português**. 5) Tem material (apostila, slides)? 6) Cai em alguma prova ou certificação? 7) Quer uma capa para a trilha? **sim**.
>
> **Você:** Trabalho, 3 semanas, 1 h por dia. Sou desenvolvedor, sei HTTP e IP, não sei nada de VLAN nem de camada 2. Tenho um PDF da empresa. Sem prova.
>
> **Agente:** Proponho 3 blocos: (1) Fundamentos de camada 2 e VLAN; (2) Trunk, STP e roteamento entre VLANs; (3) Segurança e boas práticas. Cada aula tem vídeos em português, leitura com analogias de software e ~15 questões. Posso baixar o áudio dos vídeos para transcrever e conferir? Aprova a divisão?
>
> **Você:** Aprovado, pode baixar.
>
> **Agente:** (depois de algum tempo) Pronto: 3 blocos, 9 aulas, 41 vídeos (alguns só em trechos), 9 leituras e 135 questões, cerca de 1 h 40 por aula. Não consegui vídeo bom sobre STP rápido; a leitura cobre. O pacote está em `configuracao-de-switches.zip`: peça à administradora para enviá-lo em `/admin/` → Importar trilha.

O agente também registra tudo em `content/<slug>/brief.md`, para você ou outro agente retomar depois.

## A trilha de exemplo

`content/aprendizagem-de-maquina/` traz quatro blocos para estudar aprendizado de máquina do zero, incluindo vídeos conferidos por transcrição, leituras e questões comentadas. É o padrão de qualidade que o agente tenta repetir. Os slides da disciplina original **não** são distribuídos. Para escondê-la dos alunos, desative-a em `/admin/`; para removê-la:

```bash
rm -r content/aprendizagem-de-maquina       # Windows PowerShell: Remove-Item -Recurse content\aprendizagem-de-maquina
py main.py sync
```

## O projeto irmão: k_transcriptor

Busca vídeos no YouTube, baixa **só o áudio** e transcreve localmente com o Whisper, para que o agente leia o que cada vídeo realmente diz antes de recomendá-lo. É outro repositório (`ktr` é o comando). O agente o clona e instala quando precisa (`specs/04-videos-e-k_transcriptor.md`); o repositório é `https://github.com/klawdyo/k_transcriptor.git` e a instalação é `py main.py setup`.

## Dados reais e repositórios públicos

`content/` pode conter **material de terceiros** (slides, textos) em `materials/` e **transcrições automáticas** de vídeos em `transcripts/`. Eles servem ao estudo pessoal e **não devem ser redistribuídos**. Se você publicar um repositório com as suas trilhas, **decida antes** se `materials/` e `transcripts/` ficam fora dele (`.gitignore`). Nunca versione o `.env`, o banco (`data/`) nem áudios. O repositório já ignora `.env`, `data/` e `*.db`.

## Convenções do projeto (para quem for evoluir o código)

- **Idioma:** código, arquivos de código, tabelas, colunas, chaves JSON, comandos e códigos de erro em **inglês**; specs, README, interface, mensagens para pessoas, comentários e docstrings em **português do Brasil**.
- **Commits:** atômicos, em Conventional Commits (tipo em inglês, descrição em português). **A versão é calculada pelos commits** (SemVer): não a edite à mão.
- **Contrato:** `docs/arquitetura.md` manda; mudou algo, mude o contrato primeiro. Testes com `pip install -e ".[dev]"` e `pytest`.

## Perguntas frequentes

**O que acontece com o meu e-mail?** Fica só no banco local (`data/k_study.db`). Nada é enviado a lugar nenhum.

**Onde ficam os meus dados?** No arquivo `data/k_study.db` (contas, progresso, respostas, anotações, tempos) e, para as senhas, o segredo do `.env`. O conteúdo das trilhas fica em `content/`.

**Como faço backup?** Com o servidor parado, copie `data/k_study.db` **e `.env`**. Com ele rodando, use `sqlite3 data/k_study.db ".backup backup.db"` e copie o `.env`.

**Esqueci a minha senha.** No computador do servidor: `py main.py reset-password voce@exemplo.com`.

**Fui o primeiro a me cadastrar por engano e não sou eu quem administra.** `py main.py set-admin EMAIL` torna outra conta administradora (rode no computador do servidor).

**Como importo um progresso antigo?** A conta precisa existir (entre uma vez). Depois: `py main.py import-progress --email voce@exemplo.com --trail aprendizagem-de-maquina progress.json`.

**Como removo uma trilha?** Desative-a em `/admin/` (some para os alunos, o progresso fica) ou apague `content/<slug>/` e rode `py main.py sync`.

**Posso mudar a ordem ou o texto de uma aula?** Sim, editando os arquivos em `content/<slug>/` (ou trocando a trilha por um pacote novo com "substituir"). Não mude os `id` já publicados: o progresso dos alunos depende deles.

**O agente errou algo no conteúdo.** Conserte o arquivo (ou peça ao agente). A validação (`py main.py validate`) confere a estrutura, não a qualidade; peça uma auditoria seguindo `specs/07-validacao-e-qualidade.md`.

**Preciso de internet?** O servidor roda local. Os vídeos são incorporados do YouTube e exigem internet.

## Limitações

- Sem confirmação de e-mail: quem cria a conta primeiro com um e-mail é o dono dele. Pensado para uso pessoal ou em grupo de confiança; não é um serviço aberto na internet.
- O conteúdo é gerado por IA a partir de fontes que o agente leu: confira o que for crítico. A transcrição automática tem erros.
- A API não edita conteúdo; trilhas entram por pacote ou arquivo.
- A transcrição e a busca de vídeos dependem do YouTube, que pode bloquear o IP temporariamente (o k_transcriptor orienta o que fazer).

## Aviso sobre direitos de terceiros

Vídeos são apenas **linkados** (incorporados do YouTube); o k_study não os hospeda. As transcrições servem ao estudo pessoal e à conferência do conteúdo e não devem ser redistribuídas. Material de terceiros (slides, livros) **não** deve ser copiado literalmente nem publicado: o agente é instruído a parafrasear, gerar as próprias figuras e a citar o link original. Os termos do YouTube em geral proíbem baixar vídeos sem autorização do autor: use o k_transcriptor só para estudo, com poucos vídeos, e nunca compartilhe o áudio.
