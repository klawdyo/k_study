# Validação dos vídeos pela transcrição — Aula 3 (Pré-processamento), rodada 2

Método: li a transcrição inteira de cada um dos 12 vídeos novos (`estudo/conteudo/transcripts/<ID>.json`; Whisper `small` ou legenda automática, com erros) e comparei com os 51 slides de `Aulas/Aula 3 - Pré-Processamento` (texto em `estudo/_fontes_extraidas/`). Os tempos `mm:ss` têm precisão de cerca de ±15 s. Esta ficha continua a [`validacao-videos-aula-3.md`](validacao-videos-aula-3.md) (rodada 1, vídeos a3-v1 a a3-v8, que não foram alterados). Quando aponto um erro ou limite que não depende do vídeo, marco "(conhecimento externo)". A proposta de itens para o `block.json` está num arquivo à parte (`proposta_aula3.json`, ids a3-v9 a a3-v19, com o campo extra `afterSlide`).

Aviso sobre dados que a transcrição não traz: o nome do **canal** não consta no JSON da transcrição. Onde não aparece falado no vídeo, escrevi "(a confirmar)" no campo `channel`; confirmar no YouTube antes de integrar.

Legenda da matriz: **B** = cobre bem · **P** = cobre parcialmente · **–** = não cobre · **X** = cobre de forma que diverge do slide.

## 1. Matriz: tópicos que eram lacuna × vídeos novos

| Tópico (slides) | 10km UNIVESP | p_Sm Dados faltantes | 4hUN Desbalanc. | w08j Winsoriz. | xD9 Normaliz. | 6as0 fit_transf. | RF6s Binning | 9Tf Maldição | x68C Redução | Y_4d Boxplot | o3uT Excluir? | dcXw Z-score |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Integração de bases, inconsistência, redundância (3–4) | B | – | – | – | – | – | – | – | – | – | – | – |
| Dados faltantes: alternativas (6) | B | P | – | – | – | – | – | – | – | – | – | – |
| Ruído e outliers: o que são (7) | B | – | – | P | – | – | – | – | – | – | P | P |
| Z-score, regra \|Z\| > 3 (9) | – | – | – | – | – | – | – | – | – | – | – | B |
| Quartis, IQR e regra 1,5×IQR (10–11) | – | – | – | – | – | – | – | – | – | B | – | – |
| IQR × Z-score: robustez da mediana (12) | – | – | – | P | – | – | – | – | – | – | P | – |
| Winsorização (13) | – | – | – | P | – | – | – | – | – | – | – | – |
| Manter o outlier real (13) | – | – | – | – | – | – | – | – | – | – | B | – |
| Manter + algoritmos robustos (árvores, boosting) (13) | – | – | – | – | – | – | – | – | – | – | – | – |
| Aplicar a transformação só no treino (13, 18) | – | X (ajusta na base toda) | – | – | – | B | – | – | – | – | – | – |
| Mudança de escala: por quê (14) | – | – | – | – | P (com fórmula diferente) | – | – | – | – | – | – | – |
| Discretização (21) | – | – | – | – | – | – | P (larguras iguais e frequência) | – | – | – | – | – |
| Maldição da dimensionalidade (22–23) | – | – | – | – | – | – | – | B (inglês) | P | – | – | – |
| Vantagens × desvantagens da redução (24–25) | – | – | – | – | – | – | – | – | B | – | – | – |
| Seleção × agregação (26–30) | P (só redundância, 29) | – | – | – | – | – | – | – | – | – | – | – |
| Over/undersampling e SMOTE (49–51) | – | – | B | – | – | – | – | – | – | – | – | – |
| Sobreajuste por duplicar; perda de informação ao remover (49) | – | – | P (só a perda) | – | – | – | – | – | – | – | – | – |

Observação sobre a lacuna "seleção × agregação" que o pedido associava ao vídeo x68C: o vídeo **não** a cobre. Ele fala de redução de dimensionalidade em geral (motivação, perda de informação e PCA) e nunca separa seleção de agregação.

