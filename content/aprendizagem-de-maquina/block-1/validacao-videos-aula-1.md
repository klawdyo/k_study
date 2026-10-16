# Validação dos vídeos pela transcrição — Aula 1 (Introdução ao Aprendizado de Máquina)

Método: li a transcrição inteira de cada um dos 6 vídeos (reconhecimento de fala local, Whisper "small", com erros de grafia) e comparei com os 82 slides de `Aulas/Aula 1 - Introdução AM Mestrado` (texto em `estudo/_fontes_extraidas/`). Os tempos `mm:ss` têm margem de poucos segundos. Erros de reconhecimento que aparecem: "Turin" = Turing; "cem mesas" = provavelmente "contra si mesmo" (conhecimento externo: o programa de xadrez jogou contra ele mesmo); "cura�a/acurácia" = acurácia; "castificar" = classificar. Quando aponto um erro do vídeo que depende de conhecimento meu (fora do vídeo e dos slides), isso está marcado como "(conhecimento externo)". Os slides 3–9, 12, 15, 22, 35 e outros são só figuras (`[IMAGEM]`): não dá para saber o que mostram pelo texto, então não afirmo que os vídeos os cobrem.

Legenda da matriz: **B** = cobre bem · **P** = cobre parcialmente · **–** = não cobre · **X** = cobre de forma que diverge do slide ou está errado.

## 1. Matriz tópicos dos slides × vídeos

| Tópico (slides) | J6ct Dimmy (história) | qDmo Didática (O que é ML) | N2TT Didática (treino/teste) | JDDq Didática (sup. × não sup.) | rDIo Didática (classif. × regr.) | 6Uu6 Didática (etapas) |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: |
| História da IA, invernos, Turing e o Jogo da Imitação (2, 10–11) | B | – | – | – | – | – |
| IA inclui AM, AM não define IA (10, 13) | P | P | – | – | – | – |
| Definição de AM: aprender a partir de dados/amostras (13) | – | P | P | – | – | – |
| Algoritmo convencional × AM (14) | – | B | – | – | – | – |
| Hardware, big data, poder de processamento (16–17) | P | P | – | – | – | – |
| Raciocínio indutivo × dedutivo (18–19) | – | P | – | – | – | – |
| Exemplos e usos reais (20–23) | P | P | P | P | P | – |
| Treino e teste, acurácia (24–27) | – | – | B | – | – | P |
| Base de dados, atributos preditivos e alvo (28–29) | – | – | P | P | P | – |
| Supervisionado × não supervisionado (30–31) | – | – | P | B | – | – |
| Tarefas preditivas × descritivas (32–34) | – | – | – | P | – | – |
| Classificação × regressão, alvo discreto × contínuo (36, 39, 51) | – | – | – | P | B | – |
| Binária × multiclasse (44) | – | – | – | – | B | – |
| Agrupamento (57–61) | – | – | – | P (sem o nome) | – | – |
| Associação (63–64) | – | – | – | – | – | – |
| Semissupervisionado, ativo, reforço (67–74) | – | P (sem o nome) | – | – | – | – |
| Processo de AM em 7 etapas (75–81) | – | – | – | – | – | X |
| Treino × teste dentro do processo (78) | – | – | – | – | – | X |
| Hiperparâmetros (81) | – | – | – | – | – | P (chama de "parâmetros") |
| Generalização da hipótese (82) | – | – | P | – | – | – |
| Classificadores estatísticos × estruturais (45–46) | – | – | – | – | – | – |
| Equação do aprendizado supervisionado (53) | – | – | – | – | – | – |

Leitura rápida: os cinco vídeos da Didática Tech formam uma série curta e em ordem (o próprio autor remete de um para o outro) e cobrem bem os conceitos centrais dos slides 13–14, 24–27, 30–31, 36 e 75–81. Nenhum vídeo cobre associação, semissupervisionado/ativo/reforço (com nome), classificadores dos slides 45–46 nem a equação do slide 53. O vídeo de história só serve para os slides 2 e 10–11.

