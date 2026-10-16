# Validação dos vídeos pela transcrição — Aula 3 (Pré-processamento)

Método: li a transcrição inteira (legenda automática em português, com erros) de cada um dos 10 vídeos e comparei com os 51 slides de `Aulas/Aula 3 - Pré-Processamento` (texto em `estudo/_fontes_extraidas/`). Os tempos `mm:ss` têm precisão de cerca de ±15 s (a legenda vem em blocos). Termos que a legenda automática erra e que aparecem nas transcrições: "alto valor/al vetor" = autovalor/autovetor; "outliner/outlar/ao tilar" = outlier; "esmalte/smooth" = SMOTE; "viés/enviesado" é usado de forma solta. Tudo abaixo vem de trechos lidos; quando aponto um erro do vídeo que depende de conhecimento meu (fora do vídeo), isso está marcado como "(conhecimento externo)".

Legenda da matriz: **B** = cobre bem · **P** = cobre parcialmente · **–** = não cobre · **X** = cobre de forma que diverge do slide ou está errado.

## 1. Matriz tópicos dos slides × vídeos

| Tópico (slides) | SNd Análise Macro | CLN Máq. Intelig. | 1hMt Tudo Mais Const. | NEY0 Nerd dos Dados | -L8 Eduardo escala | RWaM Eduardo encoder | p4bv Eduardo PCA | Pwl Let's Data | CS9g Menino dos Dados | ZqEh Data ICMC |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Caracterização/estatísticas descritivas, integração de bases (3–4) | – | – | P | P | – | – | – | – | – | – |
| Dados faltantes e alternativas (6) | P | – | – | – | – | – | – | – | – | – |
| Outliers: o que são, ruído (7–8) | P | B | P | – | – | – | – | – | – | – |
| Z-score, regra 68-95-99,7, limite ±3 (9) | – | B | – | – | – | – | – | – | – | – |
| IQR e regra 1,5×IQR (10–11) | B | B | B | – | – | – | – | – | – | – |
| IQR × Z-score: qual usar (12) | – | P | – | – | – | – | – | – | – | – |
| Remover × winsorizar × manter + algoritmos robustos (13) | P | P | – | – | – | – | – | – | – | – |
| Tratar outliers (e imputar) só no treino (13) | P | P | – | – | – | – | – | – | – | – |
| Mudança de escala: por quê (14) | – | – | – | B | B | – | P | – | – | – |
| Min-max (15) | – | – | – | B | B | – | – | – | – | – |
| Padronização (16) | – | – | – | B | B | – | P | – | – | – |
| Quais algoritmos precisam de escala (17) | – | – | – | P | P | – | – | – | – | – |
| Ordem: outliers antes da normalização (18) | – | – | – | – | X | – | – | – | – | – |
| Simbólico→numérico: ordinal × nominal (19) | – | – | – | – | – | P (com erro) | – | – | X | – |
| One-hot (20) | – | – | – | – | – | B | – | – | X | – |
| Numérico→simbólico: discretização (21) | – | – | – | – | – | – | – | – | – | – |
| Maldição da dimensionalidade (22–23) | – | – | – | – | – | – | P | – | – | – |
| Vantagens × desvantagens da redução (24–25) | – | – | – | – | – | – | P | – | – | P |
| Seleção × agregação; irrelevantes/redundantes/correlação (26–30) | – | – | – | – | – | – | P | – | – | – |
| PCA: ideia, pré-requisitos (numérico, padronizado), PC = combinação linear (30–36) | – | – | – | – | – | – | B | – | – | P |
| PCA: mecânica geométrica (centrar, reta, soma dos quadrados) (37–43, 45–46) | – | – | – | – | – | – | P | – | – | P |
| Autovalores/autovetores, ortogonalidade, escolher componentes (44, 47) | – | – | – | – | – | – | P | – | – | B |
| Desbalanceamento: o problema (48) | – | – | – | – | – | – | – | B | P | – |
| Over/undersampling (49–51) | – | – | – | – | – | – | – | P | P (só SMOTE, com erro) | – |
| Ajustar estatísticas/balancear só no treino (vazamento) | P (com ressalva) | P | – | X | X | – | – | B (balanceamento) | X | – |

Leitura rápida: a matriz tem muitos "–" porque nenhum vídeo cobre a aula inteira; cada um cobre um bloco. Os blocos mais bem servidos são IQR/Z-score (CLN), escala (NEY0), one-hot (RWaM), PCA (p4bv + ZqEh) e balanceamento (Pwl).

## 2. Fichas por vídeo

