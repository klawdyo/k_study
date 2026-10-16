# Validação dos vídeos pela transcrição — Aula 7 (Métricas de Avaliação para Classificadores) · Bloco 3

Método: li por inteiro a transcrição local (Whisper) de cada vídeo, minuto a minuto, e comparei com os 37 slides de `Aulas/Aula 7` (texto em `estudo/_fontes_extraidas/`). Todo `mm:ss` citado foi conferido e existe dentro da duração real do vídeo. Esta ficha **substitui** a versão anterior, que listava 12 vídeos (o bloco tinha 10), trazia uma matriz de cobertura com atribuições erradas (ex.: slide 19 atribuído a `nVctFRbmOZo`; "F1" em `vS6bQy45rdE`, que não fala de F1; "diagonal 0,5" em `yb9wic1bS4A`, que não a menciona; "k-NN vs Árvore" em `YyCgrYIcEOE`, que compara Random Forest e KNN) e afirmava "100% de cobertura", o que era falso.

Legenda: **B** cobre bem · **P** cobre parcialmente · **–** não cobre · **X** cobre com erro ou diverge do slide.

## 1. Vídeos aprovados (ordem sugerida de estudo)

| id | vídeo (ID) | canal · duração · idioma | trechos aprovados | slides | tipo |
| :-- | :-- | :-- | :-- | :-- | :-- |
| a7-v11 | `FZqMCgCbo3U` | Meigarom · 15:28 · pt | 01:22–03:46 · 04:03–14:51 | 4–7, 11, 17, 21 | principal (NOVO) |
| a7-v1 | `CbQ3se8wzfM` | Fernando dos Santos · 4:49 · pt | 00:00–04:49 | 4–8 | principal |
| a7-v6 | `vS6bQy45rdE` | Let's Data · 18:12 · pt | 02:24–04:00 · 04:28–07:41 · 10:01–14:26 | 4–8, 21, 30–32, 37 | principal, com **erro** a evitar |
| a7-v2 | `ePZswmBSLvc` | Programação Dinâmica · 12:58 · pt | 00:16–12:44 | 4, 9, 11–23, 26, 35–36 | principal (o melhor) |
| a7-v3 | `SRgZhZRKwqY` | Fernando dos Santos · 10:33 · pt | 00:00–10:33 | 11, 13–15, 17, 21, 23–24 | principal |
| a7-v4 | `nVctFRbmOZo` | Meigarom · 11:36 · pt | 02:13–11:13 | 17, 21, 22 | opcional |
| a7-v12 | `6vM-qc2StZI` | Apoena Stack · 21:33 · pt | 10:06–20:34 (e 01:02–09:59 se faltar base) | 17, 19, 21–22, 26, 30–31 | principal (NOVO) |
| a7-v5 | `rpZm6cH0fdQ` | Fernando dos Santos · 1:50 · pt | 00:00–01:47 | 26 | opcional, curto |
| a7-v13 | `rNLByGjvJ8c` | BlackBoard AI · 4:35 · **en** | 00:00–04:28 | 14, 26 | opcional (NOVO) |
| a7-v14 | `tdfVzRUqONc` | Rogério Anton · 6:01 · pt | 00:09–05:20 | 21, 30–31, 33 | principal (NOVO) |
| a7-v7 | `yb9wic1bS4A` | Café e Computação · 8:38 · pt | 01:53–08:08 | 33–34 | principal |
| a7-v9 | `4jRBRDbJemM` | StatQuest · 16:17 · **en** | 01:25–14:30 | 33–34 | opcional |
| a7-v15 | `eodZZgSjppg` | Infomity · 6:39 · **en** | 02:06–06:12 | 33–34 | opcional (NOVO) |
| a7-v10 | `FqHd1Cu_Cq4` | Apoena Stack · 12:07 · pt | 02:20–09:20 | 35–36 | opcional |

