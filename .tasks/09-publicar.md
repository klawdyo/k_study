# 09 · Unir `trilhas` ao `main` e publicar no GitHub (usuário)

**Depende de:** tarefas 01 a 06 feitas. **Exige autorização explícita do usuário** para cada passo que altera o remoto.

## Antes de qualquer envio

1. A tarefa 06 precisa estar `feita`: varredura de segredos limpa (ou o procedimento aprovado pelo usuário) e `docs/seguranca.md` concluído.
2. Suíte inteira verde (`pytest`) no k_study e no k_transcriptor.
3. Conferir o que vai ao GitHub: `.env`, `data/` e `*.db` fora do git; `content/` só com a trilha inicial; nenhum dado pessoal.
4. Conferir os remotos: k_study → `git@github.com:klawdyo/k_study.git`; k_transcriptor → `https://github.com/klawdyo/k_transcriptor.git`.

## Passos (cada um só com o "pode" do usuário)

1. Unir `trilhas` ao `main` do k_study (o `main` tem commits antigos de transcrição que migraram para o k_transcriptor; decidir com o usuário entre unir mantendo o histórico ou substituir o `main` pela `trilhas`; **não** use `push --force` sem autorização explícita).
2. `git push` do k_study e do k_transcriptor.
3. Conferir no GitHub: README renderizando, `.gitignore` efetivo, nenhum arquivo indevido.
4. Se o usuário quiser, criar uma versão (as mensagens dos commits já seguem Conventional Commits, então a versão pode ser calculada por elas); só quando ele mandar.

## Ao terminar

Atualize a linha 09 do manifesto e o "Registro" (o que foi enviado, para onde, em que commit).