### SNd_qoGUEOE — Análise Macro — Pré-processamento: valores extremos e valores ausentes (31:00)

- **Cobre:**
  - 00:40–03:00 vazamento de dados (data leakage) explicado com exemplo de série temporal: calcular algo na amostra completa e só depois separar treino/teste "contamina" o treino.
  - 03:00–05:30 valores extremos: remover linha ou coluna, substituir por média/mediana/valor arbitrário/método estatístico ou de AM, ou criar variável dummy indicando o extremo.
  - 05:30–06:30 recomenda tratar com separação treino/teste.
  - 06:30–08:15 valores ausentes: excluir linha (ou coluna, conforme a proporção) ou imputar (estatística descritiva, valor de cima, valor de baixo, valor arbitrário).
  - 10:30–15:00 (R) e 24:30–29:00 (Python) boxplot e regra Q1 − 1,5×IQR / Q3 + 1,5×IQR (cita que "algumas pessoas usam 3"), aplicada filtrando linhas.
  - 15:30–19:30 (R) e 29:00–30:30 (Python): proporção de ausentes (57%) e imputação pela média do treino; mostra que a imputação muda a distribuição (média igual, mediana e quartis mudam).
- **Não cobre:** Z-score; winsorização; IQR × Z-score; manter com algoritmos robustos; escala; ordem outliers → normalização; as alternativas de ausentes "preencher manualmente", "valor que indica ausência", "moda" e "prever com AM" (esta última só aparece citada para outliers, em 04:30). Nenhum tema de encoding, PCA, balanceamento.
- **Divergências/ressalvas em relação ao slide:**
  - Diz "aplica o processamento individualmente nessas amostras" (06:00) e "faz o mesmo procedimento depois para a amostra de teste" (02:00): isso soa como calcular a estatística separadamente no teste. O correto (e o que o slide 13 pede) é calcular os limites/médias só no treino. Na demo em R (18:00–18:30) ele diz que usa a média do treino também no teste, mas a fala é ambígua; no trecho Python (30:00) a legenda está confusa.
  - A regra IQR é atribuída a "um livro de 2021" e ele mostra que "removendo, sempre aparece novo outlier" (14:30, 28:30): comentário útil, não está no slide.
- **Nível e foco:** intermediário. Pressupõe saber o que são amostra de treino/teste, variável preditiva e modelo; vocabulário de econometria ("variáveis exógenas", "dummy", "fora da amostra"). Mistura conceito (00:00–08:30) e código (R 08:30–20:00, Python 20:00–31:00, o mesmo roteiro repetido). A parte conceitual é só 8 min.
- **Idioma/qualidade:** português do Brasil, fala clara; a legenda erra muito, mas dá para acompanhar. Parte do código usa um arquivo de 1 GB do IBGE (não reproduzível sem baixar), irrelevante para a prova.
- **Trecho recomendado:** 00:40–08:15 (7:35).
- **Veredito: `aprovar só os trechos 00:40–08:15`** (opcional: 15:30–19:30 para ver imputação pela média do treino e o efeito na distribuição). Assistir já avisado da ressalva sobre "processar cada amostra individualmente".

### CLN-y_4ZySw — Máquinas Inteligentes — Detecção e remoção de outliers (34:28)

- **Cobre:**
  - 00:30–02:30 o que é outlier, com dois exemplos: erro de digitação (temperatura 73,2 em vez de 37,2) e caso natural (renda familiar após ganhar na loteria); manter × remover depende do problema (detecção de intrusão: querer detectar, não remover).
  - 04:20–10:30 IQR: boxplot, quartis, limites Q1 − 1,5×IQR e Q3 + 1,5×IQR, constante 1,5 como padrão (código numpy).
  - 10:30–16:10 Z-score: fórmula (valor − média)/desvio, interpretação do sinal, 68%/95%/99,7%, limiar de 3 desvios, código; e os cuidados: supõe distribuição normal, ruim com poucos dados (< 10) e sensível a muitos outliers extremos (12:30–13:00).
  - 29:45–33:45 demonstração de que outliers atrapalham regressão linear: remove outliers só do conjunto de treino (31:30–32:30) e o erro médio absoluto no teste cai.
