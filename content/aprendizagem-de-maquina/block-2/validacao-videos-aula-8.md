# Validação dos vídeos pela transcrição — Aula 8 (Árvores de Decisão)

Método (refeito): a primeira versão desta ficha não se apoiava nas transcrições. Nesta rodada, li **inteira** a transcrição local (Whisper, `study transcribe`, por minuto) de cada vídeo abaixo e comparei com os 47 slides de `Aulas/Aula 8 - Arvore de decisao Mestrado` (texto em `estudo/_fontes_extraidas/`). Os vídeos mantidos da primeira versão (a8-v1, a8-v3, a8-v4, a8-v5) foram relidos e tiveram clipes, `covers` e avisos refeitos; o a8-v2 foi trocado. Os tempos `mm:ss` têm precisão de cerca de ±10 s (a transcrição vem em blocos de poucos segundos) e todos cabem na duração real do vídeo. Erros que dependem de conhecimento meu (fora do vídeo) estão marcados "(conhecimento externo)" ou "(cálculo meu)".

Duas rodadas de busca (`study search`, português primeiro): (1) entropia/ganho de informação, Gini, passo a passo, árvore de regressão, scikit-learn, vantagens e desvantagens; (2) série de Daniel Hasan Dalip, poda/pré-poda, hiperparâmetros (max_depth, min_samples), critérios Gini/entropia, regressão com erro quadrático. Transcritos e lidos 16 vídeos novos + 5 antigos (21 no total, incluindo os descartados).

Legenda da matriz: **B** = cobre bem · **P** = cobre parcialmente · **–** = não cobre · **X** = diverge do slide ou tem erro.

## 1. Matriz tópicos dos slides × vídeos mantidos

| Tópico (slides) | v1 SAÚDE | v6 Termin. | v7 Infogain | v8 Entropia+Ganho | v9 Def.+Criação | v3 Gini | v10 Kuniyoshi | v4 Numéricos+poda | v11 Regressão | v5 Overfit. | v12 Eng. Moderno | v13 Mario Filho | v14 Vant./Desv. | v15 Hiperparâm. |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Estrutura: raiz, nó, folha, ramo (3–4) | – | B | – | – | P | – | B | – | – | – | P | – | – | – |
| Perguntas encadeadas, exemplos (5–10) | P | – | – | – | B | – | B | P | – | – | – | – | – | – |
| ID3, C4.5, CART (11) | – | B | – | – | – | – | – | – | – | – | P | – | – | – |
| Classificação x regressão (12) | P | B | – | – | – | – | P | – | P | – | P | – | P | P |
| Regiões do espaço (13–14) | – | – | – | – | P | – | – | B | – | – | – | – | – | – |
| Entropia: intuição (16–17) | – | – | B | B | P | – | P | – | – | – | P | – | – | – |
| Ganho de informação, conta (18–24) | – | – | P | B | B | – | – | P | – | – | P | – | – | – |
| Índice Gini (25–29) | – | – | – | – | – | B | B | – | – | – | P | – | – | – |
| Melhor valor de split / atributos contínuos (30–31) | – | – | – | – | – | – | P | B | P | B | P | P | – | P |
| CART em regressão, MSE e média (31–32) | – | – | – | – | – | – | – | – | B | – | B | B | – | – |
| Regras de parada, poda, overfitting/underfitting (33–35) | – | P | – | – | P | – | – | B | P | B | P | B | – | B |
| Parâmetros de poda do sklearn (36) | – | – | – | – | – | – | – | P | P | – | B | B | – | P |
| criterion, splitter, max_features (37) | – | – | – | – | – | – | – | – | – | – | P | P | – | P |
| Pseudocódigo/indução, sklearn binário (38–42) | – | – | – | – | – | – | – | – | – | P | B | – | – | – |
| Reuso de atributos (43) | – | – | – | – | – | – | – | B | – | – | – | – | – | – |
| Vantagens (44) | – | – | – | – | – | – | P | – | – | – | P | – | B | B |
| Desvantagens (45) | P | – | – | – | – | – | – | P | – | P | P | – | B | B |

Leitura rápida: os blocos mais bem servidos são Gini (v3, v10), entropia (v7, v8), contínuos e pré-poda (v4, v5), regressão (v11, v12) e hiperparâmetros (v13). Lacunas que sobram: `splitter` (nenhum vídeo fala), `min_impurity_decrease` e `max_leaf_nodes` só de passagem, pseudocódigo do slide 38–42 (só v12/v5 tocam), intuição de Gini x entropia (slide 25, o limite [0; 0,5] x [0; 1]).

