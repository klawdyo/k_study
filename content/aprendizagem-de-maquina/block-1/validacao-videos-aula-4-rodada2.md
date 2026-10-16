# Validação dos vídeos da Aula 4 (Amostragem e validação), rodada 2

Método: li as transcrições inteiras (Whisper "small" ou legenda automática, com erros) de cada candidato, por minuto, e comparei com os 34 slides de `Aulas/Aula 4 - Amostragem de dados` (cache em `estudo/_fontes_extraidas/`). Os `mm:ss` são aproximados (±10 s); os `clips` da proposta usam os segundos de início de frase da transcrição. Nada foi visto no YouTube: desenhos e gráficos só são citados quando a fala os descreve. Os canais de IHAb3NHDahU, PnjkGDeynJo e 1rZpbvSI26c não aparecem na transcrição e ficam "a confirmar". Esta rodada complementa a ficha `validacao-videos-aula-4.md` (rodada 1, vídeos a4-v1 a a4-v7). Proposta de itens: `proposta_aula4.json` (ids a4-v8 a a4-v15; não editei `block.json` nem `progress.json`).

Legenda dos IDs:

| Sigla | ID | Canal / título | Duração | Idioma |
| :-- | :-- | :-- | :-- | :-- |
| IH | IHAb3NHDahU | Intro a Machine Learning, Aula 4 — O que é overfitting e underfitting | 12:34 | pt |
| JL | JlhcxlO18xg | (Mario Filho, pela fala) — Por que nunca fazer scaling antes do split | 07:46 | pt |
| OG | OGpENuxjRWM | Forecasting: Principles & Practice 5.10 — CV em séries temporais | 06:53 | pt (legenda inutilizável) |
| PN | PnjkGDeynJo | AM 03.6 — Experimentação, holdout, validação cruzada, estratificado | 17:51 | pt |
| R5 | R5c8S61balo | Marcelo Carvalho — Separação em treino, validação, teste e reamostragens | 15:12 | pt |
| FJ | FJi23G380b4 | Amostragem estratificada na prática com Python | 09:33 | pt |
| F0 | F0mLg9WQUJo | Paulo Vasconcelos (Data Hackers) — Trade-off viés e variância | 06:13 | pt |
| EU | EuBBz3bI-aA | StatQuest — Machine Learning Fundamentals: Bias and Variance | 06:36 | **en** |
| 1w | 1whfIOoPTlk | Sebastian Raschka — Resampling and Repeated Holdout | 19:27 | **en** |
| 1r | 1rZpbvSI26c | Igor — Cross-Validation for Time Series Forecasting | 10:34 | **en** |

---

## 1. Matriz tópico dos slides × vídeo

Legenda: **B** = cobre bem, **P** = parcial, **—** = não cobre. Só os trechos aprovados contam; o que cobre fora deles vem entre parênteses.