- **Também cobre, fora do slide:** métodos multivariados (EllipticEnvelope, Isolation Forest) de 16:10 a 29:30. É conteúdo extra; pular.
- **Não cobre:** winsorização; algoritmos robustos (árvores etc.) como alternativa; ordem outliers → normalização; dados faltantes; resto da aula.
- **Divergências/ressalvas:**
  - IQR × Z-score fica incompleto: ele diz que o Z-score depende de normalidade e é sensível a outliers, mas não explica que mediana e quartis são robustos e a média não (slide 12). Em 04:00 a legenda atribui "suposição gaussiana" de forma ambígua ao IQR/"seis for" (provavelmente Z-score); em 06:00–06:30 diz que o IQR é "adequado ao caso univariado".
  - Na regressão (31:30) ele remove outliers do treino com Isolation Forest, coerente com o slide 13.
- **Nível e foco:** iniciante a intermediário, bom para engenheiro de software (código simples em numpy). Foco misto conceito + código Python (numpy/sklearn, sem pandas). Fala pausada e didática, ele mesmo avisa que escreve "da forma mais didática possível".
- **Idioma/qualidade:** português do Brasil, boa explicação; legenda com muitos erros de nomes.
- **Trechos recomendados:** 00:00–02:30, 04:20–16:10, 29:45–33:45 (18:20).
- **Veredito: `aprovar só os trechos 00:00–02:30, 04:20–16:10 e 29:45–33:45`.** É o melhor vídeo para slides 7–13.

### 1hMt-X2VYBk — Tudo Mais Constante — Python e IQR (18:47)

- **Cobre:** EDA de altura/peso (describe, histogramas, correlação; 03:00–09:30); boxplot e leitura do IQR como a "caixinha" entre Q25 e Q75 (10:00–12:30); função em numpy/pandas com limites Q1 − 1,5×IQR e Q3 + 1,5×IQR (13:30–15:00); aplica a peso, altura e IMC (15:00–18:00).
- **Não cobre:** o que fazer com os outliers (só os lista); Z-score; remover × winsorizar × manter; tratar só no treino; qualquer outro tópico.
- **Divergências:** nenhuma factual; erros de fala corrigidos por ele mesmo (16:30). O vídeo é principalmente EDA com muita conversa e repetição.
- **Nível e foco:** iniciante; foco em código pandas/matplotlib/seaborn. Mais da metade do tempo vai para gráficos que não estão nos slides.
- **Idioma/qualidade:** português do Brasil, descontraído; legenda razoável.
- **Veredito: `descartar`.** Tudo o que serve (IQR, regra 1,5) está melhor em CLN e SNd; este não acrescenta nada para a prova. Se quiser um segundo exemplo de código de IQR, só 13:30–15:00.

### NEY0TrvHRoU — Nerd dos Dados — Normalização e padronização (guia completo) (42:31)

- **Cobre:**
  - 00:30–03:30 por que escalas diferentes atrapalham; só alguns algoritmos são sensíveis (KNN, SVM; árvores e random forest quase não são, mas o tempo de processamento muda).
  - 04:00–09:30 exemplo numérico à mão com KNN: distância euclidiana com dados originais classifica o ponto B como "forte".
  - 09:30–13:30 fórmula do min-max (x − min)/(max − min) e resultado sempre entre 0 e 1; "não muda o valor da variável, muda a escala".
  - 13:30–16:30 o mesmo cálculo com dados normalizados muda a classificação (vira "médio"), mostrando que a escala altera o resultado do algoritmo de distância.
  - 16:30–21:30 padronização (x − média)/desvio, resultando em média 0 e desvio 1, sem limite fixo (20:00); mesmo efeito na classificação.
  - 21:53 em diante: "qual escolher?" Resposta: testar os dois (38:30–39:30, 41:00–41:30). Demo com `StandardScaler` e `MinMaxScaler` (22:17–31:30), KNN: acurácia de 67% (original) para 91% (escalado) (34:00–36:30); SVM: 90% para 92% (39:30–40:30); redes neurais também são sensíveis (38:30).
- **Não cobre:** sensibilidade a outliers e ordem outliers → escala (slide 18); algoritmos "baseados em gradiente" do slide 17 (só cita redes neurais e SVM); regra de quando usar uma ou outra, além de "teste os dois".
- **Divergências/erros:**
  - **Vazamento de dados:** ajusta o scaler no DataFrame inteiro (27:00, 29:30) e só depois faz `train_test_split` (32:00). O correto é ajustar o scaler só no treino e aplicar ao teste (conceito do slide 13/"ajustar só no treino"). Não avisa disso.
  - 20:00–20:30 diz que, por ter média 0 e desvio 1, "aqui temos uma distribuição normal": isso está errado (conhecimento externo: padronizar não torna os dados normais); ele se corrige em seguida ("não garante simetria", 20:30). Ignorar a frase.
  - Atribui a falta de escala a "viés/overfitting" (01:00, 14:30, 32:00): impreciso. O problema é que atributos de maior magnitude dominam o cálculo de distância/gradiente; overfitting é outro conceito.
  - 39:00 "nunca treine sem normalizar ou padronizar" contradiz o que ele mesmo disse em 02:30 (árvores quase não ligam).
  - Padroniza a coluna alvo "para mostrar" (28:30) e depois explica que não se faz em classificação (34:30–35:30).
