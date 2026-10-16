# Validação dos vídeos pela transcrição — Aula 1, rodada 2 (lacunas da primeira rodada)

Método: li a transcrição **inteira** de cada um dos 12 candidatos (reconhecimento de fala local, Whisper "small", com erros de grafia) e comparei com os 82 slides de `Aulas/Aula 1 - Introdução AM Mestrado` (texto em `estudo/_fontes_extraidas/Aulas__Aula_1_-_Introducao_AM_Mestrado.pptx.txt`). Os tempos `mm:ss` vêm dos carimbos da transcrição e têm margem de poucos segundos. Sem internet: não conferi nada fora das transcrições e dos slides; o que depende de conhecimento meu está marcado "(conhecimento externo)". Os slides só com figura (`[IMAGEM]`: 3–9, 12, 15, 22, 35, 47–49, 54–55, 59, 65–66, 71, 74) não podem ser conferidos pelo texto; não afirmo que os vídeos os cobrem. Esta rodada complementa `validacao-videos-aula-1.md` (vídeos a1-v1 a a1-v6, já no bloco); a primeira rodada deixou sem vídeo: associação, semissupervisionado/ativo/reforço (com nome), agrupamento (nome), atributos preditivos × alvo, hiperparâmetros, generalização.

Legenda da matriz: **B** = cobre bem · **P** = cobre parcialmente · **–** = não cobre · **X** = cobre de forma que diverge do slide ou está errado.

Resultado: **10 aprovados** (8 só em trechos), **2 descartados** (Oq_kM6M_KQ0, lsPucobtdDk). Os itens aprovados estão em `proposta_aula1.json` (ids `a1-v7` a `a1-v16`, campo extra `afterSlide` para ordenar).

## 1. Matriz tópicos dos slides × vídeos

Colunas (ID abreviado): Oq_k = regras de associação (estudo de caso) · 5u8y = reforço · 3rU1 = semissupervisionado · tzeG = generalização · HDLI = hiperparâmetros · WqMn = k-means · ANIw = aprendizado ativo (inglês) · BuUj = dataset · TY45 = UNIVESP, visão geral · PkJI = UNIVESP, modelos preditivos · lsPu = treino × inferência · ZGyY = supervisionado × não supervisionado (outro canal).

| Tópico (slides) | Oq_k | 5u8y | 3rU1 | tzeG | HDLI | WqMn | ANIw | BuUj | TY45 | PkJI | lsPu | ZGyY |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| IA ⊃ AM ⊃ aprendizado profundo; definição de AM (10, 13) | – | – | – | – | – | – | – | – | B | – | – | – |
| Base de dados: amostra, atributos preditivos × alvo (28–29) | – | – | – | – | – | – | – | B | – | P | – | P |
| Treino × teste/inferência (24–27, 39) | – | – | – | P | – | – | – | – | P | – | X | – |
| Supervisionado × não supervisionado (30–31) | – | – | – | – | – | P | – | P | B | – | – | P |
| Preditivas × descritivas (32–34) | – | – | – | – | – | – | – | – | B | – | – | – |
| Alvo discreto (classificação) × contínuo (regressão) (36, 39, 51) | – | – | – | – | – | – | – | P | B | B | – | B |
| Hipótese aproxima f(x) (53) | – | – | – | – | – | – | – | – | – | P | – | – |
| Agrupamento (57–61) | – | – | – | – | – | B | – | – | P | – | – | – |
| Associação (63–64) | P | – | – | – | – | – | – | – | P | – | – | – |
| Semissupervisionado (68–70) | – | – | B | – | – | – | – | – | – | – | – | – |
| Aprendizado ativo (72) | – | – | – | – | – | – | B | – | – | – | – | – |
| Aprendizado por reforço (73) | – | B | – | – | – | – | – | – | P | – | – | – |
| Treinamento: parâmetros w e b (80) | – | – | – | – | – | – | – | – | – | P | – | – |
| Hiperparâmetros (81) | – | – | – | – | P | – | – | – | – | – | – | – |
| Generalização da hipótese (82) | – | – | – | P | – | – | – | – | – | – | – | – |
| Agrupamento semissupervisionado com restrições (69) | – | – | – | – | – | – | – | – | – | – | – | – |
| Classificadores estatísticos × estruturais (45–46) | – | – | – | – | – | – | – | – | – | – | – | – |
| Raciocínio indutivo × dedutivo (18–19) | – | – | – | – | – | – | – | – | – | – | – | – |
| Processo em sete etapas (75–79) | – | – | – | – | – | – | – | – | – | – | – | – |

