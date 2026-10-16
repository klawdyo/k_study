# Validação dos vídeos pela transcrição — Aula 6 (k-NN), refeita

Esta ficha **substitui a anterior**, cujos tempos e "cobre" estavam inventados (marcações além da duração real, trechos que não existem). Desta vez:

- **Todas as transcrições foram lidas por inteiro** em `estudo/conteudo/transcripts/<ID>.json`, minuto a minuto, comparadas com o texto dos 34 slides (`estudo/_fontes_extraidas/Aulas__Aula_6_-_KNN.pptx.txt`). Exceção declarada: nos vídeos descartados por serem de outro assunto (os três de pré-processamento do canal Eduardo e o de imputação da DataMites) li só o começo de cada minuto.
- Os tempos `mm:ss` têm precisão de uns ±10 s (a transcrição vem em blocos). **Conferi que todo `mm:ss` citado cabe na duração real** (campo `duration` do JSON) e que todo clip está dentro dela.
- Duas rodadas de busca: a primeira com os termos dos slides (K, overfitting, Minkowski/Manhattan, scikit-learn, regressão, vantagens e desvantagens, Mahalanobis, weights, Hamming) e a segunda para as lacunas (kd_tree/ball_tree, KNN Imputer, LOF, Hamming com categóricas, Mahalanobis, maldição da dimensionalidade). 26 vídeos transcritos localmente nesta rodada, mais os 5 que já estavam na aula (a6-v3, que só tem 2:48, também foi relido por inteiro).
- Erros recorrentes da legenda automática: "cavizinhos" = k vizinhos, "loft" = LOF, "Marlanóbis" = Mahalanobis, "waves" = weights.

Legenda dos símbolos: **B** = cobre bem · **P** = cobre em parte · **–** = não cobre · **X** = diverge do slide ou está errado.

## 1. Resultado em uma tabela

| Vídeo (id no bloco) | Duração real | Canal | Veredito | Tópicos (slides) |
| :-- | :-: | :-- | :-- | :-- |
| a6-v1 `gJK4fmCvcWY` | 10:39 | Sandeco | **aprovar com avisos** | ideia, passo a passo, votação, K ímpar (4, 6, 8, 10, 12, 13, 22) |
| a6-v6 `6nEVitKTntY` (novo) | 18:02 | Tech&Dados | **aprovar** | intuição, voto ponderado, Euclidiana/Manhattan/Minkowski, escala, prós e contras (6, 8, 13, 16–20, 22–24) |
| a6-v5 `gmrMAbNgboE` | 16:03 | Andre Kuniyoshi | **aprovar com avisos** (clips corrigidos) | mecânica, regressão, parâmetros, contras, lazy (5, 6, 8, 10, 11, 16–20) |
| a6-v12 `x5MRHYrr4Zo` (novo) | 4:32 | Máiron Chaves | aprovar só 02:09–04:15, opcional | regressão com k-NN (4, 18) |
| a6-v7 `kqIE-1DlKm8` (novo) | 7:45 | GabaritoAqui | **aprovar** | K pequeno × grande, validação cruzada (12, 13, 15) |
| a6-v8 `7WySJWL2o_4` (novo) | 23:27 | Francisco Rodrigues | aprovar só trechos, opcional | K, distâncias, normalizar, lazy (5, 8, 12, 13, 20, 22–25) |
| a6-v4 `xU0Yq-j0Djs` | 6:19 | Máiron Chaves | **aprovar** (metadados e clips corrigidos) | Min-Max e z-score (20, 22) |
| a6-v9 `3QzNv-pseoQ` (novo) | 19:37 | Rafael Rossi | aprovar só trechos | Manhattan, Euclidiana, Minkowski (22–24) |
| a6-v10 `mHXvkaZCV5s` (novo) | 8:50 | Engineering Wing | aprovar só trechos, opcional, **inglês** | Hamming com k-NN (25) |
| a6-v11 `0tMw0X_Efrw` (novo) | 26:56 | Hemerson Pistori | aprovar só trechos, opcional | Mahalanobis (26–27) |
| a6-v13 `9essjyA7fxs` (novo) | 22:59 | erikvgl | aprovar só 01:33–06:50, opcional (fraco) | LOF (28, 29) |
| a6-v14 `lCKQaxDPDXY` (novo) | 11:58 | TileStats | aprovar só 04:20–08:20, opcional, **inglês** | KNN Imputer (29) |
| a6-v15 `FnJj28u7rF0` (novo) | 14:18 | learndataa | aprovar só trechos, opcional, **inglês** | brute, kd_tree, ball_tree (31, 32) |
| a6-v16 `HJAChG-GRyA` (novo) | 30:49 | Hashtag Programação | aprovar só trechos | lazy, weights, metric, p, empate (5, 13, 16, 31, 33, 34) |