- **Nível e foco:** iniciante; ótimo para quem não conhece a área porque faz a conta passo a passo e depois usa scikit-learn. Mais ou menos meio a meio conceito/código; o código (22:17–41:00) é tutorial de sklearn (pandas, StandardScaler, MinMaxScaler, train_test_split, KNN, SVM).
- **Idioma/qualidade:** português do Brasil, explicação clara e lenta, com bastante repetição; há propaganda no fim.
- **Trechos recomendados:** 00:30–03:30 e 09:30–22:15 (omitir 20:00–20:30), 15:15 no total.
- **Veredito: `aprovar só os trechos 00:30–03:30 e 09:30–22:15`**, com as ressalvas acima (e opcional 34:00–36:30 para ver o efeito na acurácia, sabendo que o código vaza).

### -L8MacYRWGM — Eduardo (Ciência dos Dados) — Diferença entre normalização e padronização (33:08)

- **Cobre:** redimensionar não muda os dados, só a escala (02:30–03:30); KNN com atributos de escalas diferentes e a distância euclidiana (04:00–08:30); fórmula min-max (18:30–19:30) e padronização (10:00–10:30), cálculo no Excel (11:00–17:30); "quando usar" (18:10–19:00): normalização quando os dados não são gaussianos (KNN, redes neurais), padronização quando são gaussianos, mas "não precisa ser necessariamente verdade"; "depende do algoritmo, teste e escolha o melhor" (22:07–23:30); gradiente descendente, regressão, redes neurais e distâncias se beneficiam da escala (24:30–25:30); demo em sklearn com KNN (28:00–31:30): sem escala 71%, padronizado 73,9%, min-max 73,8%.
- **Não cobre:** ordem outliers → escala; Z-score; quais algoritmos de árvore não precisam (cita árvores em 03:30, de passagem).
- **Divergências/erros:**
  - 18:30–20:30: a explicação sobre outliers está confusa e contrária ao slide 18. A legenda diz que, mesmo com valores discrepantes, "os dados não serão afetados pela padronização", e o teste com 1 milhão conclui que o min-max "travou os outliers". O slide diz que as duas técnicas são extremamente sensíveis a valores extremos. Não assistir esse trecho.
  - 28:00–30:30: escala todo o X antes da validação cruzada (vazamento) e não comenta.
  - 02:00: dá "cor do carro" como exemplo de variável numérica (descuido).
- **Nível e foco:** iniciante, formato de diálogo ("Eduardo, me explica"), longo e cheio de enchimento; Excel e depois sklearn. Conceito 60% / código 40%.
- **Idioma/qualidade:** português do Brasil; muito informal; legenda ruim em vários trechos.
- **Veredito: `aprovar só os trechos 18:10–18:45, 22:05–23:30 e 24:30–25:30`** como complemento do NEY0 (regra de escolha e algoritmos). O resto do vídeo é redundante com NEY0 e tem o trecho confuso de outliers.

### RWaMw02_MQQ — Eduardo (Ciência dos Dados) — LabelEncoder × One-Hot (32:11)

- **Cobre:** por que o computador precisa de números (03:30–07:30); tipos de variável: numérica, categórica, nominal (professor, médico, advogado: sem ordem) × ordinal (júnior, pleno, sênior) (07:50–10:15); LabelEncoder = numeração em ordem alfabética (10:30–11:30, demonstrado em 14:00–16:30); problema: a ordem alfabética cria uma ordem falsa em categorias nominais (16:30–17:50); One-hot cria uma coluna 0/1 por categoria e cada linha tem exatamente um 1 (17:50–23:00); "dummy variable trap"/multicolinearidade e VIF com statsmodels (23:30–29:00); resumo de quando usar (29:50–31:00): one-hot para nominal com poucas categorias; LabelEncoder quando há ordem; com centenas de categorias, one-hot explode as colunas.
- **Não cobre:** discretização (numérico→simbólico); ordem correta de ordinais definida pelo analista (OrdinalEncoder); train/test (aplica na tabela inteira); resto da aula.
- **Divergências/erros:**
  - Recomenda `LabelEncoder` para ordinais (30:35, "júnior, pleno, sênior; primária, secundária, doutorado"), mas o próprio vídeo mostrou que ele numera por ordem alfabética (16:00). Para "primária/secundária/doutorado" a ordem alfabética (doutorado < primária < secundária) estaria errada. O slide 19 diz "converter para inteiros ordenáveis", isto é, respeitando a ordem do domínio. Observação (conhecimento externo): o `LabelEncoder` do sklearn foi feito para o alvo; para atributos ordinais usa-se mapeamento explícito ou `OrdinalEncoder` com a ordem declarada.
  - Ensina a remover uma coluna dummy para evitar multicolinearidade (24:00–29:00); o slide 20 descreve o código de c bits, uma coluna por valor. Conteúdo extra, não contradiz o conceito, mas não está nos slides.
