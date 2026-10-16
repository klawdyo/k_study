# 06 · Questões

As questões são onde o aluno aprende: depois de responder, a interface mostra a explicação de **todas** as alternativas. Exemplares: `content/aprendizagem-de-maquina/block-1/lesson-1-questions.json` (conceituais) e `code-questions.json` (código). Formato dos arquivos: `docs/modelo-de-dados.md`, seção 3.

## Quantidade e cobertura

- **13 a 20 questões por aula** (mais em aulas com muitos tópicos), do simples ao difícil. Antes de gerar, liste os tópicos do material e conte quantas questões já cobrem cada um: **todo tópico do material tem pelo menos uma questão** (cobertura 100%), e o lote fica **equilibrado** (não concentre num tema só; "o que cai na prova" é suposição até a pessoa confirmar).
- Se houver código, um conjunto à parte (`code-questions.json`) por bloco.

## Tipos

| Tipo | Uso |
| :-- | :-- |
| `single` | exatamente 1 correta (botão de rádio) |
| `multiple` | 2 ou mais corretas; só é acerto se o conjunto marcado for igual ao correto. Diga no enunciado que há mais de uma |
| Afirmações | "qual está correta?" / "quais estão corretas?" (V/F convertido) |
| Tabela | enunciado com tabela Markdown ("para estes dados, qual estratégia?") |
| Gráfico descrito | descreva o gráfico em texto/tabela, ou gere uma imagem sua em `figures/` (nunca copiada de terceiros) |
| Árvore / rede / diagrama em texto | desenhe em bloco de código ou lista indentada |
| Código com erro de lógica | trecho curto de sintaxe **correta**; o erro é de **lógica** (ordem, vazamento, alvo entre atributos, métrica inadequada, usar o dado errado). Nunca erro de sintaxe |
| Ordem das ações | "a ordem está certa?" / "qual a ordem correta?" |
| Adequação | qual técnica/ferramenta/comando serve para a situação |

Use o que a avaliação real usa (entrevista, C2 e C4). **Sem cálculo** quando a avaliação é teórica: ler valores numa tabela ou gráfico é aceitável; somar, dividir ou calcular à mão, não.

## Regras de qualidade (obrigatórias)

1. **Toda alternativa tem `explanation`**, certa ou errada, **com pelo menos 60 caracteres** e dizendo o **porquê** (não "está errada"). O validador reprova a ausência e avisa abaixo de 40 caracteres; mire em ≥ 60.
2. **`generalExplanation` ensina:** a ideia central, uma regra de bolso e, se couber, o código corrigido ou a tabela certa.
3. **Distratores plausíveis:** erros reais de raciocínio de quem está aprendendo (confundir dois conceitos, aplicar a regra no contexto errado, ordem trocada). **Nunca absurdos nem piadas.**
4. **Tamanho equilibrado das alternativas.** A correta **não pode ser sistematicamente a mais longa**. O validador avisa quando passa de 70% das `single` com a correta mais longa. Escreva distratores tão detalhados quanto a correta.
5. **Nunca cite alternativa por letra** nos textos ("a alternativa B está errada porque…", "como na letra c"): as posições são embaralhadas depois por script. Refira-se ao conteúdo ("essa opção…", "a que diz X").
6. **Posição da correta equilibrada** entre A e D. O validador avisa quando passa de 60% numa mesma letra (com ≥ 6 `single`). No fim, rode o **embaralhamento determinístico** (abaixo).
7. **Enunciado explica o cenário:** antes de pedir a resposta, diga o que o gráfico/tabela/código mostra ("o que você está vendo / o que o código faz"). O leitor não é da área. Nomeie cada função/comando na primeira vez.
8. **Sem LaTeX**; Unicode. Imagens em `prompt`/`promptFile` existem em `figures/`.
9. **Enunciado longo** (código, tabela grande, imagem): use `promptFile` (um `.md` ao lado).
10. **Gabaritos conferidos:** refaça contas, rode o código (inclusive o "corrigido"), confira o gabarito com a leitura. **Gabarito errado é pior que ausência de questão.** Questão "de cenário nosso" (dados inventados) é legítima: avise no enunciado que é ilustrativa.
11. **Alinhe com o material:** não pergunte o que nem o material nem a leitura ensinam; se a leitura trouxer divergência material × literatura, a questão indica qual versão vale na avaliação.
12. **Ids de questão (`q01`…) nunca mudam.**

## Embaralhamento determinístico das posições

Ao final da trilha (ou do bloco), rode um script seu (guarde-o fora de `content/`, ou em `tools/` se a pessoa quiser) que, para cada questão `single` e `multiple`, reordena `options` com semente fixa derivada de `id do arquivo + id da questão` e **reatribui os ids** `a, b, c, d…` na nova ordem, de modo a equilibrar a posição da correta. Regras:

- **Nunca embaralhe questões que algum aluno já respondeu.** O progresso guarda `chosen: ["b"]`: mudar o significado da letra falsifica as respostas. Confira o banco (somente leitura) ou, na dúvida, não embaralhe um conjunto publicado. Só embaralhe conjuntos novos, antes de publicar.
- Rode `py main.py validate <slug>` depois e confira que a distribuição ficou equilibrada.

## Banco de erros lógicos comuns (para questões de código; adapte ao assunto)

O formato é "o que está errado, por que importa". Exemplos de ciência de dados, como inspiração do estilo; para outros assuntos crie o equivalente (ordem de comandos, escopo, unidade, estado compartilhado, ordem de configuração):

- treinar e avaliar no mesmo conjunto (métrica otimista);
- `fit_transform` no teste (vazamento);
- imputar/normalizar com a base inteira antes de dividir;
- balancear antes de dividir ou balancear o teste;
- escolher hiperparâmetro olhando o teste;
- usar acurácia em base desbalanceada;
- codificar variável nominal como inteiros (ordem inexistente);
- incluir o alvo ou um identificador entre os atributos;
- validação cruzada com pré-processamento fora do pipeline;
- embaralhar série temporal;
- ler linhas × colunas da matriz de confusão trocadas;
- calcular a métrica da classe errada.

Em redes, protocolos, finanças etc., o "banco" é da mesma natureza: erros de **ordem**, de **escopo** e de **pressuposto**, plausíveis para quem aprende.

## Exemplo mínimo (uma `single`)

Veja `09-templates.md` para um esqueleto de cada tipo.

## Checklist por conjunto

- [ ] 13–20 questões; todo tópico coberto; mistura de tipos conforme a avaliação.
- [ ] Toda alternativa explicada (≥ 60 caracteres, com o porquê); `generalExplanation` em todas.
- [ ] Nenhuma citação por letra; tamanhos equilibrados; posições equilibradas (script rodado, se aplicável).
- [ ] Gabaritos conferidos; códigos executados.
- [ ] Sem cálculo (se a avaliação não tem); sem LaTeX; imagens existem.
- [ ] `py main.py validate` sem erros e sem avisos de posição/tamanho.