Leitura rápida: TY45 é o vídeo mais amplo (visão geral que passa por quase todas as tarefas dos slides 10–73) e o único com algo sobre associação além de Oq_k. Para os três tópicos que a primeira rodada deixou totalmente sem vídeo, achei um bom para cada: semissupervisionado (3rU1), ativo (ANIw, em inglês) e reforço (5u8y). Agrupamento ganhou WqMn. Generalização e hiperparâmetros só têm cobertura parcial e imperfeita (tzeG, HDLI).

## 2. Fichas por vídeo

### TY45HIJ3RpM — UNIVESP — Aplicações em AM: introdução ao aprendizado de máquina (17:29) — aprovar só trechos

- **Cobre:**
  - 00:24–03:16 IA ⊃ aprendizado de máquina ⊃ aprendizado profundo (redes neurais profundas, muitas camadas); redes neurais são um dos algoritmos de AM; definições de Samuel (1959) e de Mitchell (1997: experiência E, tarefa T, medida de desempenho P) (slides 10, 13).
  - 03:16–05:06 tipos de aprendizado: supervisionado = tarefas preditivas, dá as respostas corretas no treino; não supervisionado = tarefas descritivas, sem resposta, acha padrões; reforço (slides 30–34, 67, 73).
  - 05:06–09:50 supervisionado em detalhe: entrada e saída conhecidas; regressão = saída contínua (exemplo: nível de sinal de rádio × distância da antena), classificação = rótulo discreto (exemplo de imagens gato/não gato com 1 e 0); depois do treino vem a etapa de **inferência**, com imagem que não participou do treino (slides 25–26, 31, 33, 36, 39).
  - 09:51–11:30 não supervisionado: tarefas de agrupamento, associação (padrões frequentes de itens; cita o algoritmo apriori) e sumarização (slides 34, 37, 57, 63).
  - 12:35–13:58 associação: história da fralda e da cerveja (compras juntas; "folclórica", diz ele) (slides 63–64).
  - 14:37–16:03 reforço: tarefa, sistema de recompensas, ambiente (labirinto), agente (o rato), estado, recompensa (slide 73).
- **Não cobre:** semissupervisionado e ativo; as sete etapas do processo; hiperparâmetros; generalização; classificadores estatísticos × estruturais; indução × dedução; atributo preditivo × alvo por nome (diz "entrada e saída", "rótulo").
- **Divergências com o slide:**
  - 02:32–02:47 a frase de Samuel sai trocada na transcrição ("aprenderem e serem programados explicitamente"); o sentido correto é aprender **sem** ser programado explicitamente (conhecimento externo; a própria transcrição diz isso em 01:10). Usar a forma de 01:05–01:13.
  - Tarefas descritivas incluem **sumarização** (11:09, 13:58): os slides 37 só têm agrupamento e associação. Extra, não decorar.
  - 11:35–12:35 usa Mendeley e Google Notícias como exemplos de agrupamento; são exemplos fracos (são mais buscadores) e não estão nos slides: pular.
  - Samuel × Mitchell não estão nos slides: extra.
  - Diz que o curso não verá reforço (04:38): é só aviso do curso dele.
- **Nível e foco:** iniciante a intermediário, só conceito; sem código; terminologia (preditivo/descritivo) igual à dos slides.
- **Idioma/qualidade:** português do Brasil, fala fluida mas com muitos "né", "tá"; a transcrição perde pontuação, mas é compreensível. Qualidade boa como mapa geral.
- **Trechos recomendados:** 00:24–03:16 · 03:16–05:06 · 05:06–09:50 · 09:51–11:30 · 12:35–13:58 · 14:37–16:03 (13:54 no total). Se o tempo apertar, os essenciais para cobrir lacunas são 09:51–11:30, 12:35–13:58 e 14:37–16:03.
- **Veredito: `aprovar só os trechos acima`** (complemento; nenhum outro vídeo da lista cobre IA ⊃ AM ⊃ profundo, descritivas/associação e a visão unificada dos tipos).

### BuUjhqd2WnU — Aula de curso de ciência de dados — O que é um dataset para treinar algoritmos (14:50) — aprovar só trechos