## 2. Fichas por vídeo

### 10kmcTfoxiM — UNIVESP — Mineração de Dados: preparação e limpeza de dados (21:13) → proposto como **a3-v9**

- **Cobre:**
  - 00:00–03:00 dados brutos (KDD) e definições: objeto = linha, atributo = coluna.
  - 03:03–06:40 três tipos de problema numa tabela de exemplo: incompletude (objeto sem informação, cartão de crédito ausente), inconsistência (89 kg no campo estado civil, valor fora do domínio, ou bases diferentes com valores diferentes) e ruído (pessoa com doutorado e 10 anos).
  - 06:40–08:26 posição do pré-processamento no processo de KDD; alguns algoritmos só aceitam números.
  - 08:26–17:32 **dados faltantes (imputação)**: ignorar o objeto (serve se a base é grande), preencher manualmente (serve se é pequena), constante global do especialista, hot deck (copiar de um registro parecido em um atributo relacionado), valor da última observação, média ou moda (do atributo todo ou da classe), modelos preditivos e agrupamento, aproximação por regressão linear.
  - 17:32–20:30 **integração de bases**: redundância (data de nascimento e idade, que reduz a dimensionalidade), duplicidade e conflitos (quilômetros × milhas, "feminino" × "F").
- **Não cobre:** eliminar a coluna inteira (só fala em ignorar o objeto); quando usar cada alternativa além do tamanho da base; imputar só com estatísticas do treino; correlação para detectar redundância; caracterização com estatísticas descritivas (slide 3, 2º parágrafo); outliers, escala, codificação, PCA, balanceamento.
- **Divergências com o slide:** nenhuma que contradiga. Hot deck e última observação são extras; "constante global do especialista" corresponde ao "valor que indica ausência" do slide 6.
- **Nível e foco:** iniciante a intermediário. Aula expositiva de graduação, com slides e tabelas, sem código.
- **Idioma/qualidade:** português do Brasil, boa dicção; transcrição com poucos erros.
- **Trechos recomendados:** 03:03–06:40, 08:26–17:32, 17:32–20:30 (15:38).
- **Veredito: `aprovar só os trechos 03:03–06:40, 08:26–17:32 e 17:32–20:30`.** Preenche duas lacunas da rodada 1 (alternativas para dados faltantes e integração de bases). **Complementa o a3-v1** (que só cobre excluir ou imputar pela média) e não o substitui.

### 4hUNTJIEP5g — canal a confirmar — Tratamento de dados desbalanceados em Machine Learning (6:06) → proposto como **a3-v10**

- **Cobre:**
  - 00:00–01:50 undersampling: retirar registros da classe majoritária até igualar (100 laranja × 5 mil azuis); o risco é perder informação importante (01:00–01:40).
  - 01:50–02:45 oversampling: copiar a classe menor ou, melhor, gerar amostras sintéticas parecidas (45 anos gera 46 e 47).
  - 02:45–04:20 Tomek links (undersampling que apaga a maioria colada na minoria; fora dos slides).
  - 04:35–05:55 SMOTE: usa distância entre registros vizinhos da classe minoritária para criar exemplos sintéticos nos espaços vazios.
- **Não cobre:** por que o desbalanceamento prejudica (slide 48); sobreajuste por duplicação (slide 49); balancear só no treino; métrica adequada.
- **Divergências/erros:** (a) 01:00 fala em manter 500 azuis para igualar a 100 laranja (seriam 100). (b) 04:40 diz que o SMOTE "faz a cópia", mas em 05:00 explica corretamente que cria registros sintéticos. A frase confundia menos que a do Pwl no a3-v8 ("copia e cola"), porque aqui a correção vem em seguida.
- **Nível e foco:** iniciante; só conceito, com figuras de pontos azuis e laranja; sem código.
- **Idioma/qualidade:** português do Brasil, fala clara; transcrição boa.
- **Trechos recomendados:** 00:00–02:45 e 04:35–05:55 (4:05).
- **Veredito: `aprovar só os trechos 00:00–02:45 e 04:35–05:55`.** Fecha parte da lacuna do slide 49 (perda de informação na subamostragem) e a do SMOTE como exemplo sintético. **Complementa o a3-v8**, que deve vir depois dele.