## 2. Fichas por vídeo

### J6ctBcC8wyI — Doutor Dimmy — A evolução da IA: de Alan Turing ao Deep Learning (10:14) — item opcional

- **Cobre:**
  - 00:00–01:44 IA como ramo da computação que quer replicar capacidades humanas (aprender, raciocinar, perceber, planejar, reconhecer padrões); o termo "inteligência artificial" foi cunhado em 1956.
  - 01:44–04:49 "verões e invernos" da IA: Amanhecer da IA (fim dos anos 50 a 70, primeiros programas: álgebra, damas); primeiro inverno (meados dos anos 70, corte de financiamento); anos 80 com sistemas baseados em conhecimento e retropropagação (backpropagation); segundo inverno (fim dos anos 80 e início dos 90); mais um inverno no fim dos anos 90.
  - 04:49–05:17 era do aprendizado profundo (anos 2000 até hoje) puxada por internet, grandes conjuntos de dados e poder computacional (alinha com slide 17, só dois dos três pilares).
  - 05:17–06:00 teste de Turing, 1950: se a máquina engana um humano a ponto de ele achar que conversa com outro humano, pode ser considerada inteligente (slides 10–11).
  - 06:00–07:07 usos: diagnóstico médico, carros autônomos, recomendação de vídeos e músicas, assistentes como Siri e Alexa (slides 2, 11, 23).
  - 07:07–08:05 ramos da IA: aprendizado de máquina, redes neurais, processamento de linguagem natural, robótica, visão computacional (slide 10: IA inclui AM).
- **Não cobre:** o artigo "Computing Machinery and Intelligence" pelo nome; o Jogo da Imitação com três jogadores (A computador, B humano, C juiz) do slide 11; o que é AM e como difere de um algoritmo convencional; GPUs e arquiteturas (CNN, Transformers) do slide 17; qualquer conceito técnico dos demais slides. O título promete "até o Deep Learning" mas o vídeo só passa por ele em uma frase.
- **Divergências com o slide:**
  - Turing: o vídeo descreve o teste de forma simplificada (máquina × humano em conversa); o slide 11 detalha três jogadores e diz que o computador vence se o juiz C não conseguir distinguir de forma coerente. Compatível, só menos detalhado.
  - 08:25–08:38 mistura "IA geral" com "singularidade" (conhecimento externo: são ideias diferentes; não está nos slides). Ignorar.
  - A cronologia dos invernos (inclusive o "inverno no fim dos anos 90", 04:23) e a frase de que a retropropagação "renovou o interesse na aprendizagem profunda" (03:44) são simplificadas (conhecimento externo; os autores divergem nas datas). Nada disso está nos slides: não decorar datas.
  - 08:41–09:19 discute ética e impactos sociais: extra, não está nos slides.
- **Nível e foco:** iniciante, só conceito (nenhum código). Narração em tom de apresentação, quase sem exemplos técnicos.
- **Idioma/qualidade:** português do Brasil, fala nítida e pausada; transcrição com erros de grafia ("Turin"), mas compreensível. Qualidade média: ótimo para ter a linha do tempo, pouco profundo.
- **Trechos recomendados:** 01:30–06:00 (linha do tempo, eras e Turing) e 06:29–07:30 (usos e AM como ramo da IA), 5:31.
- **Veredito: `aprovar só os trechos 01:30–06:00 e 06:29–07:30`** (item opcional: serve só para contexto histórico dos slides 2 e 10–11, sem conteúdo técnico cobrável).

### qDmojpkd8rE — Didática Tech — O que é Machine Learning? (7:45)