## 2. Fichas por vídeo (na ordem dos slides)

### asyLr0NUf3Q — Inteligência Artificial na Saúde — O algoritmo de Árvore de Decisão (7:43) — `a8-v1`, opcional

- **Cobre:** 00:00–01:32 árvore como perguntas encadeadas (vai chover? tem energia?) e o fluxograma do SAMU; 01:32–02:15 cada resposta abre um ramo; 02:20–02:50 uma árvore sozinha tem variância alta (overfitting) e pouca estabilidade; 07:23–07:43 árvores servem para regressão e classificação.
- **Não cobre:** os termos raiz/nó/folha/ramo **nunca aparecem**; critério de divisão, entropia, Gini, poda, interpretabilidade.
- **Divergências/erros:** de 02:50 a 07:04 (cerca de 4 min) é sobre bagging, Random Forest e boosting/XGBoost (comitês), que o plano diz não entrar no Bloco 2. No trecho há erros de fala: boosting "eleva os pesos das features problemáticas" (conhecimento externo: o boosting aumenta o peso das amostras mal classificadas). A versão anterior da ficha dizia que o vídeo cobria interpretabilidade e "estrutura de nós"; **não cobre**.
- **Nível e idioma:** iniciante; português do Brasil, legível; salto brusco em 02:20.
- **Veredito: `aprovar só os trechos 00:00–02:50 e 07:23–07:43`**, opcional (apenas analogia).

### 7FnfYukQKUQ — Michel Janos — 28 Aprendizado com Árvores de Decisão: Terminologia (4:19) — `a8-v6` (novo)

- **Cobre:** 00:00–01:00 árvores servem para classificação e regressão; 01:00–02:30 nó raiz, divisão, nó de decisão, nó folha/terminal, poda, ramificação/sub-árvore, nó pai e filho; 02:30–03:30 cada nó é um teste, cada aresta uma resposta, recursão, pureza sobe ao descer; 03:30–04:18 ID3, C4.5, CART, CHAID e no que diferem (critério de divisão, regressão x classificação, overfitting, valores ausentes).
- **Não cobre:** exemplo numérico, Gini, entropia, hiperparâmetros.
- **Divergências/ressalvas:** define "poda" como remover sub-nós depois (pós-poda), enquanto os slides 33–37 tratam de limites na construção. Legenda erra nomes ("SER-4.5" = C4.5; "interação Q²" = CHAID, qui-quadrado).
- **Nível e idioma:** iniciante; português do Brasil, curto.
- **Veredito: `aprovar` 00:30–04:15.** Preenche a lacuna da terminologia (slides 3, 4 e 11).

### 8nV6lICu-l8 — Daniel Hasan Dalip — Infogain (5:14) — `a8-v7` (novo)

- **Cobre:** 00:30–02:30 entropia como "quantidade mínima de informação": figuras com 100% verde (previsível) x misturadas; 02:30–03:30 baixa com 100% de uma classe, mais alta com 80/20, cresce com a distribuição uniforme; 03:30–04:30 exemplo 37,5%/62,5% = 0,95; 04:30–05:13 filtrar renda = alta deixa o dado mais previsível: redução da entropia = ganho de informação.
- **Não cobre:** a conta com logaritmo, a ponderação pelo tamanho dos ramos, escolha de atributo.
- **Divergências/ressalvas:** descreve entropia como informação mínima (teoria da informação), não como "aleatoriedade"; é o mesmo sentido. Legenda: "ganho de formação".
- **Nível e idioma:** iniciante; português do Brasil; hesitante.
- **Veredito: `aprovar` 00:30–05:13.** Intuição para o slide 16–17.

### Plynx5N-urc — Michel Janos — 25 Entropia e Ganho de Informação (8:21) — `a8-v8` (novo)