### 6as06vtXNL8 — Data School (a confirmar) — "fit_transform on training data, transform only on testing/new data" (4:19, inglês) → proposto como **a3-v11**

- **Cobre:**
  - 00:00–01:00 regra: no treino `fit_transform`; no teste ou dado novo, só `transform`.
  - 01:00–02:30 por quê: mesmas transformações nos dois conjuntos (o one-hot aprende as colunas C, Q, S no treino e as recria no teste).
  - 02:30–03:15 o imputador aprende a média (31,2) no treino e usa esse valor no teste.
  - 03:15–04:15 usar a média do teste é vazamento de dados (data leakage) e invalida a estimativa de desempenho.
- **Não cobre:** scaler, limites de outliers e PCA como exemplos (a regra vale para todos, conhecimento externo); balanceamento; código completo ou `Pipeline`.
- **Divergências:** nenhuma; concorda com os slides 13 e 18.
- **Nível e foco:** iniciante a intermediário (pressupõe `fit` e `transform` do scikit-learn); conceito, sem tela de código.
- **Idioma/qualidade:** inglês claro e pausado; transcrição com poucos erros.
- **Trechos recomendados:** o vídeo inteiro (4:18).
- **Veredito: `aprovar (vídeo inteiro)`.** Inglês só é aceitável aqui por ser claramente superior: **não há vídeo em português** que mostre o `fit` só no treino com o `transform` no teste (os da rodada 1 vazam ou mostram o princípio só para imputação e balanceamento). Fecha a lacuna 6. A leitura deve acrescentar o scaler e o PCA.

### RF6sg0ozloE — Mahesh Huddar — Partitioning in Data Mining (equal width, equal frequency, clustering) (8:04, inglês) → proposto como **a3-v12**

- **Cobre:**
  - 00:00–00:37 partitioning = converter dado numérico em categórico, sem usar o rótulo; três técnicas.
  - 00:37–01:43 mesma frequência (equidepth): ordenar e agrupar de 4 em 4 valores.
  - 01:43–03:08 larguras iguais: largura = (máx − mín) / n; exemplo com mín 5, máx 215, n = 3 e largura 70.
  - 03:08–07:40 agrupamento por K-means, com iterações à mão (fora dos slides).
- **Não cobre:** rótulos dos intervalos (baixo, médio, alto), que o slide 21 pede; como escolher o número de intervalos; perda de informação ao discretizar.
- **Divergências:** nome ("partitioning" no lugar de discretização/binning) e o acréscimo da mesma frequência e do K-means, além das larguras iguais que o slide cita.
- **Nível e foco:** iniciante; cálculo à mão com números na tela; sem código.
- **Idioma/qualidade:** inglês com sotaque marcado; a transcrição troca números no fim do exemplo ("255" por 215).
- **Trechos recomendados:** 00:00–03:08 (3:08).
- **Veredito: `aprovar só o trecho 00:00–03:08`**, com aviso de que está em inglês. Qualidade apenas mediana; é o único que toca a discretização (lacuna 8), mas a leitura ainda precisa mostrar o rótulo dos intervalos.

### 9Tf-_mJhOkU — canal a confirmar — The Curse of Dimensionality (8:06, inglês) → proposto como **a3-v13**