- **Nível e foco:** iniciante, muito conversado; metade do vídeo é introdução/enchimento (00:00–07:30) e propaganda; código com pandas e sklearn.
- **Idioma/qualidade:** português do Brasil; legenda ruim, mas o conteúdo é compreensível.
- **Trechos recomendados:** 07:50–10:15, 16:30–23:00, 29:50–31:00 (10:05).
- **Veredito: `aprovar só os trechos 07:50–10:15, 16:30–23:00 e 29:50–31:00`**, ignorando a recomendação de LabelEncoder para ordinais.

### p4bvCFygfW0 — Eduardo (Ciência dos Dados) — PCA (28:49)

- **Cobre:**
  - 02:30–06:00 definição: reduzir dimensionalidade (de 3 variáveis para 2 componentes; imagens de 400 pixels).
  - 06:00–08:00 variabilidade explicada por componente (70%, 20%, 7%, 3%).
  - 08:00–11:30 por que reduzir: dimensões grandes são difíceis de treinar e exigem mais processamento e tempo; visualização impossível acima de 3 dimensões; limitação de memória; remove redundância/multicolinearidade; "minimiza perda de informação".
  - 09:16–10:30 requisitos: variáveis numéricas e dados padronizados (exemplo galões × km × anos-luz).
  - 11:30–14:00 definição como combinação linear; primeiro componente explica a variação máxima, o segundo explica a restante e não é correlacionado com o primeiro.
  - 14:15–14:45 componentes perpendiculares (90°).
  - 15:28–16:30 aparece "autovalor e autovetor" (álgebra linear), sem aprofundar.
  - 17:00–23:30 demo com Iris em sklearn (`PCA(n_components=2)`, `fit`, `explained_variance_ratio_`: 92% e 5%).
  - 25:00–27:00 resumo (componentes não correlacionados, escala importa, entrada numérica).
- **Observação importante:** o texto dos slides 35–36 ("Requisitos prévios", "Necessidade de redução de dimensionalidade", "um componente principal é uma combinação linear...") é quase a fala deste vídeo (09:16–15:00). Ou seja, este vídeo explica o que a professora escreveu.
- **Não cobre:** geometria dos slides 37–47 (centrar na origem, projetar, maximizar a soma dos quadrados das distâncias, autovalor = essa soma, escolher os maiores autovalores); só menciona autovalor/autovetor de passagem (15:28–16:30); perda de interpretabilidade e preferência por seleção em finanças/medicina (slide 31); seleção × agregação; maldição da dimensionalidade como nome.
- **Divergências/ressalvas:**
  - Diz que os dados "devem ser padronizados" (09:16, 25:30), mas a demo com Iris não padroniza (18:30–21:30).
  - 22:00: "trinta por cento" é lapso (o valor dito logo depois é 5%).
  - 25:30: "PCA funciona melhor com mais de três dimensões": frase solta, sem fundamento no resto.
  - Chama o PCA de "aprendizado não supervisionado" (19:40): correto.
- **Nível e foco:** iniciante, quase sem matemática; foco conceito (70%) + pequeno trecho de código sklearn. Pressupõe pouco.
- **Idioma/qualidade:** português do Brasil, formato de diálogo e enchimento no início (00:00–02:30) e no fim (28:00 em diante).
- **Trechos recomendados:** 02:30–15:00, 21:30–23:30 (14:30).
- **Veredito: `aprovar só os trechos 02:30–15:00 e 21:30–23:30`.** Melhor apresentação conceitual do PCA entre os candidatos.

### PwlKbdsVsiY — Let's Data — Classes desbalanceadas (47:10)

