# Validação dos vídeos da Aula 4 (Amostragem e validação) pela transcrição

Método: li as transcrições (legendas automáticas, com erros de reconhecimento) de cada vídeo e comparei com os 34 slides de `Aulas/Aula 4 - Amostragem de dados` (cache em `estudo/_fontes_extraidas/`). Os timestamps `mm:ss` são aproximados (±10 s) porque a legenda é automática. Nada foi visto no YouTube; imagens e desenhos que o vídeo mostra não aparecem na transcrição, então "usa desenho" só é afirmado quando a fala indica isso.

Legenda dos IDs:

| Sigla | ID | Canal / título | Duração | Idioma |
| :-- | :-- | :-- | :-- | :-- |
| HP | _XJTjJ0ZFFE | Hemerson Pistori — Aula IA 04: generalização, treino/validação/teste, sobreajuste | 11:02 | pt |
| AV | --NWR_1uIW0 | Apoena Stack — Viés e variância | 15:11 | pt |
| AC | CWxaXyXZ-1A | Apoena Stack — Validação cruzada | 27:04 | pt |
| NW | cauYnbfiayU | Neoway Labs Tech — Data Leakage | 27:15 | pt |
| BN | 8qTkdC_ccdY | Bruno Nogueira — Holdout × k-fold | 47:26 | pt |
| FS | E1VAYcKnLxg | Fernando dos Santos — Validação cruzada K-fold | 09:32 | pt |
| CM | 2NUCXJ3BHiU | codeManS — Vazamento de dados (Kaggle) | 25:25 | **en** |
| (FS-HO) | VZSZGCmKj-o | Fernando dos Santos — Hold-out | sem transcrição | — |

O vídeo de hold-out de Fernando dos Santos (VZSZGCmKj-o) não tem transcrição: **não foi avaliado**; o usuário vai validá-lo assistindo.

---

## 1. Matriz tópico dos slides × vídeo

Legenda: **B** = cobre bem, **P** = parcial, **—** = não cobre.

| Tópico (slides) | HP | AV | AC | NW | BN | FS | CM |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Poucos dados como desafio (4) | — | — | — | — | — | — | — |
| Dados não representativos / viés de amostragem (5–6) | P | — | — | — | — | — | — |
| Baixa qualidade, outliers, ruído; atributos irrelevantes (7) | — | — | P (só seleção de atributos via CV) | — | — | — | — |
| Generalização (8–9, 14) | B | P | P | — | P | — | — |
| Overfitting: definição e causas (8–10) | B | B | — | — | — | — | — |
| Underfitting: definição, causas, soluções (8–9, 11) | P | P | — | — | — | — | — |
| Por que não testar nos dados de treino (13–14) | B | — | P | P | B | — | — |
| Divisão treino / validação / teste (14, 33–34) | B | — | — | P | — | — | P |
| Hold-out: o que é e proporções (16) | P | — | P | — | B | — | — |
| Hold-out: crítica (uma só divisão, teste "fácil") (17) | B | — | B | — | P | P | — |
| Amostragem aleatória repetida, média e desvio padrão (18–19) | P | — | — | — | — | — | — |
| k-fold: como funciona (20) | P (só cita) | — | B | — | B | B | — |
| k-fold: métrica = média e desvio padrão (20) | — | — | P (só média) | — | P (soma as matrizes; cita variância alta entre folds) | P (só média) | — |
| k-fold: quando não usar / base grande (21) | — | — | — | — | B (com ressalva, ver ficha) | — | — |
| Data leakage: definição (22) | — | — | — | B | — | — | B |
| Leakage temporal / Time Series Split (23) | — | — | — | — | — | — | — |
| Leakage por duplicação (23) | — | — | — | B | — | — | — |
| Leakage de atributos (target leakage) (23) | — | — | — | B | — | — | B |
| Leakage no pré-processamento antes de dividir (24) | — | — | — | B | — | — | P |
| Viés × variância: definição, alvo, 4 combinações (25–28, 31–32) | — | B | — | — | — | — | — |
| Curva erro × complexidade, ponto ótimo (29–30) | — | B | — | — | — | — | — |
| Conjunto de validação e parada antecipada (33–34) | B | — | — | — | — | — | — |