- **Cobre:**
  - 00:00–01:05 intuição: nove pontos cobrem bem uma reta, deixam lacunas num quadrado e quase não preenchem um cubo; o espaço fica esparso.
  - 01:05–03:55 geometria: distância do centro ao canto cresce (√2, √3, √10, √100), volume da hiperesfera (matemática; fora da prova).
  - 03:59–04:47 por que importa em AM: os dados necessários crescem de forma exponencial (5 pontos em 1D, 25 em 2D).
  - 04:47–05:55 distâncias perdem sentido; vetores aleatórios ficam quase perpendiculares (extra).
  - 05:57–07:12 como lidar: reduzir dimensões (PCA, UMAP), selecionar atributos, algoritmos próprios, regularização, mais dados; e a ressalva de que às vezes a alta dimensão ajuda (kernels).
- **Não cobre:** o tempo computacional do slide 22 (está em x68C); atributos ruidosos, irrelevantes e redundantes; seleção × agregação; vantagens e desvantagens.
- **Divergências:** nenhuma com o slide 23, que é a mesma ideia (mais atributos exigem mais amostras). A ressalva final (07:00) vai além do slide.
- **Nível e foco:** iniciante nos trechos recomendados; o resto exige matemática. Só conceito, com animações.
- **Idioma/qualidade:** o áudio é inglês; a transcrição local saiu **misturada** (trechos traduzidos e trechos em inglês, o campo `lang` diz `pt`) e com erros ("curto" = curse). Conferir se há legenda em português no YouTube.
- **Trechos recomendados:** 00:00–01:08, 03:59–04:47, 05:57–07:12 (3:11).
- **Veredito: `aprovar só os trechos 00:00–01:08, 03:59–04:47 e 05:57–07:12`**, com aviso de inglês. Nenhum candidato em português explica que os dados necessários crescem exponencialmente (slide 23).

### x68CrD6AZhY — Rio (canal a confirmar) — 10 – Fundamentos do Aprendizado de Máquina: Redução de Dimensionalidade (15:16) → proposto como **a3-v14**

- **Cobre:**
  - 00:00–01:00 alta dimensão é difícil de entender e cara; a redução procura fatores latentes.
  - 01:00–02:00 ganhos (visualização, menor custo) e custo (perda de informação).
  - 02:00–03:15 a maioria dos algoritmos piora com menos dimensões, salvo os baseados em instância (KNN) por causa da maldição da dimensionalidade (dados esparsos, distância difícil).
  - 03:15–10:30 PCA com álgebra linear (padronizar, covariância, autovalores, projetar) e demonstração 2D → 1D.
  - 10:38–12:45 base de diabetes com 10 dimensões; PCA a 3, 2 e 1 para visualizar.
  - 12:45–15:10 regressão linear antes e depois: o erro cresce conforme reduz; trade-off entre interpretação visual e custo menor × perda de desempenho.
- **Não cobre:** seleção × agregação; atributos irrelevantes e redundantes; a explicação da maldição (só a cita).
- **Divergências/ressalvas:** (a) "ganho de interpretabilidade" é só visual, e ele próprio diz (14:00) que os atributos novos não são os originais; o slide 31 destaca a perda dos valores originais e a preferência por seleção em finanças e medicina. (b) Diz que KNN pode ganhar desempenho com a redução: não está nos slides. (c) Os erros da demonstração aparecem na transcrição como "0,37, 42, 43, 45" (provavelmente 0,37 → 0,42 → 0,43 → 0,45).
- **Nível e foco:** iniciante a intermediário nos trechos recomendados; o miolo (PCA) exige álgebra linear.
- **Idioma/qualidade:** português do Brasil, fala clara; transcrição com erros de termos ("alto-vetor").
- **Trechos recomendados:** 00:00–03:18 e 10:38–15:15 (7:55).
- **Veredito: `aprovar só os trechos 00:00–03:18 e 10:38–15:15`.** Melhor cobertura em português para vantagens × desvantagens (slides 22, 24, 25), com a perda de desempenho mostrada em números. **Complementa o a3-v6** (PCA) e o a3-v13 (maldição).