- **Cobre:** 00:30–01:30 entropia = desordem/incerteza; 01:30–02:30 distribuição equiprovável tem maior entropia, caixa só de bolas pretas tem zero; 02:30–03:30 fórmula H = −Σ pᵢ log₂ pᵢ e gráfico (zero nos extremos, máximo em 50/50); 03:30–04:30 30 brancas/70 pretas ≈ 0,88 e máximo por número de classes (2→1, 4→2, 8→3); 04:30–05:30 ganho = redução da entropia; 05:30–08:10 exemplo do tênis (14 dias, 9 sim e 5 não): ganhos tempo 0,248, umidade 0,151, vento 0,048, temperatura 0,029; maior ganho vira a raiz; repete no nível seguinte; nem toda folha é pura.
- **Não cobre:** Gini, atributos contínuos, poda.
- **Divergências/erros:** diz "H = 0,970" para 9 sim e 5 não e logo depois usa 0,940 (o correto é 0,94); a conta da urna (10, 5 e 4 bolas) não fecha; rótulos normal/alta da umidade parecem trocados, mas 0,985, 0,592 e o ganho 0,151 conferem (cálculo meu). O exemplo não é o dos slides 19–24, mas a lógica é igual.
- **Nível e idioma:** iniciante a intermediário; português do Brasil; fala clara.
- **Veredito: `aprovar` 00:30–08:10.** Substitui o a8-v2: aqui há a intuição da entropia **e** um exemplo numérico completo.

### fzGCkpHBZEo — Daniel Hasan Dalip — Definição e Criação (10:11) — `a8-v9` (novo), opcional

- **Cobre:** 00:00–01:30 nó interno = condição, folha = resultado; exemplo de crédito (renda e dependentes) e os mesmos cortes no plano; 01:30–03:00 por que escolher pelo ganho (árvore menor, legível, menos erro no treino); 03:30–06:00 ganho(renda) ≈ 0,55 como média ponderada, maior que o do dependente; 06:30–08:30 segundo nível no subconjunto "renda alta"; 08:30–10:04 exemplo com três atributos (renda, depois idade, depois dependente).
- **Divergências/erros:** os números falados não batem com o vídeo anterior da série (entropia geral 1 aqui x 0,95 lá; "75% aprovados" x entropia 0,72, que é 80/20); legenda tropeça em frações. Cita Random Forest e poda de passagem. Usa ID3 (um ramo por valor).
- **Nível e idioma:** iniciante a intermediário; português do Brasil.
- **Veredito: `aprovar como opcional`** (a ideia: maior ganho vira o nó; repete no subconjunto), sabendo que as contas não conferem.

### zEuU0RWRmV8 — Paulo Moura Oliveira — Exemplo Resolvido com Gini (6:21) — `a8-v3`

- **Cobre:** 00:40–01:30 Gini = 1 − Σ pᵢ² e Gini inicial = 0,32 (2 positivos, 8 negativos); 01:30–04:30 para cada atributo (temperatura, dá à luz, quadrúpede, hiberna) Gini de cada ramo, média ponderada e diferença para o inicial; 04:30–04:50 escolhe o atributo; 04:50–06:20 segundo nível e árvore resultante.
- **Não cobre:** o que o Gini mede (impureza), comparação com entropia/limite 0,5 (slide 25), atributos contínuos.
- **Divergências/erros:** chama de "ganho" a diferença e escolhe o **maior**; o slide 28 diz "menor Gini ponderado" (mesmo critério em duas formas). A legenda troca valores (0,98 por 0,48; 0,84 por 0,24; 0,032 por 0,072). O segundo nível é difícil de seguir. Os slides 26–27 têm os parênteses da fórmula errados (o vídeo usa a forma correta).
- **Nível e idioma:** intermediário; português de Portugal; legível.
- **Veredito: `aprovar`** com ressalvas; leitura antes ajuda.

### MMpeBCWBjhc — Andre Kuniyoshi — Como funciona uma árvore de decisão (25:26) — `a8-v10` (novo), opcional

- **Cobre:** 01:00–02:10 classificação x regressão; 02:10–04:30 árvore = perguntas sim/não, perguntas boas e ruins; 04:30–06:00 fórmula do Gini; 07:00–08:30 raiz; 08:30–15:30 Gini de cada pergunta possível, ponderado, "quanto menor melhor", empate resolvido ao acaso; 16:00–22:30 nós, folhas (nó puro) e repetição; 22:30–24:00 classifica um dado novo e explica por que é interpretável.
- **Divergências/erros:** diz que Gini "mais perto de 1" é bagunçado (para duas classes o máximo é 0,5); lê a fórmula sem os parênteses corretos; escolhe em empate "porque quis"; 1:30 iniciais de propaganda; poda adiada.
- **Nível e idioma:** iniciante; português do Brasil; lento e repetitivo.
- **Veredito: `aprovar só os trechos 01:00–24:00`, opcional.** Melhor exemplo de árvore inteira nascendo, com os nomes raiz/nó/folha.