Tempo total dos clips: 63 min só nos obrigatórios (a6-v1, v6, v5, v7, v4, v9, v16) e 118 min com os opcionais.

## 2. Matriz tópicos dos slides × vídeos aprovados

| Tópico (slide) | v1 | v6 | v5 | v7 | v8 | v4 | v9 | v16 | outros |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-- |
| Supervisionado, classificação e regressão, não paramétrico (4) | P | P | B | P | P | – | – | – | v12 (regressão) |
| Lazy / "não treina" (5, 17) | – | P | B | – | P | – | – | B | – |
| Funcionamento, ideia de vizinhança (6) | B | B | B | – | – | – | – | P | – |
| Exemplo com K, votação (8) | B | B | B | P | B | – | – | – | – |
| Pseudocódigo: distâncias → ordenar → K → votar (10) | B | B | B | – | B | – | – | – | – |
| Maldição da dimensionalidade (11) | – | P | P | – | – | – | – | – | a3-v13 (inglês) |
| Como escolher K: ímpar, empírico, validação (12) | P | P | – | B | B | – | – | P | – |
| K grande × pequeno: over/underfitting (13, 15) | – | P | – | **B** | B | – | – | – | – |
| k-NN ponderado (16) | – | B | P | – | – | – | – | B | – |
| Vantagens (17, 18) | – | B | B | – | P | – | – | – | – |
| Desvantagens (19, 20) | – | B | B | – | P | – | – | – | – |
| Sensível à escala; padronizar (20, 22) | – | B | – | – | B | B | – | P | v14 |
| Euclidiana (22) | B | B | – | – | B | – | B | – | – |
| Minkowski (23) | – | B | – | – | B | – | B | P | – |
| Manhattan (24) | – | B | – | – | B | – | B | – | – |
| Hamming (25) | – | – | – | – | P | – | – | – | v10 |
| Mahalanobis (26, 27) | – | – | – | – | – | – | – | – | v11 |
| Usos não supervisionados: LOF, KNNImputer, t-SNE/UMAP (28, 29) | – | – | – | – | – | – | – | – | v13 (LOF), v14 (KNNImputer); t-SNE/UMAP sem vídeo |
| Hiperparâmetros: n_neighbors, weights, metric, p (30, 33, 34) | P | – | P | – | P | – | – | B | – |
| algorithm: brute, kd_tree, ball_tree (31, 32) | – | – | – | – | – | – | – | P (só diz que existe) | v15 (inglês) |

## 3. Fichas dos vídeos aprovados

### a6-v1 — Sandeco `gJK4fmCvcWY` (10:39)
- **Cobre** (releitura): 00:55–02:20 k-NN baseado em distância, "dados similares ficam na mesma região" (flores Iris); 02:20–03:05 serve para classificação e regressão; 03:12–04:04 monta o exemplo (círculos, quadrados, asterisco); 04:04–05:56 distância euclidiana em 2D, 3D e n dimensões; 05:56–07:20 distâncias ordenadas da menor para a maior; 07:20–08:47 K=1, 2 (empate), 3 e 4; 08:47–09:22 K ideal e K ímpar; 09:22–10:14 uso no scikit-learn.
- **Divergências:** (a) 08:47 "o K ideal é log de n" (regra pouco usual; o slide 12 diz que não há valor único); (b) 09:46 "por padrão o valor é 3": errado, o padrão de `n_neighbors` é 5 (conhecimento externo, conferido no vídeo a6-v16, 07:16, que também diz 5).
- **Não cobre:** escala, maldição da dimensionalidade, prós e contras, trade-off de K, outras distâncias, hiperparâmetros.
- **Nível:** iniciante. **Idioma:** pt (legenda com erros de nomes).
- **Veredito: aprovar** 00:52–10:10 com os dois avisos.