- **Cobre:**
  - 00:00–00:21 definição: máquinas que adquirem conhecimento e executam bem uma ação com base em aprendizado, "não somente com base em entradas de instruções".
  - 00:21–01:21 analogia da bicicleta: ninguém aprende lendo uma lista de instruções, aprende por tentativa e erro (raciocínio que o slide 18 chama de "é assim que as crianças aprendem", mas aqui sem falar de exemplos/indução).
  - 01:21–02:32 mesma ideia com um robô que pega um abajur: em vez de programar cada passo, ele aprende a fazer.
  - 02:32–03:33 xadrez em 1997: o computador venceu o melhor humano usando uma lista de instruções com todo o conhecimento de xadrez colocado no código mais muito poder de processamento. É o exemplo de "algoritmo convencional" do slide 14.
  - 04:13–05:56 xadrez em 2017: programa da DeepMind aprende só com as regras, jogando milhões de partidas, e supera o melhor software baseado em instruções; faz jogadas que humanos consideram erradas (06:26–06:50).
- **Não cobre:** de onde vem o aprendizado (dados/amostras, rótulos): a palavra "dados" quase não aparece; indução; atributos; tipos de aprendizado; hardware (só cita processamento no xadrez); nenhum conceito dos slides 18–82 por nome.
- **Divergências com o slide:**
  - O vídeo define AM por **tentativa e erro com acertos e erros** (00:55–01:21, 02:14–02:32, 04:50–05:00). O slide 14 define por **descoberta das regras pela máquina a partir de dados**, com "meios de avaliar o desempenho" e "modo de buscar novas hipóteses", e o slide 13 diz "a partir de amostras do domínio". A descrição do vídeo se parece mais com o **aprendizado por reforço** (slide 73: recompensar ação positiva, punir negativa, agente aprende sozinho), que o vídeo não nomeia. O vídeo seguinte (N2TT) completa dizendo que o aprendizado vem de dados.
  - Contraste certo com o slide 14: o xadrez de 1997 é o "algoritmo convencional" (regras escritas por humanos), o de 2017 é "aprendizado de máquina" (regras descobertas).
  - 05:00 e 04:30 a legenda diz "jogando contra cem mesas": provavelmente "contra si mesmo" (conhecimento externo); não use a frase.
  - 03:39 "no ano de 2019" para o software de xadrez moderno, e depois "em 2017" para a DeepMind: a ordem dos anos na fala é confusa; não decorar datas.
- **Nível e foco:** iniciante absoluto, só conceito e analogias, sem código nem fórmulas.
- **Idioma/qualidade:** português do Brasil, fala clara e informal; um pouco repetitivo (00:55–01:21) e com vício de linguagem "né". Qualidade boa como porta de entrada, ótima para o contraste algoritmo convencional × AM.
- **Trechos recomendados:** 00:00–03:33 e 04:13–05:56 (5:16). O restante (03:33–04:13 e 06:08–07:33) é digressão sobre xadrez moderno e fechamento.
- **Veredito: `aprovar só os trechos 00:00–03:33 e 04:13–05:56`.** Assistir sabendo que a definição por "tentativa e erro" é uma simplificação: a forma dos slides é "descobre regras a partir de dados".

### N2TT2Q83abc — Didática Tech — Dados de treino e teste (5:59)

- **Cobre:**
  - 00:30–01:34 o aprendizado vem dos dados; exemplo de reconhecer cachorros com milhares de fotos rotuladas ("isso é um cachorro, isso não é"): o mesmo exemplo dos slides 25–26.
  - 01:34–02:23 imagem nova que o modelo nunca viu = dado de teste; mede-se o percentual de acerto (acurácia), por exemplo 95 em 100.
  - 02:23–03:00 por que o teste não pode usar dados já vistos: seria muito mais fácil acertar, então a medida não vale.
  - 03:10–04:30 cenário de detecção de doença: com dados limitados, separa-se uma parte para treino e outra para teste; não se treina com tudo e "conta com a sorte".
  - 04:30–05:07 critério de aceitação hipotético (98% de acerto no teste para usar o algoritmo).