- **Cobre:**
  - 00:44–01:43 contexto: base Iris (três espécies; medidas de pétala e sépala), objetivo de classificar uma flor nova pelas medidas.
  - 01:43–04:03 a base vira uma **tabela**: cada linha é uma observação (também chamada instância ou exemplo); as colunas são as variáveis preditoras (x1…x4) e a coluna y é a espécie; uma observação nova chega só com os x e o algoritmo tem de prever y (slides 28–29).
  - 04:03–05:00 os dados têm rótulo; por isso é aprendizado supervisionado; "aprender" é criar uma regra (equação, árvore de decisão) (slides 30–31).
  - 05:00–05:59 mesmo com imagens (matriz de pixels) vira tabela; quando **não existe variável resposta**, é aprendizado não supervisionado, "a parte de cluster" (slide 30).
  - 10:37–11:47 variáveis quantitativas discretas (contagens, inteiros, "infinito contável") × contínuas (decimais: idade, altura, faturamento) (slide 36, definição de discreto/contínuo).
- **Não cobre:** os termos "atributo preditivo" e "atributo alvo" dos slides (usa "variável preditora" e "variável resposta/y"); vetor de características; as tarefas preditivas × descritivas; divisão treino/teste.
- **Divergências com o slide:**
  - Terminologia: observação/instância/exemplo = "padrões, registros ou exemplos" (slide 28); variável preditora = atributo preditivo; variável resposta = atributo alvo (slide 29).
  - Gravação de aula ao vivo, com perguntas do chat; o trecho 06:00–07:50 (explicação de `join` de tabelas) é desvio; pular.
  - Erros de reconhecimento de fala: "orgulhismo" = algoritmo; "650 observações" = 150 (03:38 diz 150); "tamanho e altura" da pétala = comprimento e largura (conhecimento externo).
  - 07:58–10:37 (qualitativas nominais × ordinais) está fora dos slides desta aula, e em 08:30–08:36 a fala troca "ordinal" por "nominal" (lapso); fora dos trechos aprovados.
- **Nível e foco:** iniciante; exemplo com tabela; sem código.
- **Idioma/qualidade:** português do Brasil, professor didático; gravação de sala de aula, com ruído (lanche, cachorro, chat). Qualidade média, mas é a melhor explicação de "o que é a tabela de treino" do conjunto.
- **Trechos recomendados:** 00:44–05:59 e 10:37–11:47 (6:25).
- **Veredito: `aprovar só os trechos 00:44–05:59 e 10:37–11:47`.**

### ZGyY2goDIJY — Vladimir Ribeiro Prates (Ciência e Negócios) — AM: supervisionado e não supervisionado (7:24) — aprovar só trechos (opcional)

- **Cobre:**
  - 00:53–02:00 supervisionado = há uma **variável resposta**, a coluna foco da análise; exemplo: prever se o colaborador pede demissão no mês seguinte (slide 30).
  - 02:00–02:43 sinônimos: variável dependente = variável resposta = target; variáveis independentes = explicativas (as que "explicam" a resposta) (slide 29).
  - 02:43–05:06 regressão = resposta numérica; classificação = resposta categórica; coluna só com 0 e 1 é **classificação**, não regressão; idade numérica dividida em faixas etárias vira alvo categórico e a tarefa vira classificação (slide 36).
  - 06:52–07:18 resumo: a diferença está na existência ou não de uma variável resposta.
- **Não cobre:** agrupamento ou associação por nome; tarefas preditivas × descritivas; "atributo alvo/preditivo" com esses nomes.
- **Divergências com o slide:** usa "numérica × categórica" onde os slides dizem "contínuo × discreto" (slide 36); equivalentes para o caso comum. 06:15 fala em "fazer essas classificações" de perfis de clientes no não supervisionado: no slide, o nome é agrupamento (slide 57). O trecho 05:07–05:48 sobre o não supervisionado é confuso (ele mesmo diz que a explicação pode ter ficado confusa): fora dos trechos.
- **Nível e foco:** iniciante; só conceito.
- **Idioma/qualidade:** português do Brasil, fala clara; pouca profundidade. Qualidade média. Valor principal: liga os nomes de estatística (dependente/independente) aos de AM (alvo/preditivo), útil para quem vem de engenharia de software.
- **Trechos recomendados:** 00:53–05:06 e 06:52–07:18 (4:39).
- **Veredito: `aprovar só os trechos 00:53–05:06 e 06:52–07:18`, como complemento (`optional`).** Fica redundante com JDDqP6IZ4NQ e rDIocV_r9Xk em parte; a vantagem é a ligação dos nomes (resposta/target).