### xD9-t4JmJm0 — Didática Tech (a confirmar; a transcrição diz "didático ATEC") — O que é normalização e para que serve (10:36) → proposto como **a3-v15** (opcional)

- **Cobre:**
  - 00:40–04:45 exemplo de três homens (altura em m, peso em kg): a regra "altura + peso" classifica o terceiro como porte pequeno contra a intuição.
  - 04:45–06:30 diagnóstico: o peso varia dezenas e a altura ~0,5, então a altura quase não conta (é o slide 14).
  - 06:30–08:00 correção: dividir cada valor pela média do atributo.
  - 08:00–10:25 o terceiro agora fica perto do grupo grande; conclusão: trazer os atributos à mesma ordem de grandeza.
- **Não cobre:** min-max, padronização, quais algoritmos são sensíveis, outliers, KNN pelo nome.
- **Divergências:** a "normalização" ensinada é **valor / média**, que não é a do slide 15 (min-max) nem a do 16 (padronização); chama-a de "a mais comum" (não é). A regra "somar" não é um algoritmo real.
- **Nível e foco:** iniciante; só conceito; tabela de 3 linhas.
- **Idioma/qualidade:** português do Brasil, fala lenta e repetitiva; transcrição com erros pequenos.
- **Trechos recomendados:** 00:40–10:25 (9:45).
- **Veredito: `aprovar só os trechos 00:40–10:25`, como complemento opcional do a3-v3**, com `warnings` sobre a fórmula. Dá o exemplo mais concreto para o slide 14; o a3-v3 continua como principal para min-max e padronização.

### w08ja_6lXe8 — PPGC UFSC (R na Pesquisa Contábil) — Tratamento de Outlier (Winsorização) (15:34) → proposto como **a3-v16**

- **Cobre:**
  - 00:00–02:39 estatísticas descritivas e gráficos de uma variável contábil: média −3,96 contra mediana 0,58 (outliers negativos arrastam a média).
  - 02:39–04:42 winsorização: valores abaixo do percentil 1% (−89) são trocados por −89, acima do 99% por 8,85; o mesmo a 5%. Vantagem: não remove observações.
  - 04:42–12:25 código em R (pacote `psych`) e comparação de resumo, histograma e boxplot (5% melhora mais que 1%).
  - 12:25–15:20 lista dos valores antes e depois: o −249 virou −89 (1%) e −10 (5%); "não é remoção, é substituição".
- **Não cobre:** o limite pelo IQR do exemplo do slide 13; quando preferir remover ou manter; fazer só no treino; Python.
- **Divergências:** o limite é percentil (1%/5%), não IQR. A ideia (trocar o extremo pelo limite) é a do slide.
- **Nível e foco:** intermediário (assume percentil, média e mediana); conceito em 2 minutos e o resto é tutorial de R.
- **Idioma/qualidade:** português do Brasil, fala clara; transcrição com muitos erros ("insorização", "otilai").
- **Trechos recomendados:** 02:39–04:52 e 12:25–15:20 (5:08).
- **Veredito: `aprovar só os trechos 02:39–04:52 e 12:25–15:20`.** É o único vídeo sobre winsorização (lacuna 3), de qualidade média e com contexto de pesquisa contábil; a leitura precisa mostrar o exemplo do slide (limite 5.000 pelo IQR).

### Y_4dWhMmaGg — Zmove Academy — Boxplot Explicado: Quartis, Percentis e Outliers (11:44) → proposto como **a3-v17** (opcional)

- **Cobre:**
  - 00:50–04:05 percentis (100 partes) e quartis (4 partes de 25%); Q1, Q2 = mediana e Q3 numa curva de densidade de alturas.
  - 04:05–07:55 `quantile` e `describe` em pandas (cortado).
  - 07:56–09:30 leitura do boxplot: a caixa vai de Q1 a Q3 e concentra 50% dos dados; a linha central é a mediana.
  - 09:30–11:08 IQR = Q3 − Q1; limites Q3 + 1,5×IQR e Q1 − 1,5×IQR; caixa estreita = dados concentrados.