### a6-v6 — Tech&Dados `6nEVitKTntY` (18:02)  *(novo)*
- **Cobre:** 00:57–02:35 exemplo de clientes (renda × idade) e a intuição; 03:00–03:35 K=3 × K=7 mudam a classe; 03:35–04:55 voto ponderado pela distância (soma dos inversos); 05:00–07:45 Euclidiana (caminho mais curto) × Manhattan (quarteirões), fórmula de Minkowski com p=1 e p=2, e cálculo com números (Manhattan = 7, Euclidiana = 5); 07:55–08:40 mecânica (lista ordenada, K primeiros, voto); 08:40–10:37 premissas (dados numéricos e padronizados), com gráfico antes e depois de igualar as escalas; 10:39–11:45 vantagens (sem treino/lazy, simples, incremental, regressão, não paramétrico); 11:45–12:58 desvantagens (dimensões, K difícil com K pequeno → overfit e K grande → generaliza demais, escala, custo de predição, menção a particionar o espaço); 13:30 em diante código com Iris, K=5 e weights.
- **Divergências:** voto ponderado usa 1/d (04:25), o slide 16 fala do inverso do quadrado; lapso na soma de quarteirões aos 06:33 (corrigido aos 07:12); "não paramétrico" explicado de forma solta (11:30).
- **Não cobre:** Hamming, Mahalanobis, não supervisionado, hiperparâmetros (só mostra weights no código, 15:56–16:10), maldição em detalhe.
- **Nível:** iniciante. **Idioma:** pt, fala clara.
- **Veredito: aprovar** os cinco trechos (00:57–12:58). É o mais completo da aula.

### a6-v5 — Andre Kuniyoshi `gmrMAbNgboE` (16:03)
- **Cobre:** 00:00–03:57 dataset fictício (tabela e gráfico; renda, tempo no site, comprou casa); 03:57–06:19 mecânica (distâncias a todos, ordenar, K=5 mais próximos, votar); 06:19–08:50 segundo exemplo em que o k-NN erra por ruído, acurácia 90%; 09:04–09:50 **regressão** (média dos vizinhos); 09:50–10:50 parâmetros K, métrica (euclidiana, Manhattan) e peso dos vizinhos; 10:54–12:47 contras (maldição, custo "10 bilhões de distâncias", ruído); 12:47–13:10 opinião "nunca vi em produção"; 13:19–14:12 prós (simples, interpretável); 14:36–15:50 "por que o k-NN não treina" (lazy).
- **Correções em relação à ficha antiga:** o vídeo **aborda regressão** (09:04–09:50); **não** fala de "K ímpar" nem de "regiões de decisão" (a ficha antiga atribuía); **não** menciona escala (e usa colunas em escalas diferentes sem padronizar, o que contradiz o slide 22); duração real 16:03.
- **Nível:** iniciante. **Idioma:** pt, legenda boa.
- **Veredito: aprovar** 03:59–07:42, 09:00–10:54, 10:54–14:00 e 14:36–16:00, com os avisos.

### a6-v12 — Máiron Chaves `x5MRHYrr4Zo` (4:32)  *(novo, opcional)*
- **Cobre:** 02:09–04:15 k-NN para **regressão**: calcula distâncias, pega os 3 vizinhos, faz a média (15,03); com 4 vizinhos a média muda (18,02).
- **Ressalvas:** 00:00–02:09 é árvore de decisão (Aula 8); a fala mistura "altura" e "volume" (02:09–02:40).
- **Veredito: aprovar só 02:09–04:15.**

### a6-v7 — GabaritoAqui `kqIE-1DlKm8` (7:45)  *(novo)*
- **Cobre:** 01:04–02:17 supervisionado e não paramétrico, 4 passos da votação; 02:17–03:00 K=1: fronteiras fragmentadas, decora o ruído, overfitting, variância alta; 03:00–03:35 K grande: nuances locais somem, underfitting, viés alto; 03:35–04:05 o dilema (viés × variância); 04:05–05:36 curvas de erro de treino e de validação para K pequeno e K grande; 05:36–06:57 validação cruzada para escolher K.
- **Não cobre:** K ímpar para evitar empate. Voz de narração sintética e estilo de resumo; as "curvas" são descritas, não pude ver o gráfico.
- **Nível:** iniciante a intermediário. **Idioma:** pt.
- **Veredito: aprovar** 01:02–06:57. É o único vídeo em português que explica o trade-off de K (slides 13 e 15).