### TQccXuLg75g — Daniel Hasan Dalip (UTFPR) — Atributos numéricos e poda (5:02) — `a8-v4`

- **Cobre:** 00:00–01:30 cortes em x e em y, ficar com o de maior ganho; 01:30–02:15 continua cortando, y reusado, superfície de decisão em regiões; 02:15–03:00 região com um ponto = overfitting; 03:00–04:30 pré-poda: 80% de uma classe, mínimo de instâncias para dividir (por exemplo 10), nível máximo.
- **Não cobre:** nomes `min_samples_split`/`max_depth`, só binário no sklearn (slide 41), regressão com MSE.
- **Divergências:** usa ganho de informação, não Gini; chama os critérios de parada de "poda" (uso do slide 33); assume ID3 visto. Tempos anteriores estavam levemente deslocados.
- **Nível e idioma:** intermediário prático; português do Brasil.
- **Veredito: `aprovar` o vídeo inteiro.**

### pPWxZpSkt1s — Téo Me Why — Machine Learning 08: Árvore de Decisão — Regressão (14:59) — `a8-v11` (novo)

- **Cobre:** 01:00–03:30 sem a variável o melhor palpite é a média; 03:30–05:30 divide a variável contínua e prevê a média de cada grupo; 05:30–09:30 testa todos os cortes e escolhe o de menor erro quadrático total; 09:30–11:00 busca exaustiva (um nó por valor, no limite); 11:00–14:30 profundidade 1, 2 e mais: escada e overfitting; 14:30–14:58 base de teste.
- **Não cobre:** nome MSE, ponderação pelo tamanho dos grupos, hiperparâmetros além de profundidade.
- **Divergências/ressalvas:** aula ao vivo, informal (um palavrão curto), legenda com erros ("MaxDef" = max_depth); usa uma só variável.
- **Nível e idioma:** iniciante; português do Brasil.
- **Veredito: `aprovar` 01:00–14:30.** Preenche a lacuna da árvore de regressão (slide 32).

### pocz0bWjp_o — Born to be AI — Overfitting e Atributos numéricos (10:32) — `a8-v5`

- **Cobre:** 00:00–01:30 overfitting = decorar; folha com 1 instância; 1.000 instâncias com folhas de 3; 01:30–04:40 trocar subárvore pelo rótulo majoritário; custo (fraude); 04:40–07:00 por que não há um ramo por valor; 07:00–10:00 ponto de corte x1 < 0,42, x2 < 0,48, recursão, ordenar valores e escolher o corte.
- **Divergências:** descreve **pós-poda** ("depois que ela está construída"); os slides 35–37 tratam de limites **durante** a construção (pré-poda). Assume o ID3 e cita ramo por valor para categóricos (sklearn é binário). Nenhum nome de hiperparâmetro é citado. Legenda: "o contrador" = computador.
- **Nível e idioma:** intermediário visual; português do Brasil; desenho à mão.
- **Veredito: `aprovar` o vídeo inteiro**, com o aviso de pós-poda.

### Ka_GeDmjq8w — Engenheiro Moderno — O Guia Prático da Árvore de Decisão (16:22) — `a8-v12` (novo)

- **Cobre:** 00:00–01:30 lê uma árvore do sklearn (binária, pergunta, Gini, amostras); 01:30–04:30 nó puro vira folha, impureza 1 − Σ pᵢ², menor impureza em cada nó; 05:00–05:30 dividir para conquistar; 07:00–08:30 custo = média ponderada das impurezas esquerda/direita, fórmula da entropia; 08:30–09:30 Gini x entropia, ganho de informação; 09:30–11:30 hiperparâmetros (max_depth, min_samples_split, min_samples_leaf, min_weight_fraction_leaf, max_leaf_nodes, max_features); 11:30–14:00 DecisionTreeRegressor, CART, custo com MSE ponderado e previsão pela média; 14:30–15:40 resumo.
- **Divergências/erros:** o vídeo começa no meio de uma aula; Gini 0,667 no nó raiz de 3 classes (o slide 25 diz [0; 0,5], só para 2 classes); diz que o ganho é "o inverso do grau de impureza" (impreciso); legenda erra nomes de parâmetros ("MaxDiffNode", "MinSamplesDiff"); não cita `splitter` nem `min_impurity_decrease`; frase final sobre normalização confusa.
- **Nível e idioma:** intermediário; português do Brasil; fala corrida.
- **Veredito: `aprovar só 00:00–04:30, 07:00–14:00 e 14:30–15:40`.** Cobre o slide 31 (CART com MSE na regressão) e os nomes do slide 36.