- **Não cobre:** Z-score; por que o IQR é robusto; o que fazer com os outliers; tratar só no treino.
- **Divergências/ressalvas:** descreve as hastes como o limite do aceitável; na prática elas vão ao último dado dentro do limite (conhecimento externo). Não contradiz o slide 11.
- **Nível e foco:** iniciante; parte de zero (o que é um quartil), com gráficos interativos.
- **Idioma/qualidade:** português do Brasil, fala clara; transcrição boa.
- **Trechos recomendados:** 00:50–04:05 e 07:56–11:08 (6:27).
- **Veredito: `aprovar só os trechos 00:50–04:05 e 07:56–11:08`, como complemento opcional do a3-v2** (para quem não domina quartis, assistir **antes** dele). O a3-v2 continua principal por trazer Z-score e a regressão com e sem outliers.

### o3uTAZyROI8 — Prof. Fernanda Maciel — Excluir Outliers? Usar média ou mediana? (3:31) → proposto como **a3-v18** (opcional)

- **Cobre:**
  - 00:00–02:00 outlier = valor extremo; pode ser real (salário de 10 mil) ou erro (idade 300, salário de 500 mil).
  - 02:00–03:31 se for erro, remove; se for representativo, **mantém**. Com outliers a média é distorcida (7.444, puxada pelo presidente) e se usa a mediana (4.500).
- **Não cobre:** winsorização; algoritmos robustos; IQR e Z-score; treino e teste.
- **Divergências:** nenhuma. Só a mediana é oferecida como alternativa; o slide 13 fala em winsorizar ou manter com algoritmos robustos.
- **Nível e foco:** iniciante; só conceito; recorte de aula maior (começa em "agora, uma outra coisa" e se refere a uma tabela de salários mostrada antes).
- **Idioma/qualidade:** português do Brasil, fala clara; transcrição boa.
- **Trechos recomendados:** o vídeo inteiro (3:31).
- **Veredito: `aprovar (vídeo inteiro)`, como complemento opcional do a3-v2.** Explica de modo simples por que manter o outlier real (slide 13) e por que a mediana é robusta e a média não (slide 12), que o a3-v2 só toca de leve.

### dcXwhVkpYNI — canal a confirmar — Outliers utilizando Z-Scores (6:11) → proposto como **a3-v19** (opcional)

- **Cobre:**
  - 00:00–01:00 outlier = valor distante dos demais; pode ser variabilidade natural ou erro de medida.
  - 01:00–03:05 Z = (x − média) / desvio padrão; sinal e significado; outlier se Z > 3 ou Z < −3.
  - 03:13–05:10 exemplo 1 (125 num conjunto de 8 valores: Z = 2,46, **não** é outlier) e exemplo 2 (nota 786, média 512, desvio 85: Z = 3,25, é outlier).
- **Não cobre:** a regra 68-95-99,7 e a distribuição normal; sensibilidade do Z-score a outliers; IQR × Z-score.
- **Divergências:** nenhuma; menos completo que o a3-v2 no slide 9. A transcrição acaba no segundo exemplo, depois de anunciar "12 exercícios".
- **Nível e foco:** iniciante; só conceito e conta no quadro.
- **Idioma/qualidade:** português do Brasil, fala pausada; transcrição boa.
- **Trechos recomendados:** o vídeo inteiro (6:11).
- **Veredito: `aprovar (vídeo inteiro)`, como complemento opcional do a3-v2** (trecho 10:30–16:10 do CLN). Explica melhor o sinal de Z e dá dois exemplos; fraco por não citar 68-95-99,7. Opcional, não essencial.

## 3. Descartados