- **Cobre:**
  - 05:50–08:00 o que é classe desbalanceada (fraude bancária, diabetes) e por que a acurácia engana (um modelo que chuta "não fraude" acerta mais de 90%).
  - 08:10–09:30 formas de tratar: mudar a métrica, usar pesos por classe (class weight).
  - 09:30–10:30 oversampling (aumentar a minoritária copiando) e undersampling (reduzir a majoritária); o vídeo diz que o foco será oversampling, mas "a ideia funciona igual para o under".
  - 10:30–12:10 SMOTE.
  - 12:10–21:00 o ponto central do vídeo: o balanceamento só pode ser feito no treino, nunca na validação/teste, porque a validação simula o mundo real, que é desbalanceado. Fazer SMOTE antes da validação cruzada contamina os folds de validação e infla a acurácia. Explica folds (18:00–19:30) e que `cross_val_score` do sklearn não faz isso sozinho (19:56–21:00).
  - 21:00–43:30 código completo: validação cruzada "na mão" com `KFold` e SMOTE só no split de treino, comparado ao jeito errado (resultado do jeito errado ~80% × ~74% do certo; 40:00–42:30). Usa dataset de diabetes (65%/35%), XGBoost.
- **Não cobre:** as ressalvas do slide 49: duplicar registros pode causar sobreajuste (overfitting) e remover registros pode perder informação/causar underfitting. Não menciona "sobreajuste" em nenhum momento; undersampling é só definido (45:00 "reduzir artificialmente").
- **Divergências/ressalvas:**
  - 11:21–11:30 diz que SMOTE é "um control C control V", "basicamente um copia e cola da classe minoritária". Isso confunde SMOTE com o oversampling aleatório por duplicação; (conhecimento externo) o SMOTE cria exemplos sintéticos interpolando vizinhos da classe minoritária. A frase é compatível com o slide 49 (duplicar registros), mas errada para SMOTE.
  - Em 00:00–05:30 e 21:30–22:30 há muita promoção; "clickbait" assumido pelo próprio autor (21:30).
- **Nível e foco:** intermediário; supõe saber o que é validação cruzada, treino/teste e métricas. O conceito vale a pena para qualquer um; o código usa sklearn, imblearn, pandas e XGBoost. Conceito ~45%, código ~55%.
- **Idioma/qualidade:** português do Brasil, bem humorado, mas prolixo; legenda fraca (por exemplo "esmalte" = SMOTE).
- **Trechos recomendados:** 05:50–12:30 e 13:30–21:00 (14:10). O código (21:00–43:30) é opcional para quem já quer ver a ideia funcionando.
- **Veredito: `aprovar só os trechos 05:50–12:30 e 13:30–21:00`.** É o único que ensina corretamente "balancear só no treino", a versão de balanceamento do princípio de ajustar só no treino.

### CS9gMcVIAWU — Menino dos Dados — Balancear dados com SMOTE (17:43)

- **Cobre:** problema de classe desbalanceada com contagem e gráfico (06:00–08:30); SMOTE em duas linhas após separar X e y (12:30–17:00); resultado: classes iguais.
- **Não cobre:** undersampling; ressalvas do slide 49; métricas; treino/teste; ordem das etapas.
- **Divergências/erros:**
  - **Aplica SMOTE no conjunto de dados inteiro antes de qualquer divisão treino/teste** (13:30–17:00): vazamento de dados; os exemplos sintéticos derivam de registros que depois podem cair no teste. Em nenhum momento fala de separar treino e teste antes.
  - Chama `LabelEncoder` de "one hot encode" (02:00, 10:30–12:00): errado (LabelEncoder dá um inteiro por categoria; one-hot dá colunas 0/1).
  - 07:30 e 02:00 afirma que desbalanceamento "com certeza gera overfitting": impreciso; o problema é viés para a classe majoritária.
  - 09:00 "sempre faço balanceamento mesmo com 15 registros de diferença": conselho discutível.
- **Nível e foco:** iniciante; foco em código (pandas, seaborn, sklearn, imblearn), muito detalhe de slicing e pouca explicação do conceito.
- **Idioma/qualidade:** português do Brasil; bom áudio, legenda boa, mas conteúdo raso e com erro de método.
- **Veredito: `descartar`.** O Pwl cobre o conceito melhor e corretamente.

### ZqEhn1l_PlQ — Data ICMC (USP) — Aula 09 Redução de Dimensionalidade (48:44)