### PkJIxrOYnMw — UNIVESP — Aprendizado supervisionado, introdução aos modelos preditivos (20:55) — aprovar só trechos (opcional)

- **Cobre:**
  - 01:23–03:00 supervisionado recebe pares entrada/saída; classificação = rótulo discreto, regressão = quantidade contínua (slide 36).
  - 03:00–05:00 o algoritmo induz um **modelo** = função estimadora f̂(x) que tenta se aproximar da função real f(x) a partir dos pares (x, y); se o rótulo é categoria, o estimador é um **classificador**; se contínuo, **regressor** (slide 53: "h tão próxima quanto possível de f(x)").
  - 05:00–05:45 fronteira que separa doentes de saudáveis (classificador) × função ajustada a valores (regressor).
  - 08:10–09:20 base de regressão (Suíça 1880, 47 populações): o alvo é um valor em intervalo contínuo; há uma coluna de **atributo alvo** que mostra a resposta correta ao modelo no treino (slides 29, 36, 51).
  - 09:21–10:44 função de estimação linear: combinação dos atributos com pesos **W** e um termo de **viés (bias)**; o treinamento otimiza W e viés para aproximar o y correto (slide 80: "parâmetros de viés b e peso w").
  - 12:14–12:49 função de custo mede o erro da estimativa e guia o treino: minimizar o custo (slide 80: aprimorar o modelo a cada amostra).
- **Não cobre:** a notação do slide 53 (argmax); as três equações; hiperparâmetros; sete etapas do processo.
- **Divergências com o slide:**
  - Usa f̂(x), "estimador" e "função de estimação" onde o slide usa h (hipótese) e H (conjunto de hipóteses). Mesma ideia, nomes diferentes: na prova, usar os do slide.
  - 17:05–20:00 apresenta uma taxonomia de métodos preditivos (baseados em distância, probabilísticos, conexionistas, simbólicos, margem) que **não é** a divisão do slide 45–46 (estatísticos × estruturais). Não confundir; fora dos trechos.
  - 12:50–16:00 explica a função de custo da classificação binária (log) com logaritmos: é cálculo; a prova não cobra; fora dos trechos.
  - 05:48–08:10 (Iris) repete o que BuUj mostra com mais clareza; fora dos trechos.
- **Nível e foco:** intermediário (universitário), com notação matemática; pouco código.
- **Idioma/qualidade:** português do Brasil, professor claro, ritmo de aula. Qualidade boa, mas mais técnico que os demais; por isso complemento.
- **Trechos recomendados:** 01:23–05:45 · 08:10–09:20 · 09:21–10:44 · 12:14–12:49 (7:29).
- **Veredito: `aprovar só os trechos acima`, como complemento (`optional`).**

### WqMnQuC19Rg — Introdução ao algoritmo k-means (14:43) — aprovar

- **Cobre:**
  - 00:11–02:32 o que é agrupamento (também "clusterização") e aplicações: segmentação de mercado, mala direta, agrupar notícias por assunto, produtos e perfis de clientes (exemplo da Netflix), redes sociais (slide 60).
  - 02:32–04:00 agrupamento é aprendizado **não supervisionado**: não há supervisor que diga a classe ou o valor; comparação com classificação e regressão, onde há atributo alvo; "o próprio algoritmo descobre os padrões" (slides 30, 34, 37, 57).
  - 04:00–05:00 elementos do mesmo grupo devem ser similares e diferentes dos de fora; é preciso uma **métrica de distância** (slide 57: "reunir por similaridade").
  - 05:16–09:50 o algoritmo k-means (Lloyd): inicializa K centroides ao acaso, associa cada ponto ao centroide mais próximo, recalcula cada centroide como média dos pontos, repete; o K (número de grupos) é obrigatório (slide 58: "o número de clusters influencia o resultado").
  - 09:50–14:30 exemplo com idade × salário e K = 3; no fim, interpreta os grupos (mais velhos que ganham mais etc.) e propõe uma campanha para um deles (slides 57 e 60: o cientista de dados dá o significado/rótulo ao grupo).
- **Não cobre:** que um agrupamento pode não ter significado relevante (slide 58); detecção de outliers e feature engineering por agrupamento (slides 60–61); escolha do K; outros algoritmos de agrupamento (só k-means).
- **Divergências com o slide:**
  - O k-means em si **não aparece** nos slides: 05:16–14:30 vai além do exigido (útil para entender o que é agrupar; o algoritmo não é cobrado). Clips B e C marcados como extra.
  - 03:39 a fala "nós vamos criar novos dados" (no agrupamento) é confusa; entender como "descobrir grupos nos dados existentes".
  - O vídeo supõe que o aluno viu KNN antes (05:05); basta a ideia de distância.
  - Transcrição: "CAMINS/Kminz" = k-means; "Marte" em 14:18 = marketing.
