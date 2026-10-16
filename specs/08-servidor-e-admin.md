# 08 · Servidor, contas e administração

Esta spec é para **explicar à pessoa** como o servidor funciona e para você testar localmente, se tiver o repositório do k_study. Você, agente criador de trilhas, **não tem acesso ao servidor** de quem vai estudar: o que você entrega é o pacote `.zip` (`07`).

## Rodar o servidor

(Para rodar em Docker, veja o `README.md`: `docker build -t k_study .` e `docker run -p 8765:8765 -v k_study_data:/data k_study`.)

```bash
py main.py serve                          # http://localhost:8765/  (alunos em /, administração em /admin/)
py main.py serve --port 9000
py main.py serve --lan                    # aceita outros computadores da rede privada (exige e-mail e senha)
py main.py serve --content-dir D:\cursos --db D:\cursos\k_study.db --env D:\cursos\.env
```

- Um **único processo e uma única porta**: a área administrativa é parte do mesmo servidor (não existe o comando `admin` nem porta 8766).
- Padrões: `--content-dir ./content`, `--db ./data/k_study.db`, `--env ./.env`; ou as variáveis `K_STUDY_CONTENT`, `K_STUDY_DB`, `K_STUDY_ENV`.
- Sem instalar nada: `py main.py serve` usa só a biblioteca padrão. Com `pip install -e .` existe o comando `kstudy`.
- O servidor indexa `content/` ao iniciar e sempre que uma rota detecta mudança; `kstudy sync` força a reindexação.
- **`--lan`:** escuta em todas as interfaces, mas só aceita clientes de redes privadas e confere o cabeçalho `Host`. O firewall pode pedir permissão. Mesmo na rede local, todos entram com e-mail e senha.
- **HTTPS:** o servidor fala HTTP. Para expor fora do computador, ponha um proxy reverso com HTTPS na frente e defina `K_STUDY_HTTPS=1` (os cookies passam a ser `Secure`). Não o exponha direto na internet.

## Contas e segurança

- **O primeiro cadastro vira administrador.** Na primeira vez, a tela de entrada avisa. Depois disso, ninguém vira administrador pela interface; quem tem acesso ao computador pode usar `py main.py set-admin EMAIL` (recuperação).
- **Entrar:** a tela pede o e-mail; se a conta existe, pede a senha; se não existe, pede senha, confirmação e nome. **Não há confirmação por e-mail.** O nome e o e-mail do aluno aparecem juntos no topo e nas telas do administrador.
- **Senhas:** 8 a 128 caracteres e diferentes do e-mail. Guardadas só como hash (`scrypt` combinado com um segredo do servidor); nunca em texto puro. Esqueceu a senha? No computador do servidor: `py main.py reset-password EMAIL` (a nova senha é digitada no terminal, sem eco).
- **O segredo fica no `.env`** (`K_STUDY_SECRET`), criado automaticamente no primeiro uso, com permissão restrita quando o sistema permite, e **nunca vai para o Git** (está no `.gitignore`). **Faça backup do `.env` junto com o banco**: se o segredo se perder, todas as senhas deixam de valer (cada pessoa define uma nova com `reset-password`).
- **Entrar com o Google (opcional):** preencha `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` no `.env` (criadas vazias) e reinicie. O botão só aparece quando as duas estão preenchidas. O endereço de retorno é fixo no sistema e **não se coloca no `.env`**: no console do Google, em "URIs de redirecionamento autorizados", informe o endereço do servidor seguido de `/auth/oauth/google/callback` (por exemplo `http://localhost:8765/auth/oauth/google/callback`). Quem entra assim usa o e-mail verificado pelo Google; a conta criada dessa forma não tem senha.
- **Limite de tentativas:** muitas senhas erradas bloqueiam o e-mail (e o endereço) por alguns minutos.
- **Sessão:** cookie `HttpOnly` que expira por inatividade (30 dias) e, no máximo, em 90 dias; sair apaga a sessão no servidor.
- Toda alteração exige um token contra CSRF, e a interface nunca insere HTML vindo do conteúdo (a política de segurança do navegador também bloqueia scripts de fora). Cadastros em massa de um mesmo endereço também são limitados. A auditoria completa está em `docs/seguranca.md` (repositório do k_study).
- Contas antigas (de antes das senhas) continuam existindo: no primeiro acesso a pessoa define a senha e o nome, e o progresso é mantido.

## Área administrativa (`/admin/`)

Só quem é administrador a vê (o botão **Administração** aparece na grade de trilhas). Ela traz:

- **Visão geral, Alunos e Trilhas:** estatísticas (alunos ativos nos últimos 7 dias, tempo total de estudo, visitas, conclusão por trilha, tempo e **abandono** por aula, acerto por questão e questões mais erradas; detalhe por aluno com nome e e-mail). "Só abriu e saiu" = visita com menos de 10 s. Use para melhorar o conteúdo: uma questão que quase todos erram pode ter gabarito errado; um vídeo com abandono alto pode ser fraco.
- **Ativar e desativar trilhas:** uma trilha desativada some para os alunos; o progresso dos alunos continua guardado e volta se ela for reativada.
- **Importar trilha:** envia o pacote `.zip` gerado pelo agente (`kstudy pack`). O servidor confere tudo (caminhos, extensões, tamanho, conteúdo ativo, validação) antes de registrar. Se o slug já existir, é preciso marcar "substituir" (a troca é atômica e o progresso dos alunos é mantido). Pela linha de comando: `py main.py import-trail ARQUIVO.zip [--replace]`.
- **Baixar specs:** um zip com `CLAUDE.md`, `specs/**` e `docs/modelo-de-dados.md`, os mesmos arquivos que o agente local usa para criar trilhas. Não existe botão de criar trilha: o agente roda no computador de quem cria.

Como o tempo é medido: a interface envia um sinal a cada 10 s **somente com a aba visível e em foco**.

## Importar progresso antigo

Para trazer um `progress.json` do formato antigo (app de arquivo único) para uma conta que **já existe** (a pessoa precisa ter entrado uma vez):

```bash
py main.py import-progress --email aluno@exemplo.com --trail aprendizagem-de-maquina caminho/progress.json
```

O arquivo antigo tem `items`, `answers` e `notes`. O comando grava no banco para aquela conta. **Nunca edite o banco à mão.**

## Backup

O estado dos alunos está em **um arquivo**: `data/k_study.db` (SQLite em modo WAL; podem existir `-wal` e `-shm` ao lado enquanto o servidor roda), e o segredo está no `.env`. Para fazer backup com o servidor parado, copie o `.db` **e o `.env`**. Com o servidor rodando, use `sqlite3 data/k_study.db ".backup backup.db"` e copie o `.env`. O conteúdo (`content/`) pode ser versionado, com o cuidado descrito no README (material de terceiros).

## Remover uma trilha

- **Esconder dos alunos, sem apagar:** desative em `/admin/`.
- **Apagar de vez:** apague a pasta `content/<slug>/` e rode `py main.py sync`; a trilha sai do índice e da grade. O progresso dos alunos **permanece** no banco; se a pasta voltar, eles recuperam.

Para remover a trilha de exemplo: `rm -r content/aprendizagem-de-maquina` seguido de `py main.py sync`.

## Limitações

- Pensado para uso local ou para um grupo pequeno; não é um serviço de internet. Sem HTTPS próprio.
- A API não edita conteúdo: trilhas entram por pacote (ou arquivo) e se editam em arquivo.
- Transcrição de vídeos é CLI (k_transcriptor), não rota da API.
- Anotações e respostas são por aluno, mas o banco é um só: a última escrita vence.
