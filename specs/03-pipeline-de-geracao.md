# 03 · Pipeline de geração, de ponta a ponta

Roteiro autônomo para criar uma trilha. Pré-requisito: entrevista aprovada e `brief.md` gravado (`01`). Daqui em diante você **não pede confirmação para passar de uma etapa à seguinte**: decide, registra no brief e segue. Só pare se estiver bloqueado (permissão, arquivo inexistente, YouTube bloqueando) ou se algo mudar o escopo.

Monte sua lista de tarefas (ferramenta de tarefas, ou `content/<slug>/_tarefas.md` que você atualiza) e execute até o fim.

## Etapa 0 · Preparação

1. `py main.py new-trail <slug> --title ... --description ...`.
2. Coloque o material em `materials/`; extraia o texto de cada arquivo para `materials/_text/<arquivo>.txt` (cache seu: não reabra arquivos pesados depois). Guarde a **numeração** (slide N, página N) porque `goals`, `slides` e as leituras citam isso.
3. Instale e teste o k_transcriptor (`04`): `ktr doctor`.
4. Divisão aprovada → crie a lista de aulas.

## Etapa 1 · Por aula: tópicos do material

Para cada aula, liste **todos os tópicos** do material com o número do slide/página. É o **critério de cobertura**: vídeos, leitura e questões serão conferidos contra essa lista. Material só com figura (`[IMAGEM]`) não se confere pelo texto: abra e descreva, ou marque "a verificar".

## Etapa 2 · Busca e escolha de candidatos de vídeo

Detalhes e regras em `04`. Meta: **8 a 12 candidatos por aula**, vários termos por tópico (idioma preferido primeiro; termos do material e sinônimos), triagem por duração/canal/visualizações/título. Os títulos podem vir traduzidos automaticamente; a transcrição revela o idioma real.

## Etapa 3 · Transcrição (em segundo plano)

`ktr transcribe ID ... --language auto --copy-to content/<slug>/transcripts` (fila única; só downloads de áudio um por vez). Enquanto roda, avance as etapas 4 e 5 da aula anterior ou escreva leituras.

## Etapa 4 · Leitura das transcrições e curadoria

Leia **cada transcrição inteira**, por minuto (`ktr text ID`), contra a lista de tópicos. Para cada vídeo: o que cobre (`mm:ss`), o que não cobre, divergências com o material, nível, veredito. Escreva a **ficha** da aula (`04`, seção de fichas). **Segunda rodada obrigatória** se um tópico importante ficar sem vídeo bom (nova busca, transcrição, leitura); só aceite "lacuna coberta pela leitura" depois de duas rodadas. Não complete a lista com vídeo fraco.

## Etapa 5 · Leitura do zero e questões

Em paralelo à curadoria (subagentes, ver abaixo): `aula-N-do-zero.md` (`05`) e `lesson-N-questions.json` (`06`). Execute os códigos que aparecerem.

## Etapa 6 · Integração

Quem integra é **o agente principal**: monta `block-N/block.json` (vídeos na ordem do material com `clips`, `warnings`, `goals`, `transcript`, `review`; depois leitura; depois questões), registra o bloco em `trail.json`, roda o **embaralhamento determinístico** das alternativas (`06`, seção de posições), `py main.py validate <slug>` e `py main.py sync`.

## Etapa 7 · Auditoria própria

Siga `07`. Inclui conferir pessoalmente os vídeos descartados e a cobertura. Só então rode `ktr clean` (se tiver certeza) e entregue.

## Paralelização com subagentes

Contexto grande faz agentes se perderem: **um bloco por vez, e dentro dele um subagente por tarefa fechada e independente**. O agente principal faz a entrevista, a divisão, a integração e a auditoria.

Tarefas típicas (por aula):

| Tarefa | Entrada | Saída | Dono dos arquivos |
| :-- | :-- | :-- | :-- |
| (a) Leitura do zero | tópicos do aula (texto extraído), perfil, `05` | `aula-N-do-zero.md` | só esse arquivo e `figures/aN_*.png` |
| (b) Questões | tópicos, a leitura (para alinhar), perfil, `06` | `lesson-N-questions.json` | só esse arquivo |
| (c) Conferência dos vídeos | transcrições da aula, tópicos, `04` | `validacao-videos-aula-N.md` | só a ficha |
| (d) Guia e questões de código | códigos da leitura, `06` | `guia-*.md`, `code-questions.json` | só esses |
| (e) Auditoria independente | a trilha pronta, `07` | lista de achados | nenhum (só lê) |

**Regras de dono de arquivo:** cada subagente escreve **somente nos arquivos listados para ele**. **Nenhum subagente edita `block.json` nem `trail.json`**: só o agente principal integra. Cada prompt de subagente deve conter: o exemplar a imitar (a trilha de exemplo `content/aprendizagem-de-maquina/` ou um arquivo já pronto), caminhos exatos de entrada e saída, o perfil do leitor, as regras da spec correspondente copiadas ou citadas, o formato do relatório curto de volta, e a ordem de validar o JSON e conferir figuras. Peça relatório curto (o que fez, o que não verificou, dúvidas); não aceite o relatório de outro agente como substituto da sua leitura nos pontos críticos (vídeos descartados, cobertura).

No tempo de espera de um subagente, faça buscas e transcrições da aula seguinte.

## Meta de tempo por aula

Cada aula tem uma **meta de tempo obrigatório** derivada da entrevista (padrão: **60 a 120 min por aula**, mais para a de mais tópicos). Some: vídeos obrigatórios (só os `clips`) + leitura (≈ 150 linhas por 10 min de leitura atenta) + questões (≈ 2 a 3 min cada). O que passar da meta vira `optional`. Registre os totais por aula no brief.

## Critérios de pronto (por bloco e para a trilha)

- [ ] `py main.py validate <slug>` sem erros; avisos lidos e tratados ou justificados.
- [ ] Todo tópico do material tem: leitura (tabela de cobertura 100%) e pelo menos uma questão; vídeo bom ou lacuna declarada após 2 rodadas.
- [ ] Todo vídeo avaliado está em um bloco ou numa ficha com veredito e motivo; nenhuma transcrição "órfã".
- [ ] Todo `mm:ss` de `covers`, `clips` e `verdict` existe na transcrição e na duração real.
- [ ] Códigos executados; gabaritos conferidos.
- [ ] Meta de tempo atendida; opcionais marcados.
- [ ] Auditoria de `07` feita e registrada no brief.
- [ ] `brief.md` atualizado com decisões, pendências e totais.

## O que entregar ao final (relatório curto à pessoa)

Em português, sem despejar conteúdo: (1) o que ficou pronto (blocos, aulas, número de vídeos/leituras/questões, tempo obrigatório total); (2) o que **não** pôde ser verificado (figuras não lidas, vídeos sem lacuna coberta, transcrição ilegível); (3) o que ela precisa decidir; (4) como abrir (`py main.py serve`, `http://localhost:8765/#/t/<slug>`). Registre o mesmo no `brief.md`.
