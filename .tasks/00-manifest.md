# Manifesto de tarefas

Este arquivo é o **índice e o registro de andamento** das tarefas do projeto. Cada tarefa é um arquivo desta pasta, **autossuficiente**: quem a executa não precisa de nenhuma conversa anterior. Mantenha este manifesto atualizado: ele é a memória do trabalho.

## Como um agente usa esta pasta

1. Leia este manifesto inteiro, depois `docs/arquitetura.md` (o contrato) e `CLAUDE.md`.
2. Escolha a **primeira tarefa `pendente` cujas dependências estejam `feita`** (ou a que o usuário indicar). Tarefas sem dependência entre si podem ser feitas em paralelo, cada uma em sua sessão e sua branch/worktree.
3. **Marque como `em andamento`** (na linha da tabela e com a data) e comite só isso: `chore(tasks): inicia a tarefa NN`.
4. Execute a tarefa **somente** nos arquivos que ela declara como seus. Siga as regras gerais abaixo.
5. Ao terminar, rode os testes e a checagem de aceite da tarefa; marque como `feita` na tabela, anote o último commit e acrescente, na seção "Registro", o que decidiu, o que encontrou e o que ficou pendente: `chore(tasks): conclui a tarefa NN`.
6. Se não puder concluir, marque `bloqueada` com o motivo e o que falta. **Não** deixe a tarefa como `em andamento` sem alguém trabalhando nela.
7. Tarefas marcadas **(usuário)** exigem uma ação ou autorização da pessoa dona do projeto: o agente prepara tudo, explica o passo e **espera**; nunca decide por ela.

Para começar uma sessão nova, basta dizer ao agente: *"Leia `.tasks/00-manifest.md` e execute a próxima tarefa disponível."*

## Regras gerais (valem para todas as tarefas)

- **Idioma:** código (arquivos, módulos, funções, variáveis, classes, tabelas, colunas, chaves JSON, comandos e opções) em **inglês**; specs, README, interface, mensagens vistas por pessoas, logs de operação, comentários e docstrings em **português do Brasil**.
- **Commits:** atômicos e mínimos (uma mudança lógica por commit), em Conventional Commits (`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `build`; `!` ou `BREAKING CHANGE:` para quebra), tipo em inglês e descrição em português, terminando com a linha em branco e `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. A versão do projeto é calculada pelos commits (SemVer): não edite a versão à mão.
- **Nunca** faça `push`, nem crie ou apague repositórios remotos, sem autorização explícita do usuário.
- **Só biblioteca padrão** do Python no servidor (3.10+). Sem rede nos testes.
- **Testes:** `python -c "import sys,os; sys.path[:0]=['src', os.path.expanduser('~/.local/lib/pylibs')]; import pytest; sys.exit(pytest.main(['-q','-p','no:cacheprovider']))"` na raiz do repositório (ou `pytest`, se instalado). Rode a suíte várias vezes quando mexer em concorrência.
- **Contrato:** `docs/arquitetura.md` manda. Achou lacuna ou contradição? Siga o espírito dele, registre no "Registro" abaixo e, se a tarefa não for a dona do contrato, **não** edite o contrato.
- **Segurança:** SQL sempre parametrizado, nenhuma rota por caminho de arquivo, nenhum segredo em código, log ou commit (`.env`, `data/` e `*.db` ficam fora do git).
- **Não cite ferramentas internas** de versionamento ou comandos exclusivos da máquina do autor em arquivos do projeto.
- **Dono dos arquivos:** cada tarefa lista os arquivos que pode editar; os testes dela ficam junto. Não mexa nos arquivos de outra tarefa.

## Tarefas

Base de todas: branch `trilhas`, commit do contrato revisão 2 (`docs: atualiza o contrato com login por senha, admin integrado, CSRF, rotas por id e pacotes zip`).

| NN | Arquivo | Título | Depende de | Status | Último commit |
| :-: | :-- | :-- | :-- | :-- | :-- |
| 01 | `01-nucleo-seguro.md` | Núcleo seguro: banco v2, contas com senha, CSRF, rotas por id, CLI | — | pendente | |
| 02 | `02-pacotes-zip.md` | Pacotes zip: importar trilha, empacotar trilha, zip das specs | — | pendente | |
| 03 | `03-interface-aluno.md` | Interface do aluno: login em etapas, nome, cores, rotas por id | contrato | pendente | |
| 04 | `04-area-admin.md` | Área administrativa: estatísticas, ativar, importar zip, baixar specs | contrato | pendente | |
| 05 | `05-specs-e-docs.md` | Specs e documentação da revisão 2 | contrato | pendente | |
| 06 | `06-auditoria-seguranca.md` | Auditoria OWASP e varredura de segredos | 01 a 05 unidas | pendente | |
| 07 | `07-renomear-diretorio.md` | Renomear a pasta `estudos` para `k_study` **(usuário)** | — | feita (2026-10-16) | |
| 08 | `08-importar-progresso-antigo.md` | Importar o progresso antigo para a conta do usuário **(usuário)** | 01 | pendente | |
| 09 | `09-publicar.md` | Unir `trilhas` ao `main` e publicar no GitHub **(usuário)** | 01 a 06 | pendente | |
| 10 | `10-limpar-o-drive.md` | Limpar do Drive o que migrou para o projeto **(usuário)** | 08, 09 | pendente | |

Status possíveis: `pendente`, `em andamento (AAAA-MM-DD)`, `feita (AAAA-MM-DD)`, `bloqueada (motivo)`. "Unidas" significa que os commits da tarefa já estão na branch de trabalho comum (`trilhas`).

Paralelismo: **01 a 05 podem rodar ao mesmo tempo** (arquivos diferentes; 01, 03 e 04 conversam pela API do contrato e só se encaixam depois de unidas). **06 só depois** de 01 a 05 unidas. A 07 já foi feita.

## Registro

Acrescente aqui, por tarefa, em ordem cronológica: decisões, lacunas do contrato, riscos, pendências. Formato: `### NN · AAAA-MM-DD · título curto` e uma lista.

### 00 · 2026-10-16 · Estado de partida

- Branch `trilhas` com a reestruturação para trilhas já feita (pacote `k_study`, banco SQLite, painel do admin separado, interface com e-mail, specs, trilha inicial de aprendizagem de máquina). 93 testes passando.
- Revisão 2 do contrato decidida e documentada em `docs/arquitetura.md`: login com senha (scrypt + segredo no `.env`), primeiro cadastro vira administrador, admin integrado ao `kstudy serve` (sem segunda porta, sem comando `admin`), CSRF, rotas por ids sem acesso a arquivo por caminho, pacotes zip de trilha, zip das specs para download, capa da trilha, barra de progresso contando tudo, marcas obrigatória/opcional coloridas.
- O projeto irmão `k_transcriptor` (busca, download e transcrição) está pronto em outro repositório; não faz parte destas tarefas.
- Pendências conhecidas fora das tarefas: nada foi enviado (`push`); o remoto `origin` já aponta para `klawdyo/k_study`.
- A pasta local foi renomeada de `estudos` para `k_study` pelo usuário (tarefa 07) e o comando `kstudy` foi reinstalado. Cuidado: programas que gravam no caminho antigo recriam a pasta `estudos`; use sempre `k_study`.