---

## 2. Fichas por vídeo

### HP — _XJTjJ0ZFFE (Hemerson Pistori, 11:02)

- **O que cobre:**
  - 00:40–01:40: o que é uma época (epoch) e como a perda (loss) cai no treino.
  - 01:40–02:40: o problema central é generalizar, não ficar bom só no treino.
  - 02:40–05:30: conjunto de validação separado; a perda de validação começa a piorar na época 60 enquanto a de treino continua caindo. Compara guardar os pesos da época 60 (perda de validação 8) com os da época 80 (treino ótimo, validação 9).
  - 05:00–05:40: definição de overfitting ("decora o conjunto de treino").
  - 05:40–06:50: o conjunto de validação já foi "usado para decidir" (época de parada), então perde valor como medida honesta; por isso um terceiro conjunto de teste, intocado até o fim.
  - 06:50–08:40: amostragem aleatória para montar os três conjuntos; exemplo de contar bois em imagens de drone (as primeiras imagens de uma só fazenda não representam o problema); coletar dados variados.
  - 08:20–10:00: um conjunto de teste pode ser "fácil" por sorte; embaralhar e repetir, citando validação cruzada ou reamostragem; algoritmos estocásticos dão resultados diferentes.
  - 10:00–10:50: underfitting como parar o treino cedo demais (treino e validação longe do ideal).
- **Não cobre:** poucos dados, qualidade dos dados/atributos, causas de overfitting além do excesso de treino, soluções de underfitting, proporções do hold-out, média e desvio padrão, k-fold (só cita), bias/variância, leakage. Não nomeia "viés de amostragem", apenas descreve a ideia.
- **Divergências com o slide:**
  - Define overfitting/underfitting só pelo tempo de treino (épocas). Isso é compatível com os slides 8–9, mas **não** com o slide 11 (underfitting = modelo simples demais, soluções: modelo mais poderoso, melhores atributos, hiperparâmetros). Complementar com o material escrito.
  - 09:40 cita "validação cruzada ou reamostragem com reposição" de forma vaga; "com reposição" não está nos slides e pode confundir.
  - Não diz que a validação é "subconjunto do treino" (slide 34), mas o uso descrito (parada antecipada) é o mesmo.
- **Pressupõe conhecimento prévio:** sim, a aula anterior (rede neural, perda, pesos, função de perda). O recap de 00:00–00:40 é de rede neural; a partir de 00:40 dá para acompanhar sem ter visto.
- **Foco:** conceito (com um gráfico de perda por época, que a fala descreve). Sem código.
- **Qualidade:** didático e curto, bom para iniciante em engenharia de software (usa o exemplo do drone/bois); informal; um tanto centrado em redes neurais.
- **Trechos recomendados:** 00:40–10:50 (10:10), que cobre slides 8–11, 13–14, parte de 17–19 e 33–34.
- **Veredito: aprovar** (como visão geral inicial; é o único que cobre bem validação/parada antecipada).

### AV — --NWR_1uIW0 (Apoena Stack, Viés e variância, 15:11)

- **O que cobre:**
  - 00:20–03:30: três modelos (H1 ajuste razoável, H2 reta muito simples, H3 passa por todos os pontos) sobre os dados de treino; erro de treino de H3 quase nulo.
  - 02:30–04:00: bias (viés) como incapacidade do modelo de capturar a relação real; H2 alto, H1 médio, H3 baixo (sempre olhando o treino).
  - 04:00–06:00: base de teste diferente; H3 passa a errar muito.
  - 06:00–07:00: variância como consistência quando se troca o conjunto de dados.
  - 07:00–09:00: H3 = overfitting (baixo bias no treino, alta variância); H2 = underfitting (alto bias, baixa variância).
  - 09:00–12:30: gráfico erro de predição × complexidade, curvas de treino e teste; extremo de alta complexidade (treino baixo, teste alto); ponto médio ideal.
  - 12:30–14:00: analogia do alvo (dartboard), as quatro combinações de bias/variância; o ideal é baixo bias e baixa variância.
  - 14:00–14:30: cita três técnicas para reduzir (regularização e, pela legenda confusa, bagging e boosting), sem explicar.