- **Não cobre:** proporção da divisão (por exemplo 70/30); validação cruzada; sobreajuste (overfitting) pelo nome; os termos atributo preditivo e atributo alvo (diz só "rotuladas"); generalização por nome; como separar (aleatório, estratificado).
- **Divergências com o slide:**
  - Nenhuma factual. Usa o mesmo exemplo e a mesma medida (acurácia) dos slides 25–26; a ideia de "modelo especializado nos dados de treino" (slide 78, 82) está implícita em 02:23–03:00, sem o nome.
  - 04:08–04:18 e 05:24–05:36 a fala está confusa ("outros dados que vão ser usados somente na prática"); é problema de legenda e de fala, não de conceito.
- **Nível e foco:** iniciante, só conceito com exemplos; sem código. Pressupõe ter visto o vídeo "O que é Machine Learning" (ele diz isso em 00:11).
- **Idioma/qualidade:** português do Brasil, claro e direto; repetitivo, o que ajuda quem está começando. Qualidade boa.
- **Trecho recomendado:** vídeo inteiro (5:59); o início (00:00–00:30) e o fim (05:07–05:59) são só abertura e despedida.
- **Veredito: `aprovar`.**

### JDDqP6IZ4NQ — Didática Tech — Aprendizado supervisionado × não supervisionado (5:36)

- **Cobre:**
  - 00:10–00:58 supervisionado = rótulos já estabelecidos; exemplo de imagens rotuladas (celular, geladeira, flor).
  - 01:42–01:55 origem do nome: "como se tivesse um professor dizendo isso está certo, o valor é esse" (o "supervisor externo" do slide 34).
  - 00:58–01:42 curva ajustada a dados com a variável de resposta já conhecida é supervisionado (exemplo de uma aula anterior sobre overfitting e underfitting, que não está nesta lista).
  - 01:55–03:55 não supervisionado = sem informação prévia; exemplo de dados de plantas (tamanho de caule, flores, folhas) que o algoritmo separa em N grupos, descobrindo sozinho as características em comum.
  - 03:55–04:27 segundo exemplo: clientes de uma empresa separados em perfis de consumo (alinha com o slide 60: segmentação de clientes).
  - 04:27–05:07 resumo: supervisionado quer prever um novo valor com base em valores já informados; não supervisionado quer descobrir sozinho as relações, sem "certo ou errado".
- **Não cobre:** os nomes classificação, regressão, agrupamento (clustering) e associação; "atributo alvo" (diz "rótulos" e "variável de resposta"); tarefas preditivas × descritivas; a definição formal do slide 30 (tem atributo alvo ou não).
- **Divergências com o slide:**
  - Usa "classificar" para o caso não supervisionado (02:20 "classificar essas plantas", 03:17): no slide, **classificação é supervisionada** (slide 39), e o caso sem rótulo é **agrupamento** (slide 57), que também diz que os grupos são rotulados depois pelo cientista de dados. O sentido do vídeo é "separar em grupos", não classificação. Cuidado na prova.
  - Inconsistência de fala: "cinco categorias" (03:01, 03:11) e depois "quatro partes" (03:15); é só lapso.
  - 00:58–01:42 depende de uma aula sobre overfitting e underfitting que não faz parte desta seleção; o exemplo da curva fica solto. Pode pular 00:58–01:42 sem perder o fio.
- **Nível e foco:** iniciante, conceito com exemplos, sem código.
- **Idioma/qualidade:** português do Brasil, claro; repete bastante, mas é objetivo. Qualidade boa: é a melhor explicação intuitiva de supervisionado × não supervisionado do conjunto.
- **Trecho recomendado:** 00:10–05:07 (4:57).
- **Veredito: `aprovar`.** Assistir já avisado de que "classificar plantas" aqui significa agrupar.

### rDIocV_r9Xk — Didática Tech — Problemas de classificação e de regressão (5:14)