| Tópico (slides) | IH | JL | OG | PN | R5 | FJ | F0 | EU | 1w | 1r |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Poucos dados (4) | — | — | — | — | — | — | — | — | (P: curvas de aprendizado, 00:55–04:15) | — |
| Dados não representativos / viés de amostragem (5–6) | — | — | — | — | P (analogia da sopa) | — | — | — | — | — |
| Baixa qualidade, outliers, atributos irrelevantes (7) | — | — | — | — | — | — | — | — | — | — |
| Generalização (8–9, 14) | P | — | — | — | — | — | P | P | — | P |
| Overfitting: definição e causas (8–10) | B (def.) | — | — | — | — | — | P (modelo complexo, ruído) | P | P (decora com pouco dado) | — |
| Underfitting: definição, causas, soluções (8–9, 11) | B (def.; sem soluções) | — | — | — | — | — | P (causa e remédios) | P | — | — |
| Por que não testar no treino (13–14) | P | — | — | B (resubstituição) | P | — | — | P | — | P |
| Divisão treino / validação / teste (14, 33–34) | — | — | — | P | P | — | — | — | — | — |
| Hold-out: proporções (16) | — | — | — | P (60/40, 50/50, 90/10) | — | — | — | — | P (70/30, 50/50, 90/10) | — |
| Hold-out: crítica da divisão única (17) | — | — | — | P | — | — | — | — | B | — |
| Amostragem aleatória repetida: média e desvio padrão (18–19) | — | — | — | P (só média) | — | — | — | — | P (média e dispersão, sem "desvio padrão") | — |
| k-fold: como funciona (20) | — | — | P | (P: 11:00–13:00) | — | — | — | — | — | P |
| k-fold: média e desvio padrão (20) | — | — | — | (P: só média) | — | — | — | — | — | — |
| k-fold: quando não usar / base grande (21) | — | — | — | — | P | — | — | — | — | — |
| Data leakage: definição (22) | — | P | — | — | — | — | — | — | — | P |
| Vazamento temporal / Time Series Split (23) | — | P (split por tempo) | P (inutilizável) | — | — | — | — | — | — | B |
| Vazamento por duplicação (23) | — | — | — | — | — | — | — | — | — | — |
| Vazamento de atributos (23) | — | — | — | — | — | — | — | — | — | — |
| Vazamento por pré-processamento antes do split (24) | — | B (normalização) | — | — | — | — | — | — | — | — |
| Viés × variância: definição, alvo, 4 combinações (25–28, 31–32) | — | — | — | — | — | — | P (2 combinações) | B (def.; sem alvo) | — | — |
| Curva erro × complexidade, ponto ótimo (29–30) | — | — | — | — | — | — | P | P (sweet spot) | — | — |
| Conjunto de validação e parada antecipada (33–34) | — | — | — | — | P (validação separada) | — | — | — | — | — |
| Estratificação (extra, apoia o k-fold estratificado) | — | — | — | B | — | P (só código) | — | — | — | — |

---

## 2. Fichas por vídeo

### IH — IHAb3NHDahU (12:34, português)

- **O que cobre:**
  - 00:00–02:00: dados em dois eixos; a ideia de ajustar uma curva para prever dados futuros; separar treino (pontos verdes) e teste (pontos vermelhos).
  - 02:00–05:00: três curvas ajustadas só no treino. A reta erra muito; a curva suave passa pelo meio dos pontos; a ondulada passa por todos (erro zero).
  - 05:00–08:00: as mesmas curvas nos dados de teste. A reta segue ruim, a ondulada passa a errar muito e a suave é a melhor. Reforça que não se avalia o modelo só pelo treino.
  - 08:00–09:00: underfitting = a reta (ruim no treino e no teste; "abaixo do desejado").
  - 09:00–10:55: overfitting = a ondulada ("se viciou" no treino, só explica o que já viu).
  - 10:55–12:20: a meta é um modelo generalizável, no meio do caminho; é preciso lutar contra o overfitting.
- **Não cobre:** causas do overfitting além do ajuste excessivo (base pequena, ruído, vazamento), causas e soluções do underfitting (slide 11), conjunto de validação e parada antecipada, viés e variância.
- **Divergências com o slide:**
  - Define os dois termos pela complexidade do modelo, não pelo número de iterações dos slides 8–9; é a ideia do slide 10/11, compatível.
  - A legenda automática escreve "overfiten" para os dois termos; a fala distingue corretamente.
- **Pressupõe conhecimento prévio:** só a noção de treino e teste (vídeo anterior da série). Dá para acompanhar do zero.
- **Foco:** conceito, com desenho (a fala descreve as curvas). Sem código.
- **Qualidade:** a explicação mais clara do conjunto sobre por que a curva "perfeita" no treino é ruim; calmo, didático, algo repetitivo. Melhor que a4-v1 (HP) para a definição de underfitting, que HP trata só como parada precoce.
- **Trechos recomendados:** 00:00–12:22 (inteiro).
- **Veredito: aprovar.** Complementa a4-v1 (HP): este vem antes (o que é overfitting e underfitting); a4-v1 continua necessário para validação e parada antecipada. Proposta: `a4-v9`, depois do slide 10.