- **Não cobre:** tudo que não é bias/variância e overfitting/underfitting (amostragem, hold-out, validação cruzada, leakage). Causas de overfitting só aparecem como "complexidade excessiva"; sem lista de soluções do slide 11.
- **Divergências com o slide:**
  - Define variância como "consistência entre bases de dados"; o slide 27 diz "amplitude dos erros / variabilidade das predições". As duas ideias são compatíveis, mas as palavras diferem.
  - Define bias sempre olhando para a base de treino, igual ao slide 27 ("erro sobre os dados de treino"). Em textos de referência, o viés é mais geral; o material escrito deve registrar as duas versões.
  - A fala "alto bias e alta variância" na analogia do alvo (12:30–13:00) é correta, mas a legenda embaralha a ordem das combinações; atenção ao assistir.
- **Pressupõe conhecimento prévio:** pouco; assume saber o que são base de treino e de teste, regressão polinomial/linear só como nome.
- **Foco:** conceito (usa desenhos: curvas H1/H2/H3, gráfico erro × complexidade, alvo).
- **Qualidade:** a melhor explicação de bias/variância do conjunto; para iniciantes; ritmo calmo, algo repetitivo.
- **Trechos recomendados:** 00:20–14:00 (13:40).
- **Veredito: aprovar.**

### AC — CWxaXyXZ-1A (Apoena Stack, Validação cruzada, 27:04)

- **O que cobre:**
  - 00:30–02:00: divisão 75% treino / 25% teste, analogia estudo (apostila) × prova.
  - 02:00–04:00: crítica ao hold-out: com um único bloco de 25% o teste pode favorecer um modelo por acaso, gerando viés na escolha; não dá para usar todo o dataset para treino e teste.
  - 04:00–08:30: k-fold com 4 blocos de 25%, treinar e testar 4 vezes variando o bloco de teste, média das acurácias; pseudocódigo em "Portugol"; o modelo é refeito do zero em cada rodada.
  - 08:30–10:35: o k é livre (5, 10...), 10-fold é o mais comum; a média reduz o efeito de um bloco "sortudo" (exemplo 90% em um fold contra 60% nos outros).
  - 10:35–12:00: usos da validação cruzada: escolher modelo, escolher atributos, escolher hiperparâmetros.
  - 12:00–27:00: código scikit-learn num notebook (aluguel de imóveis; `KFold`, `cross_val_score`, regressão linear, Lasso, KNN com k de 1 a 20).
- **Não cobre:** desvio padrão (só fala em média), quando não usar (base grande), amostragem aleatória repetida, estratificação, nem leakage. Do hold-out, só 75/25 (sem 2/3–1/3 nem 80/20).
- **Divergências com o slide:**
  - 07:30 diz que o k-fold "considera todas as combinações possíveis" de dividir a base; isso é impreciso (são k partições fixas, não todas as combinações).
  - Só média, sem desvio padrão (slide 20 exige média e desvio).
  - Usa a validação cruzada para selecionar modelo/atributos/hiperparâmetros, tema que o slide não traz (extra, útil).
  - Em 09:00 fala em "menor variância" ao tirar a média; o termo é usado de forma informal.
- **Pressupõe conhecimento prévio:** a parte teórica (até ~12:00) quase nada; a prática (12:00 em diante) assume Python/pandas, regressão linear e conceitos de vídeos anteriores da série.
- **Foco:** conceito até 12:00; código depois.
- **Qualidade:** analogias boas (estudo × prova, exemplo numérico do fold sortudo); informal e redundante; ritmo lento no código. Para iniciante, a parte teórica é boa.
- **Trechos recomendados:** 02:00–04:00 (crítica do hold-out) e 08:30–10:35 (k livre, vantagem da média). O código (12:00–27:00) é opcional e fora do foco da prova.
- **Veredito: aprovar só os trechos 02:00–04:00 e 08:30–10:35** (a parte conceitual 04:00–08:30 repete o que FS explica melhor e mais curto).