- **Cobre:**
  - 00:00–10:30 motivação: cada atributo é um eixo, só conseguimos visualizar até 3D; cortar features sem critério perde informação; objetivo é perder o mínimo.
  - 04:30–13:30 álgebra linear: vetor, combinação linear, span, matriz como transformação linear.
  - 14:00–19:00 autovetor (vetor que mantém a direção sob a transformação) e autovalor (quanto ele escala).
  - 16:30–17:30 e 33:00–34:00 matriz simétrica tem autovetores ortogonais entre si.
  - 20:30–24:30 decomposição em autovetores/autovalores.
  - 31:00–34:30 matriz de covariância; seus autovetores apontam as direções de maior variância (isso alinha com os slides 32 e 44).
  - 34:30–36:30 centrar média e escalar.
  - 40:30–44:30 demo 2D com sklearn: mudar de base, descartar o eixo de pouca variância.
  - 44:30–46:00 Iris com `PCA`, scree plot e variância explicada (cerca de 80% e 10%).
  - 39:30–41:00 cita t-SNE e UMAP como técnicas mais novas.
- **Não cobre:** padronização como pré-requisito explícito; seleção × agregação; maldição da dimensionalidade; interpretabilidade; a explicação geométrica específica dos slides 37–43 (reta que minimiza distâncias / maximiza a soma dos quadrados) — ele chega ao mesmo resultado pela covariância.
- **Divergências/ressalvas:**
  - 35:00–37:00 diz que escalar no intervalo [−1, 1] deixa a média em zero "se assumir que são normais": impreciso (conhecimento externo: o PCA centraliza pela média; reescalar para [−1, 1] não centraliza em geral). 42:00 "tenho certeza que estão distribuídos normalmente" também é afirmação frágil. Usa X^T X como covariância assumindo média zero.
  - 24:00–31:00 é um desvio sobre exponenciação de matrizes (complexidade) sem relação com a prova.
  - Aula gravada ao vivo, com perguntas do chat (20:00, 37:00, 40:30) e áudio de sala.
- **Nível e foco:** intermediário a avançado em matemática; é uma aula de graduação (supõe geometria analítica/álgebra linear básica, mas ensina). Foco 90% conceito; poucas linhas de código.
- **Idioma/qualidade:** português do Brasil, bom professor, ritmo de aula; legenda com muitos erros ("alto valor", "al vetor").
- **Trechos recomendados:** 13:30–19:00 (autovetor e autovalor), 33:00–35:00 (simétrica → ortogonais, direção de maior variância), 40:30–45:00 (demonstração em 2D e variância explicada). Se faltar base de álgebra linear, assistir antes 09:30–13:30 (transformação linear).
- **Veredito: `aprovar só os trechos 13:30–19:00, 33:00–35:00 e 40:30–45:00`** como complemento ao p4bv (cobre os slides 43–44 e 47, que o p4bv só cita). Por ser de nível mais alto, é opcional se o tempo estiver curto; para a prova o p4bv basta.

## 3. Sequência recomendada para assistir (ordem dos slides)

Tempo estimado do conjunto: **cerca de 1h35** (94:55). Vídeos ficam em ordem de assunto, não de ID.

| # | Slides | Vídeo | Trechos (início–fim) | Tempo | Por quê / o que ignorar |
| :-: | :-- | :-- | :-- | :-: | :-- |
| 1 | 6–8, 13 | SNd_qoGUEOE | 00:40–08:15 | 7:35 | Vazamento (intuição), opções para extremos e para ausentes. Atenção à ressalva de "processar cada amostra individualmente". |
| 2 | 7–13 | CLN-y_4ZySw | 00:00–02:30 · 04:20–16:10 · 29:45–33:45 | 18:20 | O que é outlier, manter × remover, IQR, Z-score, impacto em regressão com remoção só no treino. Pular 02:30–04:20 e 16:10–29:30. |
| 3 | 14–16 | NEY0TrvHRoU | 00:30–03:30 · 09:30–20:00 · 20:30–22:15 | 15:15 | Por que escalar, min-max, padronização, exemplo de distância. Ignorar a frase "distribuição normal" (20:00–20:30). O código do vídeo vaza dados. |
| 4 | 17 | -L8MacYRWGM | 18:10–18:45 · 22:05–23:30 · 24:30–25:30 | 3:00 | Quando usar cada uma e quais algoritmos se beneficiam. Não assistir 18:45–20:30 (outliers confusos). |
| 5 | 19–20 | RWaMw02_MQQ | 07:50–10:15 · 16:30–23:00 · 29:50–31:00 | 10:05 | Nominal × ordinal, por que numerar nominais engana, one-hot. Ignorar "LabelEncoder para ordinal". |
| 6 | 22–36 | p4bvCFygfW0 | 02:30–15:00 · 21:30–23:30 | 14:30 | Ideia do PCA, pré-requisitos, componente = combinação linear, ortogonalidade, variância explicada. |
| 7 | 43–47 | ZqEhn1l_PlQ | 13:30–19:00 · 33:00–35:00 · 40:30–45:00 | 12:00 | Autovetor/autovalor, ortogonalidade, direção de maior variância. Opcional para quem tem pouca base de álgebra: antes, 09:30–13:30. |
| 8 | 48–51 | PwlKbdsVsiY | 05:50–12:30 · 13:30–21:00 | 14:10 | Desbalanceamento, métrica enganosa, over/under, e balancear só no treino. |
| | | **Total** | | **94:55** | |

