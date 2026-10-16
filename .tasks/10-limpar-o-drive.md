# 10 · Limpar do Drive o que migrou para o projeto (usuário)

**Depende de:** tarefas 08 e 09. **Exige autorização explícita do usuário** antes de apagar ou mover qualquer coisa. O Drive é sincronizado entre computadores: peça confirmação item a item e **faça backup antes**.

## Contexto

O Drive (`G:\Meu Drive\Mestrado\2026.2 - Aprend. máquina`) deve guardar **só o material da disciplina** (para o projeto da disciplina e para o artigo): `Aulas/`, `Gyl/`, `Washington/`, `Projeto/`, `treinamento/`, `artigo/`, os PDFs de referência e as especificações dessas etapas. O que era do sistema de estudo migrou para o projeto k_study.

## Candidatos à limpeza (confirmar um por um com o usuário)

- `estudo/conteudo/` (conteúdo, transcrições, figuras, `progress.json`): o conteúdo foi copiado para `content/aprendizagem-de-maquina/` do k_study; o `progress.json` só deve ser removido **depois** de importado (tarefa 08) e de o usuário confirmar que viu o progresso na conta nova. Antes, copiar para um backup fora do Drive.
- `ferramentas/run_study_app.py` e `estudo/iniciar-estudo.bat`: atalhos do app antigo; apontam para caminhos e comandos que não existem mais.
- `especificacoes/10-app-de-estudo-e-conteudo.md` e `11-playbook-autonomo-blocos.md` (e a parte de questões da `09`): foram generalizados nas specs do k_study; manter só o que é específico da prova e da disciplina.
- Menções ao app no `CLAUDE.md` do Drive e em `01-memoria-do-projeto.md`: atualizar para apontar para o k_study.
- **Nunca** tocar em `Aulas/`, `Gyl/`, `Washington/`, `Projeto/*.docx`, `aprendizagem de maquina.pdf` e `Programas-das-Disciplinas-2022-v2.pdf` (somente leitura).

## Passos

1. Listar, mostrar ao usuário e obter a lista aprovada.
2. Backup da lista aprovada fora do Drive.
3. Remover ou mover só o aprovado; atualizar `CLAUDE.md` e a memória do Drive.
4. Conferir que nada que a disciplina ainda usa foi perdido.

## Ao terminar

Atualize a linha 10 do manifesto e o "Registro" (o que saiu, o que ficou, onde está o backup).