### BDqejVlCfvc — Mario Filho — Decision Trees na Prática (30:18) — `a8-v13` (novo)

- **Cobre:** 07:00–09:30 árvore profunda overfita; para cada feature procura o melhor corte pela pureza (MSE no exemplo); 09:30–12:30 vai até um exemplo por nó (analogia do apartamento); 12:30–16:00 max_depth = 1 e a previsão do nó como a média; 16:00–21:00 max_depth 2 e vários valores (o melhor, 8, não é o mais raso nem o ilimitado); 21:30–26:00 min_samples_leaf; 26:00–27:00 min_samples_split; 27:30–29:00 max_leaf_nodes e min_impurity_decrease.
- **Não cobre:** `splitter`, comparação Gini x entropia, pré x pós-poda pelo nome.
- **Divergências/ressalvas:** exemplo de regressão (MSE por padrão), mas diz que vale também para classificação (26:00); muito código no Colab e um `plot_tree` que trava 5 min; ccp_alpha não explicado; nomes falados em inglês e escritos errado pela legenda.
- **Nível e idioma:** intermediário (com código); português do Brasil.
- **Veredito: `aprovar só 07:00–21:00 e 21:30–29:00`.** Único vídeo em português que trata dos parâmetros do slide 36.

### 7Czuid5o_50 — Daniel Hasan Dalip — Vantagens e Desvantagens (7:09) — `a8-v14` (novo)

- **Cobre:** 00:00–02:30 interpretabilidade (caixa branca) com exemplo de crédito; 02:30–03:00 pouco pré-processamento, sem normalizar; custo de predição baixo; 03:00–03:20 instabilidade (pequenas diferenças geram resultados diferentes); 03:20–04:30 Random Forest; 04:30–05:30 balancear classes; resto bibliografia.
- **Não cobre:** overfitting, variáveis redundantes, valores faltantes e múltiplos rótulos.
- **Veredito: `aprovar só 00:00–03:20`.**

### Vzj0LaHTk80 — Michel Janos — Hiperparâmetros (7:19) — `a8-v15` (novo), opcional

- **Cobre:** 01:00–02:30 max_depth e overfitting/underfitting (erro de treino só cai; baixo demais causa underfitting); 02:30–03:00 max_features, escolha por menor impureza (Gini) ou entropia; 03:00–05:00 vantagens: interpretável, remove preditores irrelevantes, sem normalização, aceita colinearidade, outlier não compromete; 05:00–05:30 instabilidade; 05:30–07:00 treino pode ser caro e as escolhas são gulosas (greedy).
- **Não cobre:** `min_samples_*`, `max_leaf_nodes`, `splitter`.
- **Divergências:** legenda "Max Fitters" = max_features; os últimos 30 s (troco em moedas) são só exemplo de algoritmo guloso.
- **Veredito: `aprovar como opcional`.** É o único que diz "ignora preditores irrelevantes" (slide 44) e "decisão gulosa" (slide 31).

## 3. Descartados e motivo