- **p_SmODmFRUw — Universo Discreto — Preencher dados faltantes (17:48).** Cerca de 4 dos primeiros minutos são sobre o "reboot do canal" e o resto é tutorial de código com `SimpleImputer` (média e mediana) sobre uma planilha de canais do YouTube. Não apresenta o conceito nem as alternativas do slide 6, não menciona treino e teste (ajusta na base inteira) e não acrescenta nada ao slide além de "preencher com a média". O 10kmc (UNIVESP) e o a3-v1 cobrem o assunto melhor. **Descartar.**

Nenhum outro vídeo foi descartado: todos os demais têm ao menos um trecho que explica de fato um tópico do slide, com `warnings` onde a explicação diverge.

## 4. Sequência proposta (ordem dos slides), com o que já existe

| Slides | Item | Vídeo | Trechos | Tempo | Observação |
| :-- | :-: | :-- | :-- | :-: | :-- |
| 3–4, 7 | a3-v9 | 10kmcTfoxiM | 03:03–06:40 · 08:26–17:32 · 17:32–20:30 | 15:38 | **Novo.** Problemas dos dados, dados faltantes e integração. Vem antes do a3-v1. |
| 6–8, 13 | a3-v1 | SNd_qoGUEOE | 00:40–08:15 | 7:35 | Já existe. |
| 8, 10 | a3-v17 | Y_4dWhMmaGg | 00:50–04:05 · 07:56–11:08 | 6:27 | **Novo, opcional.** Quartis e boxplot, antes do a3-v2. |
| 9 | a3-v19 | dcXwhVkpYNI | 00:00–06:11 | 6:11 | **Novo, opcional.** Z-score passo a passo. |
| 7–13 | a3-v2 | CLN-y_4ZySw | os 3 trechos existentes | 18:20 | Já existe. |
| 12–13 | a3-v18 | o3uTAZyROI8 | 00:00–03:31 | 3:31 | **Novo, opcional.** Manter × remover; média × mediana. |
| 13 | a3-v16 | w08ja_6lXe8 | 02:39–04:52 · 12:25–15:20 | 5:08 | **Novo.** Winsorização. |
| 13, 18 | a3-v11 | 6as06vtXNL8 | 00:00–04:18 | 4:18 | **Novo, em inglês.** Ajustar só no treino. |
| 14 | a3-v15 | xD9-t4JmJm0 | 00:40–10:25 | 9:45 | **Novo, opcional.** Intuição da escala (antes do a3-v3). |
| 14–17 | a3-v3, a3-v4 | NEY0, -L8 | os existentes | 18:15 | Já existem. |
| 19–20 | a3-v5 | RWaMw02_MQQ | os existentes | 10:05 | Já existe. |
| 21 | a3-v12 | RF6sg0ozloE | 00:00–03:08 | 3:08 | **Novo, em inglês.** Discretização. |
| 22–23 | a3-v13 | 9Tf-_mJhOkU | 00:00–01:08 · 03:59–04:47 · 05:57–07:12 | 3:11 | **Novo, em inglês.** Maldição. |
| 22, 24–25 | a3-v14 | x68CrD6AZhY | 00:00–03:18 · 10:38–15:15 | 7:55 | **Novo.** Vantagens × desvantagens da redução. |
| 22–47 | a3-v6, a3-v7 | p4bv, ZqEh | os existentes | 26:30 | Já existem (PCA). |
| 49–51 | a3-v10 | 4hUNTJIEP5g | 00:00–02:45 · 04:35–05:55 | 4:05 | **Novo.** Over e undersampling, SMOTE. Antes do a3-v8. |
| 48–51 | a3-v8 | PwlKbdsVsiY | os existentes | 14:10 | Já existe. |

Tempo dos novos: obrigatórios (a3-v9, v10, v11, v12, v13, v14, v16) **43:23**; opcionais (a3-v15, v17, v18, v19) **25:54**; total **69:17**.

## 5. Substituições e complementos em relação à rodada 1

