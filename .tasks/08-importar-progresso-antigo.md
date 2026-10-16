# 08 · Importar o progresso antigo para a conta do usuário (usuário)

**Depende de:** tarefa 01 (contas com senha e `kstudy import-progress`). **Exige o usuário:** só ele escolhe o e-mail, a senha e o nome da própria conta.

## Contexto

Antes das contas, o progresso de estudo ficava num único `progress.json` (itens feitos, respostas e anotações, com chaves `bloco/item`), gravado pela API antiga. Agora o progresso fica no banco, por aluno e por trilha. O arquivo antigo está no Drive do usuário, em `estudo/conteudo/progress.json` (dentro da pasta da disciplina de aprendizagem de máquina). **Nunca edite, mova nem apague esse arquivo**: o comando de importação só lê.

## Passos

1. O usuário sobe o servidor (`py main.py serve`), abre `http://localhost:8765/` e faz o **primeiro cadastro**: e-mail, senha, confirmação e nome. Essa conta vira administradora.
2. O agente confere o caminho do arquivo antigo com o usuário e roda:
   `kstudy import-progress --email <email do usuário> --trail aprendizagem-de-maquina "<caminho>/progress.json"`
3. O comando é idempotente e avisa sobre chaves que não existem mais na trilha (blocos e itens reorganizados desde então). Mostrar o relatório ao usuário.
4. Conferir na interface: aulas marcadas como feitas, respostas e anotações presentes, e que o progresso das questões que o usuário já tinha respondido continua correto.
5. **Não embaralhar** nem alterar ids de questões e de itens já respondidos.

## Aceite

O usuário vê o próprio progresso antigo ao entrar com a conta nova; o `progress.json` original continua intacto.

## Ao terminar

Atualize a linha 08 do manifesto e o "Registro" (quantos itens, respostas e anotações entraram e quais chaves não casaram).