### a6-v8 — Francisco Rodrigues `7WySJWL2o_4` (23:27)  *(novo, opcional)*
- **Cobre:** 04:51–05:55 euclidiana e Minkowski como generalização (p=2); 07:34–07:50 Manhattan (4−2 + 5−2 = 5); 08:00–08:35 distância para nominais e ordinais; 08:35–10:34 algoritmo (K=3 → vermelho, K=5 → azul); 11:36–13:20 K=1 irregular, overfitting × underfitting, K por validação cruzada; 13:20–13:50 comparar métricas, grid search; 13:55–15:30 normalizar (exemplo 1000 × 1); 21:00–21:55 "não aprende um modelo, só memoriza".
- **Divergências:** 13:02 "não paramétrico porque K é ajustado pelo usuário" (impreciso); 00:12 histórico diferente do slide 3; legenda confusa em 08:00–08:09.
- **Veredito: aprovar só os trechos indicados**, como complemento. 15:30–20:30 é código próprio e holdout.

### a6-v4 — Máiron Chaves `xU0Yq-j0Djs` (6:19)
- **Cobre (real):** 00:03–00:57 variáveis em metros, reais e % dominam a distância (k-NN e cluster); 00:57–03:11 Min-Max; 03:11–05:33 z-score; 05:33–06:11 recapitulação.
- **Correções:** duração real **6:19** (não 8:57); **não há** "visualização antes e depois", **nem código fit/transform**, nem vazamento; slides certos: 20 e 22 (não 28 e 29).
- **Veredito: aprovar** 00:03–06:11.

### a6-v9 — Rafael Rossi `3QzNv-pseoQ` (19:37)  *(novo)*
- **Cobre:** 00:00–03:24 um atributo e módulo; 03:24–07:00 dois atributos (idade e peso); 07:00–08:50 Manhattan/City Block (quarteirões); 08:50–11:47 Euclidiana por Pitágoras (44,72 < 60); 12:19–13:55 n atributos; 13:55–15:15 Minkowski (expoente 1 = Manhattan, 2 = Euclidiana); 15:20–19:25 distância suprema (fora dos slides).
- **Divergências:** 07:00 diz 70 em vez de 60 (corrige aos 11:17); usa "h" no lugar de "r"; não diz quando usar Manhattan (alta dimensão, outliers: slide 24).
- **Veredito: aprovar** 03:24–12:20 e 12:45–15:15.

### a6-v10 — Engineering Wing `mHXvkaZCV5s` (8:50)  *(novo, opcional, inglês)*
- **Cobre:** 00:10–00:50 Hamming para categóricos/binários e euclidiana para contínuos; 02:10–03:40 regra iguais = 0, diferentes = 1; 04:15–06:35 exemplo linha por linha; 06:35–07:50 K=3 e voto majoritário.
- **Ressalva:** áudio em inglês; único que liga Hamming ao k-NN. Não fala de one-hot.
- **Veredito: aprovar** 00:15–07:50 como complemento.

### a6-v11 — Hemerson Pistori `0tMw0X_Efrw` (26:56)  *(novo, opcional)*
- **Cobre:** 09:55–10:48 a euclidiana classifica o 6 como viável sem existir viável com 6; 10:48–11:38 ignora o espalhamento; 11:38–13:00 Mahalanobis em uma variável (divide pelo desvio padrão); 12:48–13:58 desvios 0,82 e 2,58, distâncias 2,45 e 1,16; 14:01–15:15 euclidiana é caso particular; 16:26–21:00 com 2 atributos o espalhamento tem direção; 21:00–25:55 fórmula com matriz de variância e covariância e custo de inverter a matriz.
- **Ressalvas:** não é k-NN (classificador pela média da classe); 14:06 "sempre funciona melhor" é exagero; usa "espalhamento" mais que "correlação".
- **Veredito: aprovar** 09:55–21:00 como intuição; 21:00–26:00 é opcional (matemática).