- **Nível e foco:** iniciante a intermediário, conceito com desenho passo a passo; sem código.
- **Idioma/qualidade:** português do Brasil, fala clara e calma; os desenhos são citados ("aqui", "esse centroide") e a transcrição não os mostra, mas o vídeo mostra. Qualidade boa.
- **Trechos recomendados:** 00:11–05:00 (essencial, 4:49); 05:16–09:50 e 09:50–14:30 (extra, k-means).
- **Veredito: `aprovar`** (essencial só o primeiro trecho; os dois últimos são aprofundamento).

### 3rU1H1q0vKI — IA com Clareza — Desvendando o aprendizado semissupervisionado (14:14) — aprovar só trechos

- **Cobre:**
  - 01:23–03:05 problema: muitos dados, pouco rótulo; rotular à mão custa tempo e especialistas (visão computacional); a solução combina **poucos dados rotulados e muitos não rotulados** (slide 68: "rotular exemplos pode ter custo elevado, ser difícil").
  - 03:06–05:11 como funciona: treina com os rotulados; depois o modelo prevê rótulos para os não rotulados (por propagação de rótulos ou pseudo-rótulos, "rótulos provisórios gerados pelo próprio modelo"), e refina de forma iterativa (slide 70: modelo induzido rotula os não rotulados, entram no treino, repete).
  - 07:37–07:55 **self-training**: treina com os rotulados, prevê os não rotulados e adiciona ao treino só os exemplos em que está mais confiante, repetindo (slide 70: "objeto não rotulado com classe predita com boa confiança").
  - 10:07–11:21 riscos: dados não rotulados ruins prejudicam; erros do modelo inicial se propagam nas rodadas seguintes.
- **Não cobre:** agrupamento semissupervisionado com restrições de pares (slide 69); que o aprendizado ativo é um caso de semissupervisionado (slide 72); a ressalva do slide 70 sobre dados redundantes.
- **Divergências com o slide:** nenhuma factual nos trechos. O slide 70 diz que o semissupervisionado usa os dados "de forma passiva", o que o vídeo não discute. Restante do vídeo (co-training, SVM semissupervisionada, autoencoders, aplicações, 02:58–03:05 resumo) é extra, e há propaganda de inscrição (00:31–01:23 e 13:58–14:14): fora dos trechos.
- **Nível e foco:** iniciante; só conceito; narração tipo roteiro, em tom de apresentação.
- **Idioma/qualidade:** português do Brasil; texto bem estruturado, mas genérico (tom de apresentação, quase sem exemplo numérico). Qualidade média.
- **Trechos recomendados:** 01:23–03:05 · 03:06–05:11 · 07:37–07:55 · 10:07–11:21 (5:21).
- **Veredito: `aprovar só os trechos acima`.** É o único vídeo da lista que define semissupervisionado.

### ANIw1Mz1SRI — Computerphile — Active (Machine) Learning (6:10, em inglês) — aprovar só trecho

- **Cobre:**
  - 00:00–01:05 dados têm duas partes (atributos e rótulos); rótulos vêm de humanos (exemplo: desenhar caixas em rostos); é caro e chato.
  - 01:05–03:03 ideia do aprendizado ativo: anota-se, por exemplo, 10% dos dados, treina um modelo e usa-o nos 90% restantes; o modelo precisa dar **confiança** em cada previsão; pede-se ao humano que anote só o que o modelo **não tem certeza** (slide 72: "seleciona interativamente as amostras que serão rotuladas").
  - 03:03–04:20 o ciclo: humano rotula, volta ao treino, nasce nova hipótese h1 (h0 → h1…), repete; critérios extras: escolher exemplos bem diferentes dos já rotulados (frames de vídeo seguidos são redundantes) (slide 72: "evitar amostras redundantes").
  - 04:20–05:28 "aprendizado cooperativo": o que o modelo tem alta confiança entra com o rótulo da máquina; resultado relatado: 10–20% do esforço de anotação para o mesmo desempenho.
