# 01 · Entrevista: o que perguntar antes de criar qualquer trilha

Nada é criado antes da entrevista. Ela existe porque trilhas ruins nasceram de suposições: conteúdo raso para quem começa do zero, vídeo escolhido pelo título, questões com cálculo quando a prova não tinha, foco errado em um tema que "não era o foco".

## Regras da entrevista

1. **Poucas rodadas.** Agrupe as perguntas em **3 rodadas** (A, B, C abaixo), cada uma numa única mensagem, com a opção recomendada marcada. Não faça uma pergunta por mensagem.
2. **Dê padrão.** Toda pergunta traz uma sugestão ("padrão recomendado"); a pessoa pode responder só "ok" ou corrigir o que quiser.
3. **Pergunte só o que muda o resultado.** Se a pessoa já disse algo (no pedido, em arquivos, em `materials/`), não pergunte de novo; confirme no resumo.
4. **Olhe o material antes da rodada B.** Se a pessoa entregou arquivos, leia-os (ou extraia o texto) e proponha a divisão com base neles.
5. **Mostre o resumo das decisões** (tabela curta) e **só comece depois do "pode começar"**.
6. **Registre** tudo em `content/<slug>/brief.md` (modelo em `09-templates.md`). Se a conversa for retomada em outra sessão, leia o `brief.md` primeiro e não repita perguntas.
7. Depois da aprovação, **não pergunte "posso continuar?"**: decida, registre e siga. Volte à pessoa só se bloqueado ou se algo mudar o escopo.

## Rodada A · assunto, objetivo, prazo, perfil

| # | Pergunta | Por que perguntar | Opções (padrão em negrito) | O que você faz com a resposta |
| :-: | :-- | :-- | :-- | :-- |
| A1 | **Qual o assunto e o objetivo?** (passar numa prova, aprender por hobby, usar no trabalho, ensinar alguém) | o objetivo define o que é "pronto" e o que fica de fora | prova · trabalho · hobby · **(sem padrão: pergunte)** | define a profundidade, o peso de questões e de prática; vira o título e a `description` da trilha |
| A2 | **Qual o prazo e quanto tempo por dia?** | dimensiona o tempo obrigatório por aula e quanto vai para opcional | data + horas/dia; **sem prazo: 1 h/dia** | calcula a meta de tempo total e por aula (ver `03`); define o que vira `optional` |
| A3 | **Qual o seu nível de partida?** O que você **já sabe** e o que **não sabe** (seja franco)? Qual sua profissão ou área? | calibra a explicação e escolhe as analogias; evita escrever raso ou condescendente | **iniciante total no assunto, com conhecimento sólido na própria área** | perfil do leitor (vai em todo prompt de subagente); escolhe a área das analogias; o nível filtra vídeos (didático para ESSE nível) |
| A4 | **Em que idioma será a trilha?** | decide idioma das leituras, questões e dos vídeos | **português do Brasil** | `language` em `trail.json`; busca de vídeo (ver B3 e B4) |
| A5 | **Já estudou parte? O que, e como foi?** | não repetir; talvez marcar itens como opcionais ou pular | nada · algo específico | registra no brief "já estudado"; o que ele já domina vira revisão curta; nunca apague o que ele já usou |

## Rodada B · material, divisão, vídeos