### a6-v13 — erikvgl `9essjyA7fxs` (22:59)  *(novo, opcional, fraco)*
- **Cobre:** 01:33–03:00 densidade; 02:21–02:55 LOF compara a densidade com a dos vizinhos, não supervisionado; 04:00–04:45 anomalia local × global; 05:10–06:00 score ≈ 1 normal, > 1 anomalia; 06:09–06:40 limitações (custo, sensível a K).
- **Ressalvas:** apresentação de trabalho de aluno, hesitações e legenda confusa; DBSCAN (10:08–14:20) e código em R (14:40–20:30) fora dos slides.
- **Veredito: aprovar só 01:33–06:50**, como complemento.

### a6-v14 — TileStats `lCKQaxDPDXY` (11:58)  *(novo, opcional, inglês)*
- **Cobre:** 04:20–05:30 imputação por k-NN (K=5 por padrão, média dos vizinhos); 05:30–06:25 euclidiana e padronizar; 06:25–08:20 exemplo numérico (IMC 28,33).
- **Veredito: aprovar** 04:20–08:20 como complemento. Único achado claro sobre KNN Imputer; áudio em inglês.

### a6-v15 — learndataa `FnJj28u7rF0` (14:18)  *(novo, opcional, inglês)*
- **Cobre:** 00:35–01:20 força bruta; 01:35–04:15 construção da kd_tree (mediana); 04:15–07:45 busca na kd_tree; 08:07–13:40 ball_tree.
- **Ressalvas:** não diz que ball_tree é melhor para muitas dimensões (slide 31) nem cita `algorithm='auto'`; escolha do eixo simplificada.
- **Veredito: aprovar** 00:35–13:40 como complemento. Único com os três algoritmos juntos; áudio em inglês.

### a6-v16 — Hashtag Programação `HJAChG-GRyA` (30:49)  *(novo)*
- **Cobre:** 00:21–02:20 intuição; 02:21–03:00 lazy; 03:05–03:55 weights; 04:00–04:30 radius neighbors; 04:35–05:12 aviso de escala; 07:05–07:55 documentação (n_neighbors padrão 5, weights, metric); 11:05–11:50 metric = minkowski e p = 2 (euclidiana); 12:18–12:40 algoritmos que otimizam a busca (sem nomear); 13:00–15:55 desempate pela ordem dos dados, evitar K par.
- **Divergências:** não cita kd_tree/ball_tree/brute nem p = 1 = Manhattan (slides 31 a 33).
- **Veredito: aprovar** 02:21–05:12, 07:05–07:55, 11:05–12:45 e 13:00–15:55. A melhor cobertura em português de weights, metric e p; o resto (16:00–29:30) é código com Iris e matriz de confusão (Aula 7).

## 4. Descartados e por quê