- **Não cobre:** que o ativo é uma estratégia do semissupervisionado (o vídeo trata como técnica à parte); a ideia dos slides de que as amostras não selecionadas são **descartadas** (72); nomes em português.
- **Divergências com o slide:** o vídeo descreve também o aprendizado cooperativo (aceitar rótulo da máquina), que se parece com o semissupervisionado do slide 70; o slide 72 trata só do ativo, com seleção interativa. Sem contradição, mas dois termos diferentes: manter "ativo" = escolher o que rotular.
- **Nível e foco:** iniciante a intermediário; conceito com uma figura de laço (loop). 
- **Idioma/qualidade:** **inglês** (falante nativo, claro e pausado). Qualidade boa: explica o laço h0 → h1 muito bem. A partir de 05:28 o vídeo muda de assunto (captchas, aprendizado por similaridade/âncora): fora do trecho.
- **Trecho recomendado:** 00:00–05:33 (5:33).
- **Veredito: `aprovar só o trecho 00:00–05:33`.** Não há candidato em português para o tópico; o inglês é aceito porque o conceito é único e a explicação é clara. Avisar no `note` e sugerir ativar a legenda automática. Se o usuário prefere só português, descartar e cobrir com o texto.

### 5u8yNEN5arQ — O que é Aprendizagem por Reforço (8:54) — aprovar só trecho

- **Cobre:**
  - 00:08–00:58 agente (robô/IA) num ambiente (labirinto), que aprende com erros e acertos até chegar ao objetivo.
  - 01:01–02:04 ação → novo estado → **recompensa** positiva (aproximar do objetivo) ou negativa (afastar); vários passos de interação (slide 73: recompensar ação positiva e punir negativa).
  - 02:06–02:50 diferença para o supervisionado: não há base de dados pronta; o agente aprende **interagindo com o ambiente**; muito usado em robótica (slide 73: agentes inteligentes; "aprender sozinho a melhor estratégia").
  - 02:52–05:30 exemplos do dia a dia: torradeira, ações na bolsa, multa de estacionamento; recompensa a cada passo, não só no fim.
  - 05:28–08:10 treinar cachorro (petisco × bronca); em computador a recompensa é um sinal (+1 e −1); robô sem pré-programação versus programado; robôs de futebol.
- **Não cobre:** os termos política (policy), função de valor, exploração × aproveitamento; o exemplo do slide (melhor trajetória entre dois pontos) aparece só como o labirinto (00:08–00:58); a leitura recomendada (08:12 em diante) é indicação de artigos.
- **Divergências com o slide:** nenhuma. Coerente com o slide 73 ("recompensar ou punir; o agente deve aprender sozinho"). O vídeo não diz que é um tipo à parte do semissupervisionado/ativo; o slide 67 junta os três como "tarefas fora da hierarquia clássica".
- **Nível e foco:** iniciante; só conceito; exemplos intuitivos.
- **Idioma/qualidade:** português do Brasil, ritmo calmo; a transcrição tem poucos erros. Qualidade boa.
- **Trecho recomendado:** 00:08–08:12 (8:04).
- **Veredito: `aprovar só o trecho 00:08–08:12`** (o resto é indicação de leitura).

### HDLIqanb4cw — Explicando os hiperparâmetros (6:55) — aprovar só trechos (opcional)

- **Cobre:**
  - 00:19–01:14 existem **hiperparâmetros**: configurações do algoritmo que **você** escolhe; algoritmos têm dezenas, a maioria é configuração; alguns são mais importantes (exemplo no LightGBM).
  - 01:32–02:58 número de estimadores (= número de árvores de decisão) escolhido por tentativa: aumenta ou reduz até achar o melhor resultado no teste; mencionando que técnicas avançadas existem (grid search, random search) (slide 81: "podem ser definidos novos hiperparâmetros").
  - 02:59–04:28 **taxa de aprendizado** (learning rate): a "velocidade" com que o modelo aprende; muito rápida erra a precisão, muito lenta demora: sempre um trade-off (slide 81: "taxa de aprendizado, fator para as mudanças de parâmetros do modelo").