| # | Pergunta | Por que perguntar | Opções | O que você faz |
| :-: | :-- | :-- | :-- | :-- |
| B1 | **Você tem material?** (slides, PDFs, anotações, ementa, links). Pode pôr em `content/<slug>/materials/`? | o material é a fonte de escopo e de ordem; sem ele, escopo vem de referências públicas citadas | **sim, colo os arquivos** · não tenho (você propõe o escopo a partir de fontes que citarei) | extrai o texto (cache em `materials/_text/`); o material define tópicos, ordem e numeração de slides/páginas usada em `goals` e `slides`. **Use sem copiar literalmente** (ver `05`); material com direitos de terceiros não é distribuído (`materials/` pode ir para o `.gitignore`: pergunte) |
| B2 | **Como dividir?** (você **sugere**; a pessoa aprova) | a divisão em blocos e aulas organiza o estudo e a paralelização | blocos de 2 a 4 aulas, uma aula = um tema do material; **ordem de pré-requisitos** (base antes do avançado; nunca uma introdução depois do tópico difícil) | apresente uma tabela: bloco → aulas → tópicos do material → tempo estimado. Ajuste ao pedido. Ela aprova antes de qualquer geração |
| B3 | **Vídeos: quantos por tópico, idioma, duração?** | vídeo é o que mais custa e o que mais erra | **1 bom vídeo por tópico (pode ser trecho de um vídeo maior)** · português preferido · inglês só se claramente superior e avisado · duração: em geral 5 a 35 min; mais longo só com trechos claros · só vídeos **didáticos para o nível dela** | define as regras da busca em `04`; a meta de tempo de vídeo por aula |
| B4 | **Aceita vídeo em inglês?** | muda o universo de busca | **não** (só se for claramente superior, avisado em `note`) · sim | idem; transcrição com `--language auto` |
| B5 | **Pode eu baixar o áudio dos vídeos para transcrever localmente?** (o `ktr` baixa **só o áudio**, um por vez, fora da pasta do projeto) | é ação que o agente não faz sem autorização; a transcrição é o que permite conferir o vídeo | **sim, para estudo pessoal** · não (então, vídeos só pela legenda do YouTube, `ktr captions`, de menor qualidade, e avisamos no `review`) | registre a autorização literal da pessoa no brief; sem ela, não baixe |

## Rodada C · leituras, questões, prova, tom

| # | Pergunta | Por que perguntar | Opções | O que você faz |
| :-: | :-- | :-- | :-- | :-- |
| C1 | **Leituras: tamanho e estilo?** De qual área vêm as analogias? | a leitura é o coração; o estilo dita o texto | **explicar do zero, 350 a 700 linhas por aula, analogias da profissão dela, exemplo pequeno, "Se perguntarem na prova"** · mais curta/resumo (avise: abaixo de 250 linhas o validador avisa) | prompt do subagente de leitura (ver `05`) |
| C2 | **Questões: quantas por aula e de que tipos?** | tipos de questão precisam espelhar a avaliação real | **13 a 20 por aula**, do simples ao difícil · tipos: única, múltipla, tabela, gráfico descrito, código com erro de lógica, ordem das ações, afirmações V/F · **sem cálculo** (se a avaliação tem cálculo, diga) | define a mistura de tipos; `06` |
| C3 | **Nível de dificuldade e explicações?** | evita questões triviais ou impossíveis | **cada alternativa explicada (certa e errada)**; dificuldade crescente; distratores plausíveis | padrão fixo do projeto; só muda com pedido explícito |
| C4 | **Há uma avaliação real? Qual formato e o que o professor/empresa cobra?** (peça exemplos, provas antigas, ementa) | as questões devem treinar o formato real; "tema-foco" pode ser armadilha | prova teórica/prática · certificação · entrevista · nenhuma | espelha formato e tipos; **não** super-represente um tema por achar que cai mais, a menos que a pessoa confirme; registre o que ela disser que **não** é foco |
| C5 | **Tom e preferências?** (formal/informal, humor, nada de emojis, termos em inglês entre parênteses, etc.) | preferência pessoal | **informal e direto, sem emojis, termo em inglês entre parênteses na 1ª ocorrência** | vai em todos os prompts de subagente |
| C6 | **Código de exemplo?** (linguagem, ambiente, se há execução possível) | o código das leituras é **executado** por você | linguagem do material · Python como padrão se nada indicado | define quais códigos você roda para validar |

## Resumo final (mostre antes de começar)

Uma tabela com: assunto/objetivo · prazo e horas por dia · perfil · idioma · material (arquivos) · divisão aprovada (blocos × aulas) · vídeos (regras e autorização de áudio) · leituras (tamanho, analogias) · questões (quantidade, tipos, sem/com cálculo) · avaliação real · tom · já estudado · **decisões em aberto**. Pergunte "posso começar?" **uma vez**. Depois de "sim", grave `brief.md` e inicie o pipeline em `03`.

## Perguntas que NÃO se fazem

- "Posso passar para a próxima aula?" (o contrato é autônomo).
- Detalhes que a pessoa disse que não importam agora (registre como pendência no brief e siga).
- Algo que já está em `materials/` ou no pedido.

## Se a pessoa não sabe responder

Proponha o padrão, explique em uma frase o que ele significa e registre "padrão adotado" no brief. Isso evita travar a entrevista.