### JL — JlhcxlO18xg (07:46, português)

- **O que cobre:**
  - 01:11–03:10: split por tempo (treino no passado, validação no futuro) com o exemplo luminosidade × gasto de energia; o conjunto reservado deve simular dados nunca vistos, nem o x nem o y.
  - 03:10–04:10: se a padronização (subtrair a média e dividir pelo desvio padrão) usar todos os dados, a informação do futuro vaza para o treino.
  - 04:10–05:20: em produção não se conhece o futuro; regra de ouro: tudo que estima um parâmetro com os dados vem **depois** do split.
  - 05:28–06:45: história da fábrica em que uma árvore mudou a luminosidade das fotos e degradou o modelo (mudança de distribuição; fora dos slides).
  - 06:45–07:30: na vida real o x e o y da validação e do teste nunca foram vistos.
- **Não cobre:** imputação, duplicação, vazamento por atributos; o nome "Time Series Split"; estratificação; pipelines.
- **Divergências com o slide:**
  - Chama de "validação" o conjunto que o slide chama de teste (slide 34 é outra coisa).
  - Afirma mais do que o slide: nem num split aleatório se pode contar que o futuro terá a mesma distribuição. A regra final dele é a do slide 24.
- **Pressupõe conhecimento prévio:** pouco; define padronização de passagem.
- **Foco:** conceito, desenho no tablet, sem código.
- **Qualidade:** direto e curto; tom informal e enfático; abertura sobre WhatsApp e curso pago é dispensável.
- **Trechos recomendados:** 01:11–05:20 e 06:45–07:30.
- **Veredito: aprovar só os trechos indicados.** Preenche a lacuna "normalização com estatísticas globais" (slide 24) que a4-v6 (Neoway) deixava aberta, e dá uma noção do split por tempo (slide 23). Proposta: `a4-v13`, depois do slide 24.

### OG — OGpENuxjRWM (06:53, rotulado pt)

- **O que cobre:** (a transcrição é áudio em inglês "traduzido" pelo Whisper para português, quase ininteligível: "sete de treino", "Stretch Sibble", "Stretch Sibble") a ideia de validação cruzada em séries temporais com janela de treino que cresce a cada passo, previsões a 1 passo, erro médio sobre todos os testes e a função `stretch_tsibble` do pacote R `fable`.
- **Não cobre:** a palavra vazamento, a razão de não usar k-fold comum em séries, `TimeSeriesSplit` do scikit-learn.
- **Divergências com o slide:** não dá para verificar com a transcrição atual.
- **Foco:** conceito rápido mais código em R.
- **Veredito: descartar.** Transcrição inutilizável (idioma errado), código em R, não explica o vazamento; 1r cobre o mesmo tópico melhor.

### PN — PnjkGDeynJo (17:51, português)

- **O que cobre:**
  - 00:59–03:35: treino e teste não podem ter interseção; testar na mesma base de treino (resubstituição) dá estimativa muito otimista, o modelo "decora"; testar com dados futuros serve para monitorar degradação, por isso se usam dados passados.
  - 04:02–05:05: hold-out = deixa um pedaço de fora para teste (40%) e o resto para treino; pode ser aleatório e repetido várias vezes, medindo acurácia, erro, precisão em cada repetição; 50/50 ou 90/10 "tanto faz".
  - 05:05–06:05: qual das taxas repetidas é a correta? Na prática usa-se a média, que mesmo assim pode não coincidir com o desempenho real (promete falar de intervalo de confiança na próxima aula).
  - 06:05–10:20: amostragem completamente aleatória × estratificada; com teste pequeno, o sorteio pode distorcer a proporção das classes; exemplo com 44/20/36% e os percentuais de cada método.
  - 10:20–11:00: base desbalanceada: pode-se descartar exemplos para igualar classes (extra).
  - 11:00–13:00: k-fold com 3 partições, 10-fold é comum; média das taxas ou matriz de confusão da base inteira; repetição aleatória.
  - 13:00–14:00: estratificação no k-fold com teste muito pequeno.
  - 14:00–16:10: leave-one-out e bootstrap (fora dos slides).