### NW — cauYnbfiayU (Neoway Labs Tech, Data Leakage, 27:15)

- **O que cobre:**
  - 02:30–03:40: definição: usar na modelagem informação que não estará disponível na hora da predição; métricas de teste excelentes, desempenho ruim em produção.
  - 07:00–11:16: dividir em treino e teste; analogia professor/lista de exercícios/prova (a prova não repete as perguntas).
  - 11:16–14:30: leakage no pré-processamento: preencher valores faltantes no dataset inteiro antes de dividir leva informação para o teste (comparado a pôr questão da lista na prova).
  - 14:30–15:50: leakage de atributo: colocar a própria variável resposta como atributo.
  - 15:50–17:10: leakage de atributos "do futuro" (exemplo: cirurgia relacionada à doença que se quer prever, não disponível na hora de usar o modelo).
  - 17:30–19:20: relato de experimento: imputar com KNN antes de separar treino e teste faz as métricas enganarem.
  - 19:20–20:50: duplicados (exemplo: CNPJ repetido caindo em treino e teste; pego com teste unitário).
  - 21:00–23:00: dicas: separar treino e teste sem interseção; dividir antes de qualquer manipulação (imputação); análise exploratória para achar atributos muito correlacionados ao alvo; atenção ao que existe no mundo real.
  - 25:00–26:30: usar pipelines (`PyCaret`, `scikit-learn`).
- **Não cobre:** leakage temporal / `Time Series Split` (só diz em 23:00–24:00 "se a aplicação depende do tempo, não use atributos coletados após o evento", sem falar em divisão temporal); normalização com estatísticas globais (cita só imputação); exemplo de pneumonia do slide.
- **Divergências com o slide:**
  - Não nomeia "vazamento temporal" nem "Time Series Split" (slide 23).
  - 24:00–25:00 chama de "conjunto de validação" um terceiro conjunto para simular produção, usando a palavra de modo diferente do slide 34 (validação durante o treino). Pode confundir; cuidado.
  - Os tipos aparecem como relatos soltos, sem a taxonomia do slide (temporal, duplicação, atributos, pré-processamento).
- **Pressupõe conhecimento prévio:** pouco; linguagem de dia a dia de ciência de dados; vários termos ("pipeline", "features", "imputação") são usados sem definir.
- **Foco:** conceito, com exemplos práticos (sem código).
- **Qualidade:** formato de mesa-redonda com três cientistas de dados; informal, repete o ponto algumas vezes (apresentações e conversa nos 7 minutos iniciais são dispensáveis). Fortes: exemplos de duplicação e de imputação, ligação com testes unitários (familiar a um engenheiro de software).
- **Trechos recomendados:** 02:30–03:40, 11:16–17:10, 19:20–20:50, 21:00–22:50 (total ≈ 10:25). Opcional: 17:30–19:20 (KNN).
- **Veredito: aprovar só os trechos listados** (é o melhor disponível em português para slides 22–24, mas incompleto no temporal).

### BN — 8qTkdC_ccdY (Bruno Nogueira, Holdout × k-fold, 47:26)

- **O que cobre:**
  - 00:30–05:30: medir o desempenho em dados não vistos; analogia da prova com consulta (04:30); notação f(x), h(x), classe predita × real.
  - 05:50–09:00: hold-out: separar aleatoriamente uma porção para teste (3/4–1/4; "o mais comum na literatura" 2/3–1/3).
  - 09:00–16:00: k-fold: dividir em k partes disjuntas, repetir k vezes com um fold de teste; k-fold estratificado mantendo 60/40 das classes; mesmo algoritmo com os mesmos parâmetros em cada rodada.
  - 16:00–40:00: exemplo numérico com 10 pacientes: hold-out e k=3, matrizes de confusão, acurácia, precisão e revocação (cálculo manual).
  - 40:00–41:50: validação cruzada em geral é preferível ao hold-out (estimativa estatisticamente menos enviesada, vários cenários); a variância entre folds pode ser alta (exemplo 20% em um fold e 100% em outro); a média dá segurança.
  - 42:17–43:45: o hold-out é suficiente em base muito grande (1 milhão de exemplos, 10% = 100 mil de teste já capturam a variabilidade).
  - 45:30–47:26: fecho: a estimativa serve para prometer ao cliente o desempenho esperado.
