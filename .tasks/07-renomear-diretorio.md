# 07 · Renomear a pasta `estudos` para `k_study` (usuário)

**Depende de:** nada. **Status real:** concluída pelo usuário em 2026-10-16 (a pasta agora é `k_study`).

## O que era

O repositório local vivia em `estudos` (nome do projeto antigo); o repositório remoto já se chama `k_study`. Renomear a pasta exigia que nenhum terminal, editor ou navegador estivesse com ela aberta (o Windows nega o acesso).

## O que foi feito e o que conferir

- Pasta renomeada para `k_study`; `origin` já apontava para `git@github.com:klawdyo/k_study.git`.
- Reinstalar o comando para apontar para a pasta nova: `python -m pip install -e . --no-deps`, depois `kstudy --version`.
- Conferir que não sobrou pasta `estudos` vazia ao lado (arquivos gravados por programas com o caminho antigo podem recriá-la) e que nenhum documento do projeto cita o caminho antigo.
- Atalhos e scripts fora do repositório que citem `F:\dev\Python\estudos` (por exemplo, no Drive) ficam obsoletos; a tarefa 10 cuida deles.