- **Não cobre:** desvio padrão, a crítica do slide 19 (testes repetidos podem se parecer), quando não usar k-fold (slide 21), proporção 80/20, overfitting, leakage.
- **Divergências com o slide:**
  - Só "média", sem desvio padrão (slide 18 e 20).
  - Proporções 60/40, 50/50, 90/10, em vez de 2/3–1/3 ou 80/20 (não é contradição).
  - Estratificação, bootstrap e leave-one-out não estão nos slides: material extra.
- **Pressupõe conhecimento prévio:** sim, matriz de confusão e métricas de aula anterior.
- **Foco:** conceito, com exemplos numéricos e slides; sem código.
- **Qualidade:** aula expositiva de pós-graduação, com digressões; trechos indicados claros. Legenda com erros ("re-substituição" aparece como "resto substituição").
- **Trechos recomendados:** 00:59–03:35, 04:02–05:05, 05:30–10:30.
- **Veredito: aprovar só os trechos indicados.** Único em português que fala em hold-out repetido com média (slide 18) e em estratificação. Complementa a4-v2, a4-v3 (hold-out) e a4-v5 (k-fold); substitui a lacuna 4 da rodada 1 só em parte (falta desvio padrão e a crítica do slide 19). Proposta: `a4-v10`, depois do slide 13.

### R5 — R5c8S61balo (15:12, português)

- **O que cobre:**
  - 00:24–02:05: por que usar uma amostra em vez da população inteira; ela precisa ser representativa e aleatória (analogia: provar uma colher de sopa depois de mexer a panela).
  - 02:05–03:55: tipos de análise (descritiva, inferencial, preditiva) e experimento planejado × retrospectivo (adubo e semente; fora do foco).
  - 03:55–05:00: treino e teste pela analogia da tabuada e da prova guardada na gaveta.
  - 05:00–11:55: reamostragens (validação cruzada, bootstrap, rolling origin), parâmetros × hiperparâmetros com a máquina de sorvete, learning rate.
  - 11:55–13:10: validação cruzada serve com dados limitados e treino barato; com volume enorme (deep learning) é cara e se usa um conjunto de validação separado.
  - 13:10–14:35: número de GPUs e custo de US$ 2 milhões citados sem fonte; validação para ajustar hiperparâmetros, teste só no fim.
- **Não cobre:** "viés de amostragem" pelo nome nem exemplo de amostragem falha (slides 5 e 6), poucos dados, qualidade dos dados, overfitting e underfitting, hold-out e proporções, k-fold passo a passo, desvio padrão, leakage, bias e variância, parada antecipada.
- **Divergências com o slide:** usa "validation set" como terceira partição separada (o slide 34 diz que é subconjunto do treino; na prática é a mesma ideia). O trecho da sopa fala de um estudo descritivo, não de treino de modelo.
- **Pressupõe conhecimento prévio:** pouco; vídeo muito amplo.
- **Foco:** conceito com analogias e desenhos; sem código.
- **Qualidade:** informal e com muitas digressões. A analogia da sopa é boa; o resto do vídeo foge do foco.
- **Trechos recomendados:** 00:24–02:05 e 11:55–13:10.
- **Veredito: aprovar só esses dois trechos, como complemento opcional e fraco.** Não fecha a lacuna "dados não representativos": só dá a analogia da representatividade. Proposta: `a4-v8`, depois do slide 5, `optional: true`.

### FJ — FJi23G380b4 (09:33, português)

