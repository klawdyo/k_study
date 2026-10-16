# 05 · Specs e documentação da revisão 2

**Depende de:** só do contrato.

## Leia primeiro

`docs/arquitetura.md` (revisão 2), `CLAUDE.md`, `README.md`, todos os arquivos de `specs/`, `docs/modelo-de-dados.md` e `.tasks/00-manifest.md` (regras gerais).

## Arquivos desta tarefa

`CLAUDE.md`, `README.md`, `specs/**`, `docs/modelo-de-dados.md`. **O `CLAUDE.md` deve manter** a seção que manda ler `.tasks/00-manifest.md` e seguir o protocolo.

## Contexto

O agente que cria trilhas roda **localmente**, na máquina de quem cria, e **não** tem acesso ao servidor: ele entrega um **pacote zip** que o administrador importa pela área administrativa. As specs que o administrador baixa em `/admin/` (zip de `CLAUDE.md`, `specs/**` e `docs/modelo-de-dados.md`) são EXATAMENTE os arquivos deste repositório, então escreva-as para funcionarem sozinhas fora dele: nada que dependa de arquivos que não estejam nesse zip (se precisar citar o contrato, copie o essencial para as specs).

## O que fazer

1. **Fluxo ponta a ponta** (specs 00 e 03): o admin baixa o zip das specs → abre um agente de IA numa pasta vazia → descompacta → o agente (exigindo que a pessoa instale Python 3.10+) baixa o k_transcriptor (`https://github.com/klawdyo/k_transcriptor.git`), roda o `setup` dele, conduz a entrevista, cria a pasta da trilha `content/<slug>/` (com `py main.py new-trail` se tiver o projeto k_study; senão à mão, com os templates da spec 09), valida (`kstudy validate`, ou a checklist da spec 07), **empacota** (`kstudy pack <slug>`; senão cria o zip à mão com uma única pasta de topo `<slug>/` seguindo EXATAMENTE as regras do pacote: extensões permitidas, sem links simbólicos, limites, sem HTML nem JS) e entrega o `.zip` → o admin o envia em "Importar trilha". Deixe claro que a criação acontece fora do servidor e que o servidor não tem botão de criar trilha.
2. **Capa da trilha:** o agente PODE gerar uma imagem de capa (1200×630, png, jpg ou webp, até 1 MB) e registrá-la no `trail.json` no campo `cover` (caminho relativo, por exemplo `cover.webp`). Descreva como (ferramentas de imagem do agente, ou perguntar à pessoa), as regras de direitos (sem logotipos nem personagens de terceiros, sem texto minúsculo) e que é opcional. Atualize `docs/modelo-de-dados.md` e a spec 09 (template do `trail.json`) com `cover`.
3. **Contas e segurança** (README e spec 08): o primeiro cadastro vira administrador; login por e-mail e senha, com nome; senhas com scrypt e segredo no `.env` (criado no primeiro uso, nunca versionado; fazer backup junto com o banco); sem confirmação por e-mail; limite de tentativas; admin integrado ao mesmo servidor (sem segunda porta); o admin ativa e desativa trilhas, importa zip e baixa as specs; recuperação por `kstudy set-admin EMAIL` e `kstudy reset-password EMAIL`; `--lan`; `K_STUDY_HTTPS`. Remova toda menção ao comando `admin`, à porta 8766 e a rotas por caminho de arquivo.
4. Atualizar o **README** (muito descritivo, para pessoas) e o **CLAUDE.md** (curto e firme) com tudo isso, o CLI novo (`serve`, `validate`, `new-trail`, `pack`, `import-trail`, `sync`, `trails`, `set-admin`, `reset-password`, `import-progress`), `py main.py` no Windows, o aviso de que dados reais em `content/` não devem ir para um git público e a convenção de idioma e de commits (atômicos, Conventional Commits; versão pelos commits, sem editar à mão).
5. Manter a qualidade e as regras aprendidas nas specs (vídeos conferidos por transcrição, mm:ss reais, sem sobreposição, didático para o nível, questões equilibradas, sem LaTeX etc.). Ajustar a spec 04 (k_transcriptor): o comando de instalação dele é `py main.py setup`; usar `py main.py` ou `ktr` conforme instalado; o cache dele é próprio (`ktr where`).
6. Conferir consistência total com `docs/arquitetura.md` (comandos, rotas, pastas, campos) e entre as specs. Contradição no contrato? Registre no "Registro" do manifesto (não edite o contrato).

## Aceite

Uma pessoa que leia só o zip de specs consegue criar e empacotar uma trilha válida; nenhuma menção a recursos removidos; links e comandos consistentes.

## Ao terminar

Atualize a linha 05 do manifesto e o "Registro".