- **Cobre:**
  - 00:23–01:14 regressão = prever um valor numérico específico (preço de produto, tamanho, idade).
  - 01:14–02:22 classificação = descobrir a classe; exemplos: tem ou não tem doença, e-mail é ou não é spam; também pode ser multiclasse (A, B, C, D; perfil de cliente; tipo de planta; raça de cachorro) (slide 44).
  - 02:22–04:01 ponto-chave: classe pode ser escrita como número (1 = tem doença, 0 = não tem; classe 1, 2, 3, 4), mas é só um rótulo: "estar na classe 4 não significa ser quatro vezes a classe 1". O que decide é o **significado** do número, não ele ser número.
  - 04:01–04:55 primeiro passo do profissional: reconhecer se o problema é de classificação ou de regressão (liga ao "reconhecimento do problema" do vídeo de etapas).
- **Não cobre:** que ambos são aprendizado supervisionado/tarefas preditivas (slide 36); os termos "atributo alvo discreto × contínuo" (slide 36); "predição ou estimação" como sinônimos de regressão (slide 51); equação de regressão; classificadores estatísticos × estruturais; fases de aprendizagem e reconhecimento (slide 39).
- **Divergências com o slide:**
  - Define pela natureza do **valor numérico × categoria**; o slide 36 define por alvo **discreto** (conjunto finito ou enumerável) × **contínuo** (intervalo de reais). Equivalentes para quem entende, mas com vocabulário diferente: na prova use os termos do slide.
  - 00:48–00:52 e 00:55 "prever um preço futuro": regressão não precisa ser sobre o futuro (conhecimento externo); é só prever um número.
  - O vídeo fala em **multiclasse** (01:44); o slide 44 escreve "binárias ou multilabel" e depois "multiclasses". Em geral multilabel e multiclasse são coisas diferentes (conhecimento externo): trate "multilabel" do slide como sinônimo de multiclasse e use o termo multiclasse. O slide também escreve SIM(01) e NÃO(00); o vídeo usa 1 e 0 (02:45).
- **Nível e foco:** iniciante, só conceito; sem código.
- **Idioma/qualidade:** português do Brasil, claro; repete a ideia várias vezes de propósito. Qualidade boa; o trecho do número-como-rótulo vale mais do que os slides dizem.
- **Trecho recomendado:** vídeo inteiro (5:14); só o fim (04:55–05:14) é despedida.
- **Veredito: `aprovar`.**

### 6Uu6zo0xoig — Didática Tech — Etapas do Machine Learning, resumo básico (12:03)

- **Cobre:** o vídeo apresenta um "mapa" com **etapas** (ele nunca diz um número):
  - 00:49–01:33 **1. conhecimento dos dados**: entender o problema, o que a tabela e cada variável significam e o que se quer prever.
  - 01:33–03:55 **2. pré-processamento e seleção de variáveis**: adequar/formatar (texto para número, caracteres especiais), normalizar, tratar dados faltantes (eliminar a amostra ou substituir), tratar outliers (remover ou manter), selecionar variáveis relevantes e excluir colineares, reduzir a dimensionalidade (agrupar variáveis em uma). Liga aos slides 76–77.
  - 03:55–05:57 **3. Machine Learning propriamente dito**: escolher e aplicar o modelo; diz que em programação é a parte mais fácil porque os algoritmos já estão prontos (a observação de 04:57–05:13 aparece repetida na transcrição por erro de reconhecimento).
  - 06:01–06:33 **4. medir os resultados**: separar em treino e teste, validação cruzada, reamostragem, escolher a métrica (slides 78 e 81).
  - 06:33–09:20 **5. aperfeiçoar**: testar outro modelo, mudar os parâmetros do mesmo modelo (rede neural: camadas, neurônios por camada, taxa de aprendizado, quantidade de amostras por lote) ou voltar ao pré-processamento (trocar a remoção de faltantes por média ou mediana, tratar outliers de outro jeito). Retorno decrescente: chega um ponto em que não vale mais o esforço (08:29–09:20).
  - 09:20–09:43 critério de parada: "esse é o modelo final que eu vou utilizar".