Vídeos fora da sequência: **1hMt-X2VYBk** (descartar; redundante com CLN) e **CS9gMcVIAWU** (descartar; SMOTE aplicado no conjunto inteiro, LabelEncoder chamado de one-hot).

Se faltar tempo (versão mínima, ~48 min): itens 1, 2 (só 04:20–16:10), 3 (só 09:30–22:15), 5, 6 e 8.

## 4. Lacunas: tópicos que nenhum vídeo cobre bem (o material escrito precisa cobrir)

1. **Slides 3–4: caracterização dos dados e integração de bases** (inconsistências e redundâncias ao juntar tabelas). Nenhum vídeo; só aparecem estatísticas descritivas de passagem (1hMt 03:00–04:00; NEY0 24:30–26:30).
2. **Dados faltantes (slide 6):** nenhum vídeo lista as 7 alternativas. Faltam: preencher manualmente, heurística, valor que indica ausência, moda e prever o valor com um algoritmo de AM.
3. **Winsorização e "manter + algoritmos robustos" (slide 13):** não aparece em nenhum vídeo; só há remoção e substituição por média/mediana (SNd 04:00–05:30) e a decisão manter × remover (CLN).
4. **IQR × Z-score (slide 12):** a razão de ser robusto (mediana e quartis não são arrastados por um extremo, a média sim) não é dita; CLN só diz que o Z-score supõe normalidade e é sensível.
5. **Ordem outliers → normalização (slide 18):** nenhum vídeo; o único que toca no assunto (-L8, 18:30–20:30) diz o contrário do slide.
6. **Ajustar só no treino na prática (scaler, imputer, PCA):** nenhum vídeo mostra o `fit` só no treino e `transform` no teste. NEY0 e -L8 vazam; CS9g vaza no SMOTE; só Pwl faz certo, e apenas para balanceamento; SNd e CLN mostram o princípio para imputação/remoção de outliers. Este é um tópico para o texto escrito (com um trecho de código curto, como na prova).
7. **Quais algoritmos precisam de escala (slide 17, "baseados em gradiente / distância"):** cobertura só parcial (NEY0 02:30–03:30, -L8 24:30–25:30); falta a lista completa do slide e a distinção por tipo de algoritmo.
8. **Discretização / conversão numérico→simbólico (slide 21):** nenhum vídeo (larguras iguais, intervalos com rótulo).
9. **Maldição da dimensionalidade (slides 22–23):** nenhum vídeo explica que mais atributos exigem mais amostras; só "dimensões grandes são difíceis de treinar" (p4bv 08:00–11:30) e "perde informação" (Zq 04:30).
10. **Seleção de atributos × agregação (slides 26–30):** atributos irrelevantes (id, nome), atributos/objetos redundantes (data de nascimento × idade), correlação para detectar redundância, e a preferência por seleção em finanças/medicina por causa da interpretabilidade (slide 31). Nenhum vídeo.
11. **PCA: parte geométrica dos slides 37–43 e 45–46** (centrar na origem, reta que maximiza a soma dos quadrados das projeções, autovalor = essa soma, PC2 perpendicular, rotacionar o sistema). Os vídeos chegam ao mesmo resultado por outro caminho (covariância); o encadeamento do slide precisa de texto próprio. Também não aparece "combinação linear ou não linear" (slide 31).
12. **Sobreajuste por duplicação e perda de informação por undersampling (slide 49):** nenhum vídeo; ninguém explica o undersampling além da definição. Falta também descrever SMOTE corretamente (sintético por interpolação, diferente de duplicar).
13. **Como o slide 17 e os slides de gráficos/imagens podem ser cobrados** (slides 8, 9, 10, 12 etc. têm figuras): os vídeos não reproduzem as figuras da professora; vale o material escrito descrever o que cada gráfico mostra.