- **O que cobre:** implementação de amostragem estratificada com `StratifiedShuffleSplit` do scikit-learn, no dataset de renda (`income`), checando que a amostra de 100 registros mantém 76/24%.
- **Não cobre:** por que estratificar (só um parágrafo), relação com treino/teste, k-fold.
- **Divergências com o slide:** afirma que numa amostra aleatória de 100 pessoas "a probabilidade é muito grande" de pegar só quem ganha menos de 50 mil; com 24% da classe positiva isso é muito improvável, então a justificativa está exagerada. Usa a função para tirar uma amostra de 100, não para dividir treino e teste.
- **Pressupõe conhecimento prévio:** sim, pandas, aula teórica anterior da série.
- **Foco:** código.
- **Veredito: descartar.** É tutorial de código com justificativa fraca; PN explica melhor a estratificação, com exemplo.

### F0 — F0mLg9WQUJo (06:13, português)

- **O que cobre:**
  - 00:40–01:03: erro de generalização: ir bem em dados que o modelo não viu.
  - 01:03–01:44: três erros (variância, viés, erro de Bayes ou irredutível); Bayes é citado e deixado de lado.
  - 01:44–02:00: viés = limitação do modelo (rígido demais para captar o sinal real); variância = sensibilidade ao conjunto de treino.
  - 02:00–04:00: modelos simples (regressão linear e logística) têm viés alto e variância baixa; modelos complexos (árvores, KNN) têm variância alta, viés baixo, modelam o ruído e memorizam, com bom resultado no treino e ruim no teste.
  - 04:00–05:00: viés alto e variância baixa = underfitting (ex.: modelo linear em dados sem relação linear).
  - 05:00–05:35: formas de equilibrar: regularização, poda, profundidade da árvore, hiperparâmetros, trocar de algoritmo.
- **Não cobre:** alvo com as quatro combinações (só duas), gráfico erro × complexidade, outras causas do underfitting (atributos insuficientes, pré-processamento, pouco tempo de treino), hold-out, validação cruzada, leakage.
- **Divergências com o slide:**
  - Definições de viés e variância em palavras diferentes das do slide 27 (viés = erro no treino; variância = amplitude dos erros); compatíveis.
  - Em 05:15 diz "simples demais para ele overfitar", lapso de fala por "underfitar".
  - A associação modelo → viés/variância é tendência geral e depende dos hiperparâmetros.
- **Pressupõe conhecimento prévio:** sim, termos como overfitting e modelo supervisionado.
- **Foco:** conceito, sem desenho nem código.
- **Qualidade:** estilo "pergunta de entrevista", informal e rápido; legenda com erros ("chinl", "IP parâmetros").
- **Trechos recomendados:** 00:40–01:03 e 01:44–05:35.
- **Veredito: aprovar só os trechos indicados, como complemento opcional de a4-v7.** Acrescenta quais modelos tendem a cada caso e os remédios; cobre só parte da lacuna de causas e soluções. Proposta: `a4-v15`, depois do slide 28.

### EU — EuBBz3bI-aA (06:36, inglês)

- **O que cobre:**
  - 00:28–01:05: altura de camundongos pelo peso; a relação real é uma curva.
  - 01:05–02:00: divide em treino e teste; regressão linear ajusta uma reta no treino.
  - 02:00–03:00: viés = incapacidade do método de capturar a relação verdadeira (a reta nunca curva); a ondulada tem viés baixo.
  - 03:00–04:00: soma dos quadrados dos erros: a ondulada vence no treino (erro zero) e perde no teste.
  - 04:00–05:00: variância = diferença de ajuste entre conjuntos; a ondulada tem variância alta, a reta variância baixa ("boas, não ótimas, mas consistentes").
  - 05:00–05:50: a ondulada está em overfitting; o ideal é viés baixo e variância baixa, no ponto entre modelo simples e complexo.
  - 05:48–06:05: cita regularização, boosting e bagging, sem explicar.