- **Não cobre:** overfitting/underfitting (só cita rapidamente em 18:00 que avaliar no treino "favorece o sobreajuste"), amostragem aleatória repetida, desvio padrão, leakage, bias/variância, desafios dos dados.
- **Divergências com o slide:**
  - 41:51–42:17 diz que o hold-out é "mais indicado" quando há **muito poucos dados** porque os subconjuntos ficam pequenos. O slide 21 diz o contrário: validação cruzada serve para bases pequenas; hold-out basta em bases grandes. A segunda metade (base muito grande) está de acordo com o slide. **Pular esse trecho.**
  - Consolida as métricas **somando as matrizes de confusão de todos os folds** (36:30–39:00), enquanto o slide 20 pede média e desvio padrão por fold. Ele menciona a variância entre folds (41:12), mas não calcula desvio padrão.
  - Adiciona estratificação (não está nos slides; extra útil).
- **Pressupõe conhecimento prévio:** sim, o vídeo anterior sobre métricas (matriz de confusão, acurácia, precisão, revocação); notação de h(x) e f(x).
- **Foco:** conceito, com exemplo numérico à mão (sem código).
- **Qualidade:** aula expositiva clara e bem estruturada; usa desenho (quadro) e exemplo; o trecho 16:00–40:00 é longo e gira em torno de matriz de confusão, que o usuário disse não ser foco.
- **Trechos recomendados:** 05:50–09:00 (hold-out), 40:00–41:50 e 42:17–43:45 (k-fold vs. hold-out e base grande). Opcional: 09:00–16:00 se quiser uma segunda explicação de k-fold e da estratificação.
- **Veredito: aprovar só os trechos 05:50–09:00, 40:00–41:50 e 42:17–43:45.** O restante é redundante ou fora do foco.

### FS — E1VAYcKnLxg (Fernando dos Santos, Validação cruzada K-fold, 09:32)

- **O que cobre:**
  - 00:00–00:40: o k-fold resolve a deficiência do hold-out.
  - 00:20–04:20: k = número de subconjuntos (folds); exemplo de 90 exemplos com k = 3 (30 por fold); divisão estratificada (mantém a proporção das classes); k treinos/testes alternando o fold de teste; k matrizes de confusão; média das métricas (acurácia, precisão, revocação); o modelo é reiniciado do zero a cada rodada (04:20).
  - 04:40–07:20: exemplo com 9 exemplos (Iris: setosa/versicolor) mostrando como montar folds A, B, C com proporção 33%/66%.
  - 07:20–09:32: as três rodadas (A+B treino e C teste, etc.) e média final; fecho: "diminuir o risco de deixar alguém de fora do treino ou do teste" do hold-out.
- **Não cobre:** desvio padrão, quando não usar (base grande), custo computacional, amostragem aleatória repetida.
- **Divergências com o slide:** nenhuma de conteúdo; só "média" (sem desvio padrão).
- **Pressupõe conhecimento prévio:** começa com "essas outras validações..." (continuação de um vídeo anterior, provavelmente o de hold-out de FS-HO); assume saber matriz de confusão e métricas de classificação.
- **Foco:** conceito, com exemplo numérico simples.
- **Qualidade:** curto, passo a passo, bom para iniciante; sem enrolação.
- **Trechos recomendados:** 00:00–09:32 (inteiro).
- **Veredito: aprovar.**

### CM — 2NUCXJ3BHiU (codeManS, Vazamento de dados Kaggle, 25:25) — idioma: **inglês**