- **Não cobre:** a diferença entre **parâmetros** (w e b, aprendidos no treino; slide 80) e **hiperparâmetros** (fixados antes; slide 81); a "quantidade de repetições sobre o conjunto de treino" (épocas) do slide; onde os hiperparâmetros entram na ordem das etapas.
- **Divergências com o slide:** chama os hiperparâmetros de "parâmetros" em 03:02 ("parâmetro de ajuste de otimização"); o slide separa os dois termos. O "número de estimadores" é específico de métodos que combinam árvores (LightGBM) e não está no slide. 05:58–06:48 (`scale_pos_weight`, classes desbalanceadas) e o resto do vídeo são específicos do LightGBM: fora dos trechos. 02:06–02:13 a fala sobre aumentar estimadores é confusa.
- **Nível e foco:** iniciante em AM, mas pressupõe ter visto código e ter ideia do que é uma árvore de decisão.
- **Idioma/qualidade:** português do Brasil, informal, professor que conversa; transcrição com alguns erros. Qualidade média.
- **Trechos recomendados:** 00:19–01:14 e 01:32–04:28 (3:51).
- **Veredito: `aprovar só os trechos acima`, como complemento (`optional`)**, com o aviso de que só a taxa de aprendizado coincide com o slide.

### tzeG-ubgNgQ — Machine Learning em Português (Aula 4): Generalização, Overfitting e Underfitting (10:54) — aprovar só trecho (opcional)

- **Cobre:**
  - 03:05–04:05 imaginar uma girafa, uma galinha, um leão, um carro: cada um imagina uma versão diferente, mas todos reconhecem; é isso que se quer de um modelo: ser **genérico**.
  - 04:05–05:45 o modelo de reconhecer periquitos deve ser genérico o bastante para reconhecer periquitos diferentes; se quase todas as imagens de treino são o mesmo periquito (azul, de lado, na corda), ele só reconhece aquele (slide 82: "um especialista nos dados treinados" e não "válido para casos futuros").
- **Não cobre:** a definição formal de "capacidade de generalização" (slide 82: quanto mais os resultados esperados e obtidos convergem, maior a capacidade); a ligação com os dados de teste; hiperparâmetros.
- **Divergências com o slide:**
  - Nenhuma no conceito. **Atenção a lapsos de fala:** em 04:26 chama de "teste" as imagens que são de **treino**; em 05:56–06:28 o trecho sobre overfitting também mistura "treino" e "teste" (99% no teste e 63% no treino, o que está invertido): por isso esses minutos ficam fora.
  - Overfitting e underfitting (05:48–09:12) **não estão nos slides** da Aula 1; fora do trecho.
- **Nível e foco:** iniciante; analogia com periquitos.
- **Idioma/qualidade:** português do Brasil, mas desorganizado: começa dizendo que gravou de novo, divaga (agapornis, ornitorrinco) e tem lapsos. Qualidade fraca a média: aceito **apenas** o trecho 03:05–05:45 por ser o único que explica a ideia do slide 82.
- **Trecho recomendado:** 03:05–05:45 (2:40).
- **Veredito: `aprovar só o trecho 03:05–05:45`, como complemento (`optional`)**, com avisos. Se o usuário preferir só vídeos de qualidade alta, descartar e cobrir só com o texto.

## 3. Descartados e por quê

| ID | Vídeo | Duração | Motivo |
| :-- | :-- | :-: | :-- |
| Oq_kM6M_KQ0 | Análise de padrão de compra com Regras de Associação | 5:40 | É a abertura de um estudo de caso (Kaggle Instacart): só 01:01 de conceito (cestas de compra, fralda e cerveja, "padrões escondidos") e o resto é leitura do enunciado, prêmios do concurso e importação de bibliotecas Python. A história da fralda e da cerveja já está em TY45 (12:35–13:58), em fala mais próxima do slide 63. Lista um conceito útil em 02:06 ("regras de associação são uma das quatro tarefas, com regressão, classificação e agrupamento"), mas é de passagem. Não aprovo para não completar a lista com vídeo fraco. |
| lsPucobtdDk | AI ML Training versus Inference | 4:40 | O áudio é dublagem automática de um vídeo em inglês e a transcrição é incoerente: "M.L.Model", e a **fase de treinamento aparece no lugar de inferência** em 01:39–02:00 ("a fase de treinamento é menos intensiva em recursos"), o que inverte o conceito. Foca em modelos generativos/LLM e produção (modo batch × tempo real), fora dos slides. A distinção treino × inferência está em TY45 (09:28–09:50). |

## 4. Sequência recomendada para os aprovados desta rodada (ordem dos slides)