- Nenhum item novo **substitui** um existente; todos complementam.
- **a3-v9 complementa o a3-v1** (ausentes: alternativas completas; integração de bases).
- **a3-v17, a3-v18 e a3-v19 complementam o a3-v2** (quartis; manter × remover; Z-score). O a3-v2 continua sendo o principal em slides 9 a 12.
- **a3-v11 complementa o a3-v1, o a3-v2, o a3-v3 e o a3-v8** (o princípio "só no treino" aplicado a imputação, outliers, escala e balanceamento).
- **a3-v15 complementa o a3-v3** (intuição antes de min-max e padronização).
- **a3-v13 e a3-v14 complementam o a3-v6** (motivação e vantagens × desvantagens antes do PCA).
- **a3-v10 complementa o a3-v8** (o que são over e undersampling e o SMOTE, antes de "balancear só no treino").

## 6. Lacunas que continuam sem vídeo bom (o material escrito precisa cobrir)

Estado das 13 lacunas da rodada 1:

1. **Caracterização dos dados com estatísticas descritivas (slide 3):** continua sem vídeo. A integração de bases (slide 4) passou a ter o a3-v9.
2. **Dados faltantes (slide 6):** **coberto** pelo a3-v9 (a única lacuna do slide 6, "eliminar a coluna", é citada no slide mas não no vídeo).
3. **Winsorização:** coberta (a3-v16, qualidade média, limite por percentil). **Manter + algoritmos robustos (árvores, random forest, boosting): continua sem vídeo**; o a3-v18 só cobre "manter o outlier real".
4. **IQR × Z-score (slide 12):** coberta pela metade. O a3-v18 explica que a mediana não é arrastada pelo extremo e a média é; ninguém junta isso à escolha entre IQR e Z-score nem diz que os dados assimétricos pedem IQR. A leitura deve fazer essa ligação.
5. **Ordem outliers → normalização (slide 18):** **continua sem vídeo.** Nenhum candidato novo toca no assunto; o único que citava (-L8) diz o contrário do slide.
6. **Ajustar só no treino na prática:** coberta em inglês (a3-v11) para imputação e one-hot; o `fit` do scaler, dos limites de outliers e do PCA continua só na leitura.
7. **Quais algoritmos precisam de escala (slide 17):** **continua sem cobertura boa.** O a3-v15 não fala nisso.
8. **Discretização (slide 21):** coberta só em inglês e mediana (a3-v12), sem os rótulos dos intervalos.
9. **Maldição da dimensionalidade (slides 22–23):** coberta (a3-v13 em inglês; a3-v14 em português, de passagem).
10. **Seleção × agregação (slides 26–30):** **continua sem vídeo**: atributos irrelevantes (Id, nome), redundantes por dedução (só a data de nascimento × idade, via a3-v9), correlação para achar redundância, e a preferência por seleção em finanças e medicina (slide 31, só tocada em a3-v14).
11. **PCA geométrico (slides 37–43, 45–46):** **continua só na leitura**, como na rodada 1. Também falta "combinação linear ou não linear" (slide 31).
12. **Sobreajuste por duplicar registros (slide 49):** **continua sem vídeo.** A perda de informação na subamostragem está no a3-v10 e o SMOTE como exemplo sintético está no a3-v10.
13. **Figuras dos slides (8, 9, 10, 12 etc.):** inalterado; a leitura deve descrever o que cada gráfico mostra.

Resumo: continuam sem vídeo bom as lacunas 1 (caracterização), 3 (algoritmos robustos), 4 (ligação IQR × Z-score), 5 (ordem outliers → escala), 7 (algoritmos que precisam de escala), 10 (seleção × agregação), 11 (PCA geométrico) e 12 (sobreajuste por duplicação). Para as lacunas 8, 9 e 6, o vídeo existe mas está em inglês (ou só cobre parte); a leitura ainda precisa repetir a explicação.