- **O que cobre:**
  - 01:30–02:30: definição de leakage (dados de treino com informação sobre o alvo que não existirá na hora da predição).
  - 02:30–07:15: dois tipos: *target leakage* (exemplo de pneumonia e antibiótico: variável criada depois do evento; excluir variáveis atualizadas ou criadas após o alvo) e *train-test contamination*.
  - 07:30–09:30: contaminação por pré-processamento (ajustar um imputer antes do `train_test_split`).
  - 12:00–13:00: usar pipelines do scikit-learn; mais crítico em validação cruzada.
  - 13:00–22:30: exemplo de cartão de crédito: acurácia de 98% na validação cruzada é suspeita; identificar e remover preditores vazados (acurácia cai para 83%, realista).
- **Não cobre:** leakage temporal/Time Series Split, duplicação, normalização.
- **Divergências com o slide:**
  - Usa "validation" e "test" de modo intercambiável (o texto Kaggle trata "validation" como o conjunto de avaliação); não separa do conjunto de validação do slide 34.
  - O exemplo de pneumonia/antibiótico é o **mesmo do slide 23** (provavelmente o slide veio do texto de Kaggle), mas a explicação do vídeo tem pouco acréscimo.
- **Pressupõe conhecimento prévio:** sim (pipelines, `cross_val_score`, `RandomForest`, DataFrame).
- **Foco:** leitura do tutorial do Kaggle com código.
- **Qualidade:** o apresentador lê o texto e comenta com sarcasmo, dizendo repetidamente que o autor "não sabe o que escreve" e que não entende partes (por exemplo 09:00–12:30 e 18:30–22:30), com longos desabafos fora do tema (09:30–11:00, 22:45–24:30). Pouco didático para quem não conhece a área; em inglês, com legenda automática.
- **Trechos recomendados:** nenhum necessário. Se quiser ver o exemplo exato do slide, 03:00–07:15, em inglês, mas o texto original da Kaggle (curso "Intermediate Machine Learning", lição "Data Leakage") é mais claro que o vídeo.
- **Veredito: descartar** (NW cobre o mesmo em português e mais bem).

---

## 3. Sequência recomendada para assistir (ordem dos slides)

| # | Slides | Vídeo | Trecho | Duração | O que o trecho entrega |
| :-- | :-- | :-- | :-- | :-: | :-- |
| 1 | 3–7 (desafios do AM) | **nenhum vídeo cobre** | — | — | Ler o material escrito (ver lacunas). Só a ideia de "dados representativos" aparece em HP 06:40–08:20 (item 2). |
| 2 | 8–14, 17–19 (parcial), 33–34 | HP `_XJTjJ0ZFFE` | 00:40–10:50 | 10:10 | Época e perda, generalização, validação, overfitting, treino/validação/teste, parada antecipada, aleatoriedade, teste "fácil", underfitting (só pela ótica do tempo de treino). Já cobre os slides 33–34; **não precisa rever depois**. |
| 3 | 16 (hold-out: proporções) | BN `8qTkdC_ccdY` | 05:50–09:00 | 3:10 | Hold-out e proporções 3/4–1/4 e 2/3–1/3. |
| 3b | 16 (hold-out) | **hold-out (Fernando dos Santos, a validar pelo usuário)** | — | — | Espaço reservado: decidir depois se substitui ou complementa o item 3. |
| 4 | 17 (crítica do hold-out) | AC `CWxaXyXZ-1A` | 02:00–04:00 | 2:00 | Um único conjunto de teste pode favorecer um modelo por sorte. |
| 5 | 18–19 (amostragem aleatória repetida) | (já visto em HP 08:20–10:00, item 2) | — | — | Sem vídeo próprio; média e desvio ficam para o material escrito. |
| 6 | 20 (validação cruzada k-fold) | FS `E1VAYcKnLxg` | 00:00–09:32 | 9:32 | Funcionamento passo a passo, estratificação, média das métricas. |
| 7 | 20 (complemento) | AC `CWxaXyXZ-1A` | 08:30–10:35 | 2:05 | k livre (10-fold mais comum), vantagem da média, exemplo do fold sortudo. |
| 8 | 21 (quando usar / base grande) | BN `8qTkdC_ccdY` | 40:00–41:50 e 42:17–43:45 | 3:18 | Validação cruzada vs. hold-out; hold-out basta em base muito grande. **Pular 41:51–42:17.** |
| 9 | 22–24 (data leakage) | NW `cauYnbfiayU` | 02:30–03:40; 11:16–17:10; 19:20–20:50; 21:00–22:50 | 10:25 | Definição, pré-processamento antes de dividir, atributos vazados, duplicação, dicas. |
| 10 | 25–32 (bias e variância) | AV `--NWR_1uIW0` | 00:20–14:00 | 13:40 | Bias, variância, overfit/underfit, curva de complexidade, alvo. |