| # | Slides | Id proposto | Vídeo | Trechos (início–fim) | Tempo | Por quê / o que ignorar |
| :-: | :-- | :-- | :-- | :-- | :-: | :-- |
| 1 | 10, 13, 30–37, 63, 73 | a1-v7 | TY45HIJ3RpM | 00:24–03:16 · 03:16–05:06 · 05:06–09:50 · 09:51–11:30 · 12:35–13:58 · 14:37–16:03 | 13:54 | Mapa geral das tarefas; divisível por tópico (os dois últimos trechos ficam junto dos slides 63 e 73). Opcional. |
| 2 | 28–29, 36 | a1-v8 | BuUjhqd2WnU | 00:44–05:59 · 10:37–11:47 | 6:25 | Tabela de treino, x e y. Ignorar a conversa sobre `join`. |
| 3 | 29–31, 36 | a1-v9 | ZGyY2goDIJY | 00:53–05:06 · 06:52–07:18 | 4:39 | Nomes resposta/target. Opcional. |
| 4 | 36, 53, 80 | a1-v10 | PkJIxrOYnMw | 01:23–05:45 · 08:10–09:20 · 09:21–10:44 · 12:14–12:49 | 7:29 | f̂(x) ≈ f(x); pesos e viés; função de custo. Opcional. |
| 5 | 57–61 | a1-v11 | WqMnQuC19Rg | 00:11–05:00 · 05:16–09:50 · 09:50–14:30 | 14:03 | Agrupamento (essencial: o 1º trecho); k-means é extra. |
| 6 | 68–70 | a1-v12 | 3rU1H1q0vKI | 01:23–03:05 · 03:06–05:11 · 07:37–07:55 · 10:07–11:21 | 5:21 | Semissupervisionado. |
| 7 | 72 | a1-v13 | ANIw1Mz1SRI | 00:00–05:33 | 5:33 | Aprendizado ativo (inglês). |
| 8 | 73–74 | a1-v14 | 5u8yNEN5arQ | 00:08–08:12 | 8:04 | Reforço. |
| 9 | 81 | a1-v15 | HDLIqanb4cw | 00:19–01:14 · 01:32–04:28 | 3:51 | Hiperparâmetros (só a taxa de aprendizado coincide). Opcional. |
| 10 | 82 | a1-v16 | tzeG-ubgNgQ | 03:05–05:45 | 2:40 | Generalização (analogia). Opcional. |

## 5. Lacunas que continuam (o texto escrito precisa cobrir)

Esta rodada foi feita **sem internet**: só validei os candidatos que já estavam transcritos. A regra do playbook pede duas rodadas de busca por tópico importante; para os tópicos abaixo a segunda rodada de busca **ainda precisa ser feita** (ou aceitar a lacuna e cobrir só com o texto).

1. **Regras de associação (63–66): sem vídeo dedicado bom.** Só TY45 (10:42–11:30 e 12:35–13:58) e Oq_k (1 min) tocam no assunto; ambos mostram apenas a ideia de "itens comprados juntos". Falta um vídeo que explique, para iniciante, uma transação de compras e como se vê o padrão (suporte/confiança, não cobrados pelo slide). Termos para buscar: "regras de associação análise de cesta de compras explicação para iniciantes", "algoritmo apriori passo a passo", "market basket analysis fralda cerveja explicado". Se a busca não render, o texto cobre.
2. **Hiperparâmetros (81): cobertura parcial.** HDLI só explica a taxa de aprendizado e o número de árvores; falta o contraste parâmetros (w, b) × hiperparâmetros e a ideia de repetições/épocas. Buscar: "hiperparâmetros versus parâmetros do modelo", "o que são épocas epochs e taxa de aprendizado".
3. **Generalização (82): cobertura parcial e fraca.** tzeG só dá a analogia; o vínculo com os dados de teste fica no texto (N2TT2Q83abc já cobre a razão de testar com dados novos). Buscar: "generalização modelo de machine learning dados nunca vistos explicação simples".
4. **Agrupamento semissupervisionado com restrições de pares (69):** nenhum vídeo. Pouco provável de existir em nível inicial; cobrir com texto.
5. **Aprendizado ativo (72):** só vídeo em inglês (ANIw); sem candidato em português. Buscar "aprendizado ativo machine learning seleção de amostras rotuladas" se quiser português.
6. **Raciocínio indutivo × dedutivo (18–19), classificadores estatísticos × estruturais (45–46), equação argmax do slide 53 e as sete etapas em detalhe (75–79):** continuam sem vídeo (herdadas da rodada 1; PkJI toca a ideia de f̂(x) ≈ f(x) mas sem argmax, e propõe outra taxonomia de métodos). Cobrir com o texto.
7. **Slides só com figura (3–9, 12, 15, 22, 35, 47–49, 54–55, 59, 65–66, 71, 74):** os vídeos não mostram as figuras da professora; o texto descreve.