| Vídeo | Motivo |
| :-- | :-- |
| a6-v2 `DeAuVrhKw58` Programação Dinâmica (11:08) | Reduzido a um exemplo de código com K=10 (par: poderia dar empate, contra o slide 13) no Iris, mais classification report e matriz de confusão (Aula 7). **Não há** discussão de escolha de K, K ímpar, over/underfitting nem hiperparâmetros (a ficha antiga inventou). O que serve (votação, `KNeighborsClassifier`) está melhor em a6-v1 e a6-v16. |
| a6-v3 `WVNoO5Iy8Og` PM Expert (2:48 reais, 6:48 no bloco) | Áudio em **inglês**, só 2:48 (os clips e "covers" do bloco passavam da duração). Diz (02:07 e 02:22) que Manhattan "resolve" features em escalas diferentes: **errado**, só a padronização resolve. Sobre o que o slide 24 pede (menos sensível a outliers), a legenda de 02:22 é ilegível ('tem alunos', talvez 'outliers'): não dá para confirmar. Substituído por a6-v6 e a6-v9. |
| `-2H5LmhR6B0` Máiron Chaves, Aula 12 KNN (10:15) | Pt e correto: exemplo de empresas boas/más pagadoras, cálculo euclidiano à mão e votação com K=1, 2, 4 e 7 (06:27–08:20, a classe muda com K). Redundante com a6-v1 e a6-v6; a gravação termina no intervalo da aula (09:50). Também diz que o R 'testa todos os valores de K'. Pode servir de reserva. |
| `Uht9flzEEAY` Nerd dos Dados (14:58) | Demonstração em código no Iris sem distância nem K; só o aviso de escala (13:48–14:20) é útil e está melhor em a6-v6 e a6-v16. |
| `Tq5QVLuwbBE` CS School (11:16) | Inglês; tutorial de código com validação cruzada e matriz de confusão; só cita brute/kd/ball tree de passagem (02:20–02:55). |
| `nPtDRe7K_x4` Código Fluente (32:27) | Passo a passo de código (pandas, split, StandardScaler, K=5). Úteis só: "não paramétrico, funciona com fronteira irregular" (02:51) e escalar (16:11–18:45), que já estão em outros vídeos. |
| `lKht-wb1vys` Hamming (4:05) | Inglês; é Hamming de **códigos corretores de erro** (bits e paridade), não de k-NN. |
| `xXhLvheEF7o` TileStats Mahalanobis (11:01) | Áudio em inglês e a transcrição saiu em sueco nos 3 primeiros minutos; bom conteúdo (centroide, elipse), mas com chi-quadrado e outliers além do slide. Prefira a6-v11. |
| `gzmus8zwWno` Mahalanobis (4:53) | Áudio em **espanhol**, 4:53; boa descrição verbal, mas sem exemplo numérico. |
| `-F1f5mefSi0` Aric LaBarr Mahalanobis (4:58) | Inglês; ótima intuição de por que olhar uma dimensão por vez falha, mas inclui a versão robusta (MCD), fora do slide. Alternativa ao a6-v11 se quiser algo de 5 min. |
| `-PRuwwzgNas` Alcinei Azevedo Mahalanobis (25:13) | Pt, mas é de análise multivariada com delineamento experimental e MANOVA no R. Só 04:56–07:00 (a euclidiana supõe ângulo reto = sem correlação) e 10:00–10:56 (Mahalanobis também padroniza) são relevantes. |
| `Ymvq6JHjoBY` Aric LaBarr LOF (5:02) | Inglês; define "densidade" como área do círculo (o contrário do que o iniciante espera) e diz "densidade maior que a dos vizinhos = outlier". Confuso para o slide. |
| `2Tf2LunSPHY` e `P3JwElzE1iw` KNN Imputer | Ingleses; o primeiro é muito condensado (distância "nan-euclidiana" e produção), o segundo é tutorial de código. a6-v14 é melhor. |
| `Y4ZgLlDfKDg` Lavrenko kd-tree (5:50) | Inglês; só kd_tree, repete parte de a6-v15. |
| `oyNkmkAWvyM`, `kg-9-2SurlM` Eduardo (imputação) | Falam de `dropna` e mediana, não de k-NN. |
| `9Tf-_mJhOkU` DataMListic (maldição, 8:07) | Já usado em a3-v13; áudio em inglês (transcrição mista). Para o slide 11 serve, mas já está na Aula 3. |

## 5. Lacunas que restam (duas rodadas feitas)

Cobertas pela leitura `aula-6-do-zero.md`, sem vídeo bom:

- **Slide 3** (histórico, Fukunaga e Narendra): irrelevante.
- **Slide 5:** dividir em treino e teste mesmo sendo lazy; K=1 acerta 100% no treino (nenhum vídeo fala).
- **Slide 11:** maldição da dimensionalidade com "todos os pontos parecem longe na mesma proporção": só menções curtas (a6-v5 10:54–11:20, a6-v6 11:45–11:55) e o vídeo em inglês da Aula 3 (a3-v13).
- **Slide 19:** baixa performance com variáveis categóricas explicativas; irrelevantes/redundantes: só a6-v6 08:50–09:00 (dados numéricos) e a6-v10 (Hamming).
- **Slide 24:** "Manhattan reduz a influência de outliers e vai melhor em alta dimensão": nenhum vídeo diz.
- **Slides 28 e 29:** t-SNE e UMAP sem vídeo (só LOF e KNN Imputer, opcionais).
- **Slides 31 e 32:** kd_tree/ball_tree/brute só em inglês (a6-v15), e "ball_tree para muitas dimensões" sem vídeo.
- **Slide 33:** p = 1 → Manhattan em hiperparâmetro do scikit-learn: o vídeo a6-v16 só mostra p = 2; a ligação p = 1 é dita em a6-v9 (expoente 1) e a6-v6.
- **Hamming e KNN Imputer:** só em inglês (a6-v10, a6-v14).