**Tempo total (sem o vídeo de hold-out de Fernando dos Santos):** 10:10 + 3:10 + 2:00 + 9:32 + 2:05 + 3:18 + 10:25 + 13:40 = **54:20**.

Os vídeos descartados nesta sequência: CM (descartar). Opcional, só se sobrar tempo: BN 09:00–16:00 (segunda explicação do k-fold e da estratificação) e AC 12:00–27:00 (código scikit-learn, útil para a leitura de trechos de código da prova, mas fora do escopo das lacunas listadas).

---

## 4. Lacunas (tópicos que nenhum vídeo cobre bem; o material escrito deve cobrir)

1. **Desafios do AM (slides 3–7):** poucos dados, dados de baixa qualidade (erros, outliers, ruído), atributos irrelevantes e seleção/agregação de atributos, e **viés de amostragem** (nome e exemplo da desnutrição em áreas rurais). Só há a ideia de representatividade em HP 06:40–08:20, sem o conceito de viés de amostragem.
2. **Underfitting completo (slide 11):** definição como modelo simples demais, causas (modelo simples, atributos insuficientes, pré-processamento inadequado, pouco tempo de treino) e as três soluções (modelo mais poderoso, melhores atributos, ajustar hiperparâmetros). Os vídeos só mostram o caso "parou cedo" (HP) e "modelo simples" (AV, sem lista de soluções).
3. **Causas de overfitting (slide 10):** modelo complexo, base pequena, ruído, treino excessivo, vazamento. Os vídeos tocam em complexidade (AV) e treino excessivo (HP) apenas.
4. **Amostragem aleatória repetida com média e desvio padrão (slides 18–19)** e sua crítica (conjuntos de teste podem ser parecidos entre si). Só HP 08:20–10:00 fala em repetir e embaralhar, sem média/desvio e sem a crítica.
5. **Média e desvio padrão no k-fold (slide 20):** nenhum vídeo fala em desvio padrão; o significado de desvio alto (instabilidade do modelo) fica só no material escrito. Registrar também que BN soma as matrizes de confusão em vez de usar média por fold.
6. **Leakage temporal e Time Series Split (slide 23):** nenhum vídeo cobre. Vazamento por **normalização com média e desvio do dataset inteiro** (slide 24) também não é mostrado (só imputação, em NW).
7. **Hold-out: proporção 80/20 (slide 16):** os vídeos falam em 75/25 e 2/3–1/3; o vídeo de hold-out de Fernando dos Santos, ainda não avaliado, pode cobrir.
8. **Relação overfitting/underfitting × viés/variância (slides 28 e 31–32):** AV cobre a associação (alto viés = underfitting, alta variância = overfitting), mas o slide 32 e a definição formal de viés ("diferença entre o valor esperado da predição e o real") precisam do texto.
9. **Divergências de definição a registrar no material escrito (para a prova):** (a) variância = amplitude dos erros (slide) × consistência entre bases (AV); (b) viés definido sempre pelo erro de treino (slide e AV) vs. a definição geral; (c) hold-out para poucos dados (BN, contradiz slide 21); (d) "conjunto de validação" como subconjunto do treino (slide 34) vs. usos de NW/CM.