- **ZrHHJ5owZIo — Fernando dos Santos, "Exercício Entropia e Ganho (Linguagens de Programação)" (a8-v2 antigo; 10:00): descartado.** É só o enunciado de um exercício de aula: monta a estrutura de H(S) e do ganho(S, comercial), diz "preencha o formulário no nosso ambiente" e não calcula nenhuma entropia nem ganho, nem explica o que é entropia. O exemplo tem 3 classes (Delphi, C++, Java), enquanto os slides 19–24 são binários. A ficha antiga dizia que o vídeo "resolve o exercício" e que era o "melhor vídeo em português do Ganho"; era falso.
- **PCTEn3hWDxA — Aprendendo Gestão, "Árvores de Decisão - Exemplo completo com construção e cálculo" (14:26): descartado.** É árvore de decisão de **análise de decisão** (valor esperado, academia amplia ou não), não aprendizado de máquina. Mesmo nome, outro assunto.
- **AALssRaKvEc — Gabriel Spontoni, nó raiz com entropia (6:15): descartado.** Fala corrida e contas confusas (por exemplo, diz que 7 sim e 3 não tem entropia 1; (conhecimento externo) o valor é ≈ 0,88).
- **rOpPW21z55c — Eduardo, Ciência dos Dados, Entropia (2:46): descartado.** Só mostra a ideia de impureza com 5/5 x 9/1 e termina antes de calcular; o v8 cobre o mesmo e mais.
- **BqcGrdMQyk0 — Simplified AI Course, "Decision Tree Regression: Weighted MSE" (11:46, inglês): descartado.** Boa explicação do MSE ponderado, mas está em inglês e sem exemplo numérico; o v11 (pt) cobre o que o slide 32 pede.
- **vW8kk_hMg-Y — Professor Leandro Almeida, Scikit-Learn - Árvores de Decisão (26:42): descartado.** Tutorial de código (Jupyter, Iris); só cita `criterion` e `max_depth` de passagem.
- **XABw4Y3GBR4 — Bhavesh Bhatt, "Decision Tree Hyperparameters" (9:05, inglês): descartado (reserva).** Explica bem max_depth, min_samples_split, min_samples_leaf, max_features e criterion, mas o v13 e o v12 cobrem os mesmos parâmetros em português. Se o usuário quiser rever `criterion` e `max_features` em um vídeo curto, é a reserva.

## 4. Sequência final proposta (ordem dos slides)

1. **a8-v1** (opcional) — analogia de perguntas, instabilidade (slides 3, 5, 6, 12, 45). 00:00–02:50 e 07:23–07:43.
2. **a8-v6** — terminologia (3, 4, 11, 12).
3. **a8-v7** — intuição de entropia (16, 17, 18).
4. **a8-v8** — entropia, fórmula, ganho e exemplo numérico (16–24).
5. **a8-v9** (opcional) — árvore de crédito, ganho e subconjuntos (4, 13, 17–24).
6. **a8-v3** — Gini passo a passo (25–29).
7. **a8-v10** (opcional) — árvore inteira com Gini (3, 4, 12, 25–30, 44).
8. **a8-v4** — numéricos, overfitting, pré-poda (13, 14, 30–37, 43).
9. **a8-v11** — árvore de regressão (31, 32, 34, 36).
10. **a8-v5** — overfitting, poda e cortes (30–35, 41).
11. **a8-v12** — leitura da árvore do sklearn, custo, hiperparâmetros, regressão (4, 25–28, 31–37, 41, 44, 45).
12. **a8-v13** — hiperparâmetros de poda do sklearn (31–37).
13. **a8-v14** — vantagens e desvantagens (44, 45).
14. **a8-v15** (opcional) — max_depth, vantagens, instabilidade, decisão gulosa (31, 34, 36, 44, 45).

Tempo de vídeo (trechos): cerca de 130 min no total, dos quais cerca de 43 min são opcionais; mínimo obrigatório ≈ 87 min.

## 5. Lacunas restantes (cobrir na leitura)

- **Intuição de Gini x entropia** (slide 25: Gini em [0; 0,5] e entropia em [0; 1], Gini mais barato): nenhum vídeo comenta; v10 e v12 dão valores contraditórios ao slide, por isso a leitura deve explicar.
- **`splitter` ("best" ou "random")** e a explicação de `max_features` com exemplo (slide 37): só v12/v15 nomeiam `max_features`; `splitter` não aparece em nenhum vídeo.
- **`min_impurity_decrease` e `max_leaf_nodes`** (slide 36): só uma frase em v13 e v12.
- **Pseudocódigo de indução e os passos de como o sklearn difere (slides 38–42)** e **reuso de atributos binário/categórico (slide 43)**: v4 e v5 mostram o caso contínuo; binário e categórico ficam só na leitura.
- **Pré-poda x pós-poda:** os vídeos usam "poda" nos dois sentidos; a leitura deve dizer que o slide trata de limites durante a construção e que o vídeo v5/v6 descrevem poda depois.
- **Vantagens do slide 44 sem vídeo:** lidar com valores faltantes e múltiplos rótulos; "funcionar imediatamente sem hiperparâmetros complexos".
- **Underfitting por árvore pequena demais** (slide 34): só implícito (v15 e v13 falam de max_depth baixo demais).