Descartados: `WfEMppwd6oQ` (a7-v8, transcrição péssima: "ALC ROCK", "Rubi-Col"; não explica o limiar; trata de multiclasse fora dos slides; o `notCovered` antigo dizia o contrário), `pgfga-EhHo4` (StudyPalz, 7:53, en: definições de uma linha cada, metade é multiclasse fora dos slides; nada que os outros não façam melhor), `YyCgrYIcEOE` (Nerd dos Dados, 17:33: 4 minutos de preparação de dados, código pesado, compara Random Forest e KNN com `roc_curve`; não fala de limiar, ao contrário do que a ficha antiga dizia).
Reserva (lido, não incluído): `8d3JbbSj-I8` (Scarlett's Log, 8:56, en): ótima intuição de por que o F1 usa média harmônica (precisão e recall se vigiam: prever tudo positivo dá recall 1 e precisão ≈ 0), mas sem exemplo numérico; fica no lugar do a7-v13 se o usuário preferir mais conceito e menos número.

## 2. Orientação da matriz (divergência recorrente)

- **Linhas = real, colunas = previsto** (igual ao scikit-learn): a7-v2, a7-v6 (real à esquerda), a7-v11.
- **Colunas = real, linhas = previsto**: a7-v3 e a7-v12. Não é erro, mas inverte a posição de FN e FP: confira sempre.
- a7-v10 diz "linhas = previstos" em 03:28 (errado para o sklearn) e se corrige em 04:40.

## 3. Cobertura dos slides (honesta)

| Slides | Tópico | Vídeos (trecho) | Situação |
| :-- | :-- | :-- | :-- |
| 3 | Introdução às métricas | — | texto |
| 4 | O que é a matriz de confusão | a7-v11 04:03–05:19; a7-v6 02:24–03:20; a7-v2 03:25–03:55 | B |
| 5 | Exemplo do hotel (cancelamento) | nenhum | **lacuna** (análogo: churn em a7-v6 11:48–14:26) |
| 6–8 | VP, VN, FP, FN | a7-v1 00:35–03:35; a7-v11 08:04–11:19; a7-v6 04:28–07:41 | B |
| 9 | Exemplo de SPAM | a7-v2 03:55–05:19; a7-v12 01:02–04:53 | B |
| 10–11 | Acurácia | a7-v3 00:07–02:01; a7-v2 00:16–00:59; a7-v11 13:47–14:43 | B |
| 12 | Acurácia no cancelamento (hotel) | a7-v6 11:48–14:26 (churn, acurácia 72%/75%) | P (análogo) |
| 13 | Desbalanceamento (SPAM 99%) | a7-v2 01:01–03:20; a7-v3 04:18–05:56; a7-v12 07:04–09:59 | B |
| 14 | Fraude com 99,8% de acurácia | a7-v13 00:00–00:35 (en, mesmo raciocínio, sem os números do slide) | P |
| 15 | Vantagens/desvantagens da acurácia | a7-v2 00:52–01:00; a7-v12 09:29–09:59 | P |
| 16–17 | Precisão | a7-v2 05:23–05:49 e 06:24–07:40; a7-v12 10:06–11:35 (82%); a7-v3 06:29–08:45 | B (sem os números 30/10 e 30/2 do slide) |
| 18 | Precisão no hotel | nenhum | **lacuna** |
| 19 | Importância do FP (vídeos infantis, investimentos) | a7-v2 06:24–07:40 (crianças); a7-v12 11:42–12:43 (spam) | P; **investimentos: lacuna** |
| 20–21 | Revocação/sensibilidade | a7-v2 07:41–09:20; a7-v3 08:08–09:09; a7-v12 12:44–13:46; a7-v14 01:06–01:40 | B |
| 22 | Fraude (revocação) | a7-v12 14:09–15:45; a7-v4 10:11–11:13 | B |
| 23–24 | Doença grave, baixa revocação | a7-v2 07:41–09:20; a7-v3 05:56–10:33; a7-v9 05:24–05:57 (Ebola) | B |
| 25–26 | F1 (média harmônica; F1 baixo ⇒ P ou R baixo) | a7-v13 02:10–04:03 (en, com número); a7-v2 09:34–10:04; a7-v12 18:24–20:34; a7-v5 | P: **nenhum vídeo em português com exemplo numérico** |
| 27 | F1 como confiabilidade da acurácia | nenhum | **lacuna** |
| 28–29 | F1 no hotel | nenhum | **lacuna** |
| 30–31 | Especificidade (VN/(VN+FP); foca nos FP) | a7-v14 01:40–02:17; a7-v12 15:46–18:24 (25%); a7-v6 10:29–10:48 (fórmula) | B |
| 32 | Especificidade no hotel | nenhum | **lacuna** |
| 33 | ROC/AUC: eixos, limiar (0,5) | a7-v14 02:17–04:36; a7-v7 01:53–04:35; a7-v9 01:25–08:30 (en); a7-v15 02:06–03:40 (en) | B |
| 34 | Diagonal, "mais alto é melhor", AUC de 0 a 1 | a7-v7 05:05–06:49; a7-v9 10:04–10:21 e 13:33–14:16 (en); a7-v15 03:40–05:28 (en) | B; **"AUC = 0,5 = chute" só em inglês (a7-v15)** |
| 35–36 | `classification_report`, suporte | a7-v2 10:09–12:44 (Iris, igual ao slide); a7-v10 06:33–09:20 (Titanic) | B |
| 37 | Conclusão: depende do custo | a7-v6 11:48–14:26; a7-v3 09:09–10:33; a7-v14 04:36–05:20 | B |

## 4. Fichas por vídeo

### a7-v11 · `FZqMCgCbo3U` · Meigarom — TUDO que você precisa saber sobre Matriz de Confusão! (15:28, pt) — NOVO
- **Cobre:** 01:22–03:46 contexto (fotos gato x cachorro, comparar rótulo real e previsto); 04:03–05:19 a matriz nasce de 4 combinações; 05:22–06:00 e 11:24–11:48 orientação (linhas = real, colunas = previsto; autores invertem); 06:00–07:56 positivo/negativo é convenção, fraude como positivo; 08:04–11:19 regra "acertou = verdadeiro, errou = falso" e nomes VP/FP/FN/VN; 11:56–14:43 precisão, revocação e acurácia derivadas da matriz.
- **Não cobre:** números; F1; especificidade; ROC; hotel.
- **Divergências:** em 12:30–12:41 diz "true positive mais falso negativo" no denominador da precisão (deslize; o certo é VP + FP).
- **Nível:** iniciante, didático. **Veredito:** aprovar 01:22–03:46 e 04:03–14:51. Único vídeo que explica a construção da tabela do zero (slide 4).

### a7-v1 · `CbQ3se8wzfM` · Fernando dos Santos — Elementos de uma matriz de confusão (4:49, pt)
- **Cobre:** 00:00–00:35 nomes das células; 00:35–01:45 VP e VN; 01:45–02:31 FP e FN (os **FP/FN começam em 01:45**, não em 03:10); 02:31–03:35 teste de covid; 03:35–04:24 exame de gravidez (charge); 04:24–04:49 erro tipo 1 = FP, tipo 2 = FN.
- **Ressalvas:** começa no meio de uma série (não monta a tabela); escorrega em 02:23 e corrige em 02:28. **Veredito:** aprovar inteiro, depois do a7-v11.

### a7-v6 · `vS6bQy45rdE` · Let's Data — Matriz de Confusão | Explicação e exemplos práticos (18:12, pt)
- **Cobre:** 02:24–03:20 layout da matriz (real à esquerda, previsto em cima, "não é padrão"); 03:20–04:00 covid; 04:28–06:14 VP/VN/FN/FP; 06:14–07:41 erros tipo 1 e 2 e charge; 10:01–10:48 recall e especificidade (fórmulas); 10:50–11:48 exemplo 6000/50/600/4000 (acurácia ≈ 94%, precisão ≈ 90%, recall ≈ 99%); 11:48–14:26 churn com custo (R$ 70 por FP, R$ 500 por FN): modelo de acurácia 75% perde R$ 3.900 contra R$ 3.250 do de 72%.
- **ERRO a evitar:** 04:01–04:28 e 09:40–09:50 dizem que em saúde a "precisão" deve ser alta e a definem como acertos entre os positivos reais (é a revocação); contradiz o slide 23. Em 14:26–17:00 diz que a ROC/AUC só vale para regressão logística (impreciso; os slides falam de classificação binária). **Não fala de F1.** Especificidade só em fórmula.
- **Veredito:** aprovar só 02:24–04:00, 04:28–07:41 e 10:01–14:26 (os clips pulam os trechos errados).

### a7-v2 · `ePZswmBSLvc` · Programação Dinâmica — Métricas de um CLASSIFICADOR (12:58, pt)
- **Cobre:** 00:16–01:00 acurácia; 01:01–03:20 desbalanceamento (100 e-mails, 99 não spam); 03:25–05:19 matriz e exemplo de SPAM (positivo = spam); 05:23–06:02 fórmulas de precisão e revocação; 06:24–07:40 vídeos para crianças (reduzir FP); 07:41–09:20 doença grave (reduzir FN); 09:34–10:04 F1 = média harmônica (só fórmula); 10:09–12:44 `classification_report` no Iris, com "suporte = número de amostras de cada espécie" (igual ao slide 35).
- **Ressalvas:** F1 sem exemplo numérico; o clip antigo (70–640) cortava justamente o F1 e o relatório do sklearn. **Veredito:** aprovar 00:16–12:44.

### a7-v3 · `SRgZhZRKwqY` · Fernando dos Santos — Métricas (acurácia, precision e recall) (10:33, pt)
- **Cobre:** 00:07–02:01 acurácia no exemplo de HIV (VP 1, VN 90, FN 8, FP 1 → 0,91); 02:27–04:18 por classe, só 1 dos 9 positivos achado; 04:18–05:56 modelo que sempre diz "negativo" também tem 0,91; 05:56–06:29 em diagnóstico importa achar os positivos; 06:29–08:05 precisão e recall; 08:08–09:09 precisão 0,5 e recall ≈ 0,11; 09:09–10:33 recall baixo é o problema.
- **Ressalvas:** matriz com colunas = real; **não** diz "precisão reduz FP" (cálculo apenas). **Veredito:** aprovar inteiro.

### a7-v4 · `nVctFRbmOZo` · Meigarom — Como entender as métricas Precision & Recall (11:36, pt)
- **Cobre:** 02:13–06:35 história do pesqueiro (160 lançamentos, 70 peixes de 100 no tanque); 06:44–07:56 precisão = 70/160 = 44%; 07:59–09:33 recall = 70% (tarde: precisão 19%, recall 100%); 09:33–10:07 recall da Fiat; 10:11–11:13 churn e fraude.
- **Ressalvas:** a ficha antiga falava em "peixes vs botas": **não há botas** na fala. Não menciona matriz nem FP/FN; a vara "super precisa" da tarde tem precisão menor (confuso). **Veredito:** só complemento opcional, depois do a7-v3.

### a7-v12 · `6vM-qc2StZI` · Apoena Stack — Métricas de Performance para Classificação (21:33, pt) — NOVO
- **Cobre (com um único exemplo, 80 spam e 20 não spam, VP 70, FN 10, FP 15, VN 5):** 01:02–04:53 matriz (colunas = real); 05:06–09:59 acurácia (75%) escondendo que o modelo erra a maior parte dos não spam; 10:06–11:35 precisão ≈ 82%; 11:42–12:43 custo do FP (e-mail importante na caixa de spam); 12:44–13:46 recall ≈ 88%; 14:09–15:45 fraude: FN caro, FP só gera análise; 15:46–17:21 especificidade 5/20 = 25%; 17:02–18:24 recall x especificidade mostram o desequilíbrio; 18:24–20:34 F1.
- **Ressalvas:** F1 só em fórmula; lapso em 03:44; matriz com colunas = real. **Veredito:** aprovar 10:06–20:34 (e 01:02–09:59 se faltar base). Preenche as lacunas de especificidade com número e de fraude (slide 22).

### a7-v5 · `rpZm6cH0fdQ` · Fernando dos Santos — Métrica F1-score (1:50, pt)
- **Cobre:** 00:00–00:57 F1 combina precisão e recall (fórmula na tela); 00:57–01:47 mesmo peso; nem todo problema é assim; próximo de 1 = bom.
- **Ressalvas:** não explica a média harmônica ("não vem ao caso"), sem número, não cobre o slide 27; as metas antigas prometiam o contrário. **Veredito:** complemento curto opcional.

### a7-v13 · `rNLByGjvJ8c` · BlackBoard AI — F1 Score: Melhor que a Acurácia para Dados Desbalanceados (4:35, en) — NOVO
- **Cobre:** 00:00–00:35 acurácia de 99% inútil (fraude); 00:35–01:46 matriz, precisão e recall; 01:46–02:10 cabo de guerra; 02:10–03:12 por que não a média simples e F1 ≈ 0,02 com precisão 1,0 e recall 0,01; 03:12–04:03 exemplo de 1.000 e-mails (90/10/10/890 → F1 0,90).
- **Ressalvas:** inglês; sem slide 27 nem hotel. **Veredito:** complemento opcional (único com número de F1).

### a7-v14 · `tdfVzRUqONc` · Rogério Anton — Sensibilidade e Especificidade (6:01, pt) — NOVO
- **Cobre:** 00:09–01:06 todo teste erra, tabela doentes x não doentes; 01:06–01:40 sensibilidade (alta ⇒ poucos FN ⇒ negativo confiável, bom para descartar); 01:40–02:17 especificidade (alta ⇒ poucos FP ⇒ positivo confiável, bom para confirmar); 02:17–03:45 ponto de corte (limiar): mover aumenta uma e reduz a outra; 03:45–04:36 curva ROC (sensibilidade x 1 − especificidade, canto superior esquerdo); 04:36–05:20 custo e risco; triagem x confirmação.
- **Ressalvas:** vocabulário médico; sem fórmulas nem números (use o a7-v12); não fala de AUC = 0,5. **Veredito:** aprovar. Única explicação em português da especificidade com a ideia de limiar.

### a7-v7 · `yb9wic1bS4A` · Café e Computação — Teoria da Curva ROC e Métrica AUC (8:38, pt)
- **Cobre:** 01:53–02:55 ROC = TPR x FPR em vários limiares; 02:59–04:35 fórmulas dos eixos; 04:35–05:05 ponto = limiar, 1 − FPR = especificidade; 05:05–05:43 canto superior esquerdo; 05:43–06:49 AUC de 0 a 1; 06:49–07:30 AUC independe do limiar.
- **Ressalvas:** em 00:57–01:53 chama a **acurácia** de "precisão"; chama a ROC de "curva AUC"; **não** menciona diagonal nem 0,5 (a ficha antiga afirmava); diz AUC 0 = "modelo completamente ruim". **Veredito:** aprovar 01:53–08:08.

### a7-v9 · `4jRBRDbJemM` · StatQuest — ROC and AUC, Clearly Explained! (16:17, en)
- **Cobre:** 01:25–03:00 probabilidade e limiar 0,5; 03:03–04:43 camundongos e matriz; 04:48–07:00 mudar o limiar, exemplo do Ebola; 07:03–08:30 ROC; 08:32–13:30 construção ponto a ponto; 10:04–10:21 diagonal; 13:33–14:16 AUC; 14:24–15:30 extra (precisão no lugar de FPR).
- **Ressalvas:** inglês; não diz "AUC = 0,5 = aleatório". **Veredito:** aprofundamento opcional; o melhor para entender o limiar.

### a7-v15 · `eodZZgSjppg` · Infomity — O que são as curvas ROC e AUC em Machine Learning? (6:39, en) — NOVO
- **Cobre:** 02:06–02:49 limiar; 02:49–03:40 ROC; 03:40–04:24 canto superior esquerdo, diagonal = aleatório, abaixo = pior que o acaso; 04:24–05:00 AUC de 0 a 1; 05:00–05:28 **AUC 0,5 = jogar uma moeda**, acima de 0,9 excelente.
- **Ressalvas:** inglês; chama ROC/AUC de "robustos" ao desbalanceamento (simplificação). **Veredito:** complemento opcional curto.

### a7-v10 · `FqHd1Cu_Cq4` · Apoena Stack — Métricas de Performance para Classificação com Sklearn (12:07, pt)
- **Cobre:** 02:17–03:00 `sklearn.metrics`; 02:49–04:17 `confusion_matrix` (124 VN, 15 FP, 45 FN, 39 VP); 04:23–05:43 heatmap; 05:45–06:27 leve desbalanceamento; 06:33–08:50 `classification_report` (acurácia 73%, recall 0,89 x 0,46; recall da classe negativa = especificidade); 08:53–09:20 suporte (139 e 84).
- **Ressalvas:** em 03:28 diz "linhas = previstos" (errado para o sklearn), 04:54–05:19 cita 165 e 83 (não batem); usa Titanic, não Iris; não diz y_true/y_pred. **Veredito:** complemento opcional.

## 5. Lacunas restantes (depois de duas rodadas de busca)

1. **Exemplo do hotel** (slides 5, 12, 18, 28, 29, 32): nenhum vídeo; analogia com churn em a7-v6 11:48–14:26. Fica para a leitura do zero.
2. **Investimentos** (slide 19) e os números do slide 14 (1.000.000 de transações, 998.000 corretas): nenhum vídeo; o raciocínio está em a7-v3, a7-v13 (en) e a7-v2.
3. **F1 com exemplo numérico em português** (slides 26, 28 e 29): só em inglês (a7-v13). O motivo da média harmônica também só em inglês.
4. **Slide 27** (F1 como confiabilidade da acurácia): nenhum vídeo; só texto.
5. **"AUC = 0,5 = chute aleatório" em português** (slide 34): só em inglês (a7-v15); em português só aparece no vídeo descartado a7-v8 (transcrição péssima).
6. Os números 30/10 e 30/2 do slide 17 não aparecem em nenhum vídeo.

- **11/10/2026 (agente principal):** o a7-v3 passou de obrigatório a opcional: usa a matriz de confusão transposta (colunas = real), ao contrário do slide e do scikit-learn, e cobre o que o a7-v2 e o a7-v12 já cobrem; nada foi removido.