- **Não cobre:** a etapa de **coleta de dados** como etapa própria nem quantidade × qualidade dos dados (slide 76); balanceamento dos dados (slide 77); a etapa de **aplicação** (uso do modelo já treinado para prever, slide 81); a divisão treino/teste dentro da preparação (slide 78); a equação b e w e como o treino muda os parâmetros (slide 80); generalização (slide 82); o nome "hiperparâmetro".
- **Divergências com o slide (importantes):**
  - **Número e nomes das etapas**: o slide 75 tem **sete** (coleta de dados, preparação dos dados, seleção do modelo, treinamento, avaliação, ajuste de parâmetros, aplicação). O vídeo tem **cinco blocos**: conhecimento dos dados, pré-processamento/seleção de variáveis, aplicação do modelo, medição dos resultados, aperfeiçoamento. Mapa: conhecimento dos dados ≈ coleta (parcial); pré-processamento ≈ preparação; aplicação do modelo = seleção do modelo + treinamento (juntos); medir resultados = avaliação; aperfeiçoar = ajuste de parâmetros (e volta atrás); a **aplicação** final do slide não é uma etapa.
  - **Onde entra a divisão treino/teste**: no vídeo, só depois do modelo aplicado (06:09, bloco de medição). No slide 78, a divisão está dentro da **preparação**, antes de selecionar o modelo. Na prova, seguir a ordem do slide.
  - **"Parâmetros" × "hiperparâmetros"**: o vídeo chama de "parâmetros do modelo" (06:49–07:17) as camadas, neurônios e taxa de aprendizado. Pelo slide 80, **parâmetros** são o peso w e o viés b (o treino muda isso); pelo slide 81, **hiperparâmetros** são o que controla o aprendizado (repetições sobre os dados, taxa de aprendizado). Usar o termo do slide.
  - **Pré-processar antes de separar treino e teste**: o vídeo põe todo o pré-processamento (normalizar, imputar, tratar outliers) antes de separar os dados. Fazer isso com o conjunto inteiro pode vazar informação do teste para o treino (conhecimento externo; ver a validação da Aula 3: "ajustar só no treino"). Slide 78 divide cedo. Cuidado.
  - 09:20–09:43 diz que "o trabalho está pronto" no critério de parada, sem passar para uso do modelo.
- **Nível e foco:** iniciante; só visão geral conceitual (desenha o mapa em slides), sem código.
- **Idioma/qualidade:** português do Brasil, fala clara; há enchimento no início (00:00–00:33) e um final longo (09:43–12:03) que repete a dica de salvar o mapa e divulga o curso. Qualidade boa como visão geral, mas **não** substitui o slide 75 (números diferentes).
- **Trecho recomendado:** 00:33–09:43 (9:10).
- **Veredito: `aprovar só os trechos 00:33–09:43`**, com o aviso de que o vídeo tem cinco blocos e o slide tem sete etapas.

## 3. Sequência recomendada para assistir (ordem dos slides)

Tempo estimado do conjunto: **cerca de 36:46** (`2206 s`).

| # | Slides | Vídeo | Trechos (início–fim) | Tempo | Por quê / o que ignorar |
| :-: | :-- | :-- | :-- | :-: | :-- |
| 1 (opcional) | 2, 10–11, 17 | J6ctBcC8wyI | 01:30–06:00 · 06:29–07:30 | 5:31 | Linha do tempo da IA, Turing, usos; sem conteúdo técnico. Ignorar "IA geral = singularidade" e as datas exatas. |
| 2 | 13–14, 18 | qDmojpkd8rE | 00:00–03:33 · 04:13–05:56 | 5:16 | Algoritmo convencional (xadrez 1997) × aprendizado (xadrez 2017). Lembrar que a definição dos slides é "regras descobertas a partir de dados". |
| 3 | 24–27, 78, 82 | N2TT2Q83abc | 00:00–05:59 (inteiro) | 5:59 | Dados de treino e de teste, acurácia, por que testar com dados nunca vistos. |
| 4 | 30–34 | JDDqP6IZ4NQ | 00:00–05:36 (inteiro) | 5:36 | Supervisionado × não supervisionado. Atenção: "classificar" aqui quer dizer agrupar. |
| 5 | 36, 44, 51 | rDIocV_r9Xk | 00:00–05:14 (inteiro) | 5:14 | Classificação × regressão; classe numérica é só rótulo. Usar os termos discreto/contínuo do slide. |
| 6 | 75–81 | 6Uu6zo0xoig | 00:33–09:43 | 9:10 | Visão geral do processo. O vídeo tem cinco blocos, o slide tem sete etapas; "parâmetros" do vídeo = hiperparâmetros do slide. |
| | | **Total** | | **36:46** | |