- **Não cobre:** o alvo e as quatro combinações (slides 28 e 31), relação "viés alto = underfitting" pelo nome, gráfico de erro × complexidade (slides 29 e 30), ruído (slide 30).
- **Divergências com o slide:** viés e variância definidos pela capacidade do método e pela diferença de ajuste entre conjuntos, e não por "erro sobre o treino" e "amplitude dos erros" (slide 27); compatíveis. Regularização, boosting e bagging estão fora dos slides.
- **Pressupõe conhecimento prévio:** nenhum; soma dos quadrados é explicada em 20 s.
- **Foco:** conceito com gráficos e animação; sem código.
- **Qualidade:** excelente, claro e curto; mas em inglês e não substitui a4-v7, que cobre alvo e curva de erro.
- **Trechos recomendados:** 00:28–06:08.
- **Veredito: aprovar, como complemento opcional em inglês de a4-v7** (segunda explicação curta). Proposta: `a4-v14`, depois do slide 25.

### 1w — 1whfIOoPTlk (19:27, inglês)

- **O que cobre:**
  - 00:00–08:20: curvas de aprendizado (acurácia × tamanho do treino): com pouco dado o modelo decora (treino alto), com mais dado o teste melhora; viés pessimista por reservar teste; coletar mais dados pode ajudar (liga com "poucos dados" e "base muito pequena", mas em nível avançado e usando o teste repetido).
  - 08:20–09:00: reservar muito dado para teste prejudica o treino; reduzir o teste é uma solução, mas gera outro problema.
  - 09:00–11:40: com teste pequeno a estimativa varia muito (exemplo de amostras de uma distribuição em 70/30, três vezes).
  - 11:40–13:30: hold-out repetido k vezes e média = Monte Carlo cross-validation; mostra a sensibilidade do modelo à divisão.
  - 13:30–17:00: simulação com Iris e KNN: 50 repetições com 50/50 e com 90/10; acurácia varia de 88% a 100% e de 80% a 100%; média de cerca de 95%; teste menor, mais variação.
  - 17:00–19:00: código da simulação.
- **Não cobre:** desvio padrão pelo nome, a crítica do slide 19, k-fold, estratificação, leakage.
- **Divergências com o slide:** mostra dispersão por mínimo e máximo, e fala "média"; não menciona desvio padrão. Usa "variância" para a variação da estimativa. Menciona viés pessimista e bagging (fora dos slides).
- **Pressupõe conhecimento prévio:** sim, hold-out, acurácia e a ideia de viés/variância do alvo.
- **Foco:** conceito com gráficos, simulação e um pouco de código.
- **Qualidade:** aula universitária clara, em inglês; vídeo longo com muita coisa fora do foco.
- **Trechos recomendados:** 08:20–17:10.
- **Veredito: aprovar só esse trecho, como complemento opcional em inglês de PN.** É o que melhor mostra por que o desvio alto significa instabilidade (slides 17 e 18), mesmo sem dizer "desvio padrão". Proposta: `a4-v11`, depois do slide 17.

### 1r — 1rZpbvSI26c (10:34, inglês)

- **O que cobre:**
  - 00:00–02:00: o que é validação cruzada.
  - 02:00–03:50: visualização das divisões, treino e teste mudando de posição.
  - 03:50–05:00: em séries temporais isso é um problema: treinar com dados posteriores e testar em anteriores usa o futuro para prever o passado; informação vazando do teste para o treino.
  - 05:00–06:10: solução: o teste sempre depois do treino; o treino cresce a cada divisão e o teste avança.
  - 06:10–09:15: exemplo com suavização exponencial (Holt-Winters) e `TimeSeriesSplit` do scikit-learn para ajustar um hiperparâmetro; código.
  - 09:28–10:25: resumo: validação cruzada comum vaza; usar `TimeSeriesSplit`; "o conjunto de teste sempre à frente do de treino".
- **Não cobre:** duplicação, vazamento por atributos, pré-processamento com estatísticas globais, média e desvio padrão da validação cruzada.
- **Divergências com o slide:**
  - Chama de "rolling" o esquema em que a janela de treino cresce; o `TimeSeriesSplit` do scikit-learn faz isso por padrão. A regra é a do slide 23.
  - Erros de legenda ("hop-ramps" = hiperparâmetros).
- **Pressupõe conhecimento prévio:** sim, validação cruzada (slide 20).
- **Foco:** conceito com gráficos nos primeiros 6 minutos; depois código.
- **Qualidade:** claro e objetivo, mas em inglês e com muito código na segunda metade.
- **Trechos recomendados:** 01:58–06:07 e 09:28–10:25.
- **Veredito: aprovar só os trechos indicados (inglês).** É o único vídeo com explicação visual do Time Series Split, que era lacuna completa. Proposta: `a4-v12`, depois do slide 23.

---

## 3. Descartados

| Vídeo | Motivo |
| :-- | :-- |
| OGpENuxjRWM (CV em séries temporais, Hyndman) | Transcrição inutilizável (áudio em inglês transcrito como português, quase ininteligível); código em R; não menciona vazamento. 1r cobre o tópico. |
| FJi23G380b4 (amostragem estratificada em Python) | Tutorial de código; justificativa exagerada (diz que a amostra aleatória quase certamente pega só uma classe); usa a função para uma amostra de 100, não para treino e teste. PN explica melhor. |

---

## 4. Lacunas restantes (tópicos que continuam sem vídeo bom; o material escrito deve cobrir)

Verificação dos tópicos que eram lacuna na rodada 1:

1. **Desvio padrão no k-fold e na amostragem aleatória repetida (slides 18–20): continua sem vídeo.** Nenhum dos 10 candidatos diz "desvio padrão". 1w mostra a dispersão (mínimo e máximo) e a ideia de instabilidade; PN dá a repetição e a média. A leitura deve explicar que o desvio padrão mede essa dispersão e que desvio alto = modelo instável. Continua sem vídeo também a **crítica do slide 19** (os conjuntos sorteados podem se repetir).
2. **Estratificação: coberta** por PN (06:05–10:20) e, na rodada 1, por BN e FS. Não está nos slides; é extra.
3. **Vazamento com pré-processamento global: coberto.** JL mostra a normalização (média e desvio do dataset inteiro) e NW (a4-v6) a imputação.
4. **Validação em série temporal: coberta só em inglês** (1r), com complemento parcial em JL. Sem vídeo em português com o nome "Time Series Split".
5. **Dados não representativos e viés de amostragem (slides 5–6): continua sem vídeo bom.** R5 dá só a analogia da amostra representativa; o conceito de viés de amostragem e o exemplo da desnutrição rural ficam no texto.
6. **Causas de overfitting e underfitting (slides 10 e 11): parcial.** IH define os dois; F0 e EU citam complexidade e ruído; 1w liga base pequena a decorar (em inglês, fora do clip). Continuam sem vídeo as causas "atributos insuficientes", "pré-processamento inadequado", "tempo de treino insuficiente" (só HP fala em parar cedo) e as três soluções do slide 11 (modelo mais poderoso, melhores atributos, ajustar hiperparâmetros), só parcialmente em F0.
7. **Poucos dados (slide 4), baixa qualidade, outliers e atributos irrelevantes (slide 7): continuam sem vídeo.** Os tópicos de pré-processamento têm vídeos na Aula 3 (a3-v1, a3-v2, a3-v6); referenciá-los na leitura.
8. **Ainda sem vídeo:** vazamento por duplicação e por atributos além do que NW (a4-v6) e CM (rodada 1) já dão; a **crítica ao k-fold em bases grandes** só em BN (rodada 1); o alvo de viés e variância do slide 31 só em AV (a4-v7).
9. **Divergências de definição a registrar no texto (para a prova):** viés e variância (slide 27: erro no treino e amplitude dos erros × EU e F0: capacidade do método e sensibilidade ao conjunto); "validação" como terceira partição separada (R5) × subconjunto do treino (slide 34); proporções do hold-out 60/40 e 90/10 (PN, 1w) × 2/3–1/3 e 80/20 (slide 16).