Versão mínima, sem o item opcional: **31:15** (itens 2 a 6). Nenhum vídeo foi descartado.

## 4. Lacunas: tópicos que nenhum vídeo cobre bem (o material escrito precisa cobrir)

1. **Slides figura-apenas (3–9, 12, 15, 22, 35, 47–49, 54–55, 59, 65–66, 71, 74):** os vídeos não mostram as figuras da professora; o texto escrito deve descrever o que cada uma representa (a linha do tempo, os esquemas das tarefas, os gráficos de classificação, regressão e agrupamento).
2. **Slides 16–17 (hardware e os "três pilares": big data, GPUs, arquiteturas CNN e Transformers):** o vídeo de história só cita dados e poder computacional; GPUs e arquiteturas não aparecem.
3. **Raciocínio indutivo × dedutivo (18–19):** nenhum vídeo define; o exemplo da criança aprende por exemplos só aparece como analogia da bicicleta (tentativa e erro), que é outra coisa. Falta o cuidado com a escolha dos exemplos.
4. **Exemplos dos slides 20–22 (cartão de crédito e diagnóstico médico com base de histórico) e a lista de usos do slide 23:** só aparecem usos parecidos de passagem (doença, spam, recomendação).
5. **Base de dados, atributos e alvo (28–29):** sinônimos (padrão, registro, exemplo; atributo, campo, variável), vetor de características, atributos preditivos × atributo alvo. Os vídeos só dizem "rotuladas".
6. **Preditivas × descritivas (32–35)** e a regra "atributo alvo discreto/contínuo/ausente decide a tarefa": só aparece implícita (JDDq).
7. **Classificação em detalhe (39–49):** fases de aprendizagem e reconhecimento, indutor, binária × multiclasse (o slide escreve "multilabel"), classificadores estatísticos × estruturais (45–46). Só a parte binária/multiclasse está no rDIo.
8. **Regressão formal (51–55):** equação, aprendizado supervisionado como argmax da hipótese (53). Nenhum vídeo.
9. **Agrupamento (57–61):** funcionalidades (extração de padrões, outliers, feature engineering, filtros automáticos), o aviso de que um agrupamento pode não ter significado e o efeito do número de clusters. JDDq só mostra a ideia, sem o nome.
10. **Associação (62–66):** nenhum vídeo (padrões de itens comprados juntos).
11. **Semissupervisionado, ativo e por reforço (67–74):** nenhum vídeo com o nome; o xadrez do qDmo lembra reforço sem dizer. O texto escrito deve definir os três e diferenciá-los (parte rotulada/parte não; escolher quais rotular; recompensar e punir).
12. **Processo de AM em sete etapas (75–81) com os detalhes dos slides:** coleta com quantidade e qualidade, balanceamento, separação treino/teste dentro da preparação, equação do treino (peso w e viés b), avaliação, hiperparâmetros (repetições sobre os dados e taxa de aprendizado), aplicação. O vídeo 6Uu6 só cobre a ideia geral com outra estrutura.
13. **Generalização da hipótese (82):** nenhum vídeo define "capacidade de generalização" nem o contraste com um modelo especialista nos dados de treino.
14. **Mapeamento etapas dos vídeos × etapas dos slides:** o texto escrito deve trazer a tabela de correspondência (cinco blocos do vídeo × sete etapas do slide) para evitar confusão.
