# Validação dos vídeos pela transcrição — Aula 11 (Máquinas de Vetores de Suporte, SVM) — Bloco 4

Método: li a transcrição inteira, minuto a minuto, de cada vídeo citado aqui (30 vídeos no total: os 4 que estavam no bloco, 6 transcrições órfãs de SVM e 20 candidatos novos, buscados em duas rodadas com `study search` e transcritos com `study transcribe`), e comparei com os 31 slides de `Aulas/Aula 11 - Máquina de Vetor de Suporte (SVM)` (texto em `estudo/_fontes_extraidas/`). Os tempos `mm:ss` vêm dos blocos de um minuto da transcrição (precisão de cerca de ±30 s); todo `mm:ss` citado está dentro da duração real do vídeo (conferido por script). A legenda é automática (Whisper local) e erra símbolos, nomes e fórmulas.

**Esta ficha substitui a anterior.** A ficha antiga e os 4 itens do bloco (a11-v1 a a11-v4) foram tratados como não confiáveis e refeitos. O que a auditoria achou de errado neles:

- **a11-v4** (Pablo Dalsasso): título inventado ("One-vs-One e One-vs-Rest"). O vídeo cobre **só** o um-contra-um; o um-contra-todos (slide 29) não aparece. O recorte 01:15–04:30 também começava 50 s antes do assunto (multiclasse começa em ~02:05).
- **a11-v3** (Universo Discreto): título inventado ("Truque e Espaço de Maior Dimensão"; o real é "Kernel do SVM - Machine Learning 15"). A ficha dizia que os 3 kernels estavam em 04:50–08:30; na verdade estão em **08:00–09:30**, e o recorte de 01:00–08:30 cortava a lista de kernels no meio.
- **a11-v2** (ProfDanilo): a ficha dizia que "vetores de suporte" estavam em 05:30–06:57 e "simetria" em 03:00–05:30; na verdade os vetores de suporte são explicados em 03:00–04:00 e o vídeo não fala de simetria. Também omitia que o vídeo traz C, gamma e os nomes dos kernels.
- **a11-v1** (Programação Dinâmica): 00:35–02:00 é código de importação e gráfico pairplot da Iris, não "definição de SVM"; o vídeo só fala de C em uma frase (08:50–09:15). Vira complemento opcional.
- Nenhum dos 4 vídeos antigos cobria hiperplano canônico, folga (ε), C e gamma com explicação de fato, Lagrangeana/dual, um-contra-todos, vantagens e desvantagens: cerca de 13 dos 31 slides ficavam sem vídeo real.

Legenda das matrizes: **B** cobre bem · **P** cobre em parte · **–** não cobre · **X** diz algo que diverge do slide. `(opc)` = vídeo opcional.

## 1. Tópicos por slide

| Slide | Tópico |
| :-- | :-- |
| 1–2 | Capa e título (sem conteúdo) |
| 3 | O que é SVM; classificação e regressão; dados linearmente separáveis; hiperplanos |
| 4 | Qual o melhor hiperplano: ponto médio, simetria, distância d, menos overfitting [imagem] |
| 5 | Equação do hiperplano: β vetor normal (perpendicular), x ponto, β0 deslocamento [imagem] |
| 6 | Vetores de suporte (pontos mais próximos) e margem [imagem] |
| 7 | Abordagens: classificador de máxima margem → de vetores de suporte → SVM |
| 8 | Classificador de máxima margem: SVM linear de margem rígida, equação, produto escalar [imagem] |
| 9 | O que é um hiperplano [só imagem] |
| 10 | Separando as classes: yi = +1/−1 e yi·f(xi) > 0 [imagem] |
| 11 | Classificador de máxima margem; hiperplano canônico [3 imagens] |
| 12 | Entre tantos hiperplanos, qual escolher [só imagem] |
| 13 | Maximizar a largura do corredor (M); otimização com restrições; margem rígida |
| 14 | Classificador de vetor de suporte: permite pontos entre as margens [imagens] |
| 15 | Parâmetro C (tuning); variáveis de folga ε: 0, entre 0 e 1, maior que 1 [imagens] |
| 16 | Influência do parâmetro C [só imagens] |
| 17 | O classificador de vetor de suporte serve para limite linear; os reais costumam ser não lineares |
| 18 | SVM não linear: truque do kernel e hiperparâmetros |
| 19 | Kernel: transformação não linear para dimensão maior; fronteira não linear no espaço original |
| 20 | Hiperparâmetros: tolerar erros (soft margin) ou tentar separação perfeita (hard margin) |
| 21 | Parâmetro C: tolerância a erros; C é o inverso da regularização; C pequeno × C grande |
| 22 | C alto: overfitting e treino lento; C baixo: soft margin e underfitting [imagem] |
| 23 | Parâmetro gamma: só no SVM não linear (RBF, polinomial, sigmoide); raio de influência; pesos para a distância |
| 24 | Gamma alto: overfitting; gamma baixo: underfitting [imagem] |
| 25 | Função Lagrangeana; problema dual; produto interno (só títulos) |
| 26 | Problema dual; produto interno (só títulos) |
| 27 | Problemas multiclasse: um-contra-um ou um-contra-todos |
| 28 | Um-contra-um: classificadores por pares, voto da maioria (exemplo A, A, C → A) |
| 29 | Um-contra-todos: cada classe contra o resto (exemplo → C) |
| 30 | Vantagens: robusto a outliers, dados esparsos, não linear com kernels, alta dimensionalidade |
| 31 | Desvantagens: caixa-preta, lento, ajuste de C e gamma exige muitos testes |

## 2. Matriz slide × vídeo

Colunas, na ordem em que os vídeos aparecem no bloco: **v2** ProfDanilo (teoria) · **v5** UNIVESP · **v6** Levada (otimização) · **v11** Hashtag (código) opc · **v7** Michel Janos · **v12** StatQuest parte 1 opc · **v13** Levada (margens suaves) opc · **v8** Bhavesh Bhatt (C e gamma) · **v15** StatQuest RBF opc · **v3** Universo Discreto (kernel) · **v16** Visually Explained opc · **v1** Programação Dinâmica opc · **v14** Intuitive ML opc · **v9** Mahesh Huddar (multiclasse) · **v4** Pablo Dalsasso opc · **v10** computaçãoSemDrama (revisão).

| Slide | v2 | v5 | v6 | v11 | v7 | v12 | v13 | v8 | v15 | v3 | v16 | v1 | v14 | v9 | v4 | v10 |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 3 | B | B | – | P | P | P | – | – | – | P | – | – | P | – | – | B |
| 4 | B | B | – | B | B | B | – | – | – | B | – | – | B | – | – | – |
| 5 | – | B | B | B | – | – | – | – | – | – | – | – | – | – | – | P |
| 6 | B | B | – | B | B | B | – | – | – | B | – | – | B | – | – | – |
| 7 | – | P | – | – | B | B | – | – | – | – | – | – | – | – | – | – |
| 8 | – | P | B | P | – | – | – | – | – | – | – | – | – | – | – | B |
| 9 | B | – | – | P | P | B | – | – | – | – | – | – | P | – | – | – |
| 10 | – | – | B | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 11 | – | – | B | – | – | – | – | – | – | – | – | – | – | – | – | B |
| 12 | B | B | – | – | – | P | – | – | – | P | – | – | P | – | – | – |
| 13 | – | P | B | – | P | P | – | – | – | – | – | – | P | – | – | – |
| 14 | – | B | – | – | B | B | B | – | – | – | – | – | P | – | – | P |
| 15 | – | – | – | – | – | P | B | P | – | – | – | – | P | – | – | P |
| 16 | P | – | – | – | – | – | – | B | – | – | – | – | P | – | – | – |
| 17 | – | B | – | – | B | B | – | – | – | B | B | – | – | – | – | – |
| 18 | – | B | – | P | B | B | – | – | – | B | B | P | – | – | – | – |
| 19 | – | B | – | P | B | B | – | – | – | B | B | – | P | – | – | P |
| 20 | – | P | – | – | – | – | P | P | – | – | – | – | P | – | – | P |
| 21 | P | – | – | – | – | – | P | B | – | – | – | P | B | – | – | P |
| 22 | P | – | – | – | – | – | – | B | – | – | – | – | P | – | – | – |
| 23 | P | P | – | – | P | P | – | B | B | P | P | P | P | – | – | – |
| 24 | P | – | – | – | – | – | – | P | P | – | P | – | B | – | – | – |
| 25 | – | – | P | – | – | – | – | – | – | – | P | – | B | – | – | P |
| 26 | – | – | – | – | – | – | – | – | – | – | B | – | B | – | – | P |
| 27 | – | – | – | – | – | – | – | – | – | – | – | – | – | B | B | B |
| 28 | – | – | – | – | – | – | – | – | – | – | – | – | – | B | P | P |
| 29 | – | – | – | – | – | – | – | – | – | – | – | – | – | B | – | P |
| 30 | – | B | – | – | – | – | – | – | – | – | – | – | – | – | – | P |
| 31 | – | B | P | – | – | – | – | P | – | – | – | – | – | – | – | B |

Os slides 1 e 2 são capa. **Cobertura só com vídeos não opcionais** (v2, v5, v6, v7, v8, v3, v9, v10): todos os slides de 3 a 31 têm pelo menos P, e B nos slides 3 a 14, 16 a 19, 21 a 23 e 27 a 31. As exceções, declaradas honestamente:

- **Slide 15 (ε em três casos):** os vídeos principais só tocam em folga (v10, v8 fala de C). Os três casos (0; entre 0 e 1; maior que 1) estão bem em v13 (opcional).
- **Slides 25 e 26 (Lagrangeana, dual, produto interno):** são só títulos nos slides; o principal só toca no assunto (v10, 06:30–08:00). Em vídeo, quem explica de verdade é v14 (opcional, matemático) e v16 (3 min, mais fácil).
- **Slide 24 (overfitting com gamma alto):** v8 mostra o efeito de gamma no ajuste mas não o overfitting; só v14 (opcional) diz "gamma grande, risco de overfitting".
- Ver lacunas na seção 5.

## 3. Fichas dos vídeos aprovados (na ordem do bloco)

### a11-v2 — `Fgd-paB7Ejc` — Máquina de vetores de suporte (SVM) - Teoria (ProfDanilo_DS, 6:57)

- **Cobre:**
  - 00:30–01:00 SVM supervisionado, usado em classificação e regressão (slide 3).
  - 01:00–02:00 objetivo: o hiperplano de margem máxima entre vários possíveis, que dá mais confiança a pontos novos (slides 3, 4 e 12).
  - 02:00–03:00 hiperplano como fronteira de decisão; 2 atributos: reta; 3: plano; acima disso não dá para desenhar (slide 9).
  - 03:00–04:00 vetores de suporte: pontos próximos que definem posição e orientação do hiperplano (slide 6).
  - 04:00–05:00 C: grande, margem pequena e melhor no treino; pequeno, margem grande e mais erros (slides 21 e 22). Cita os kernels linear, polinomial, gaussiano/RBF e sigmoide (slide 23).
  - 05:00–06:00 gamma: baixo, a influência de um ponto alcança longe; alto, só os próximos (slides 23 e 24); boa margem = equilibrada entre as classes.
- **Não cobre:** equação do hiperplano com valores; margem rígida × suave e folga; truque do kernel; multiclasse; vantagens e desvantagens.
- **Divergências:** 04:30–05:00 diz que "regularização baixa dá uma reta, alta dá uma curva"; pelo slide 21 C é o **inverso** da regularização. Legenda confusa em 03:00–04:30.
- **Nível e idioma:** introdutório, português do Brasil, sem exemplo numérico.
- **Veredito: `aprovar o trecho 00:30–06:57`** como primeira visão geral.

### a11-v5 — `54wtapH5t3E` — Aprendizado de Máquinas - Máquinas de Vetores de Suporte SVMs (UNIVESP, 22:55)

- **Cobre:** (aula expositiva, quase a mesma sequência dos slides)
  - 06:00–07:00 separador de margem máxima (slides 3 e 6).
  - 08:00–10:00 várias fronteiras lineares = hiperplanos; a ótima fica no meio, com duas margens (slides 4 e 12).
  - 10:00–11:00 vetores de suporte "sustentam" a fronteira (slide 6).
  - 11:00–12:00 equação: w vetor normal, x ponto, b deslocamento; rótulos −1 e +1 (slides 5 e 10).
  - 12:00–14:00 margem rígida (só aceita ponto fora da margem, supõe separação perfeita) × margem suave (aceita taxa de erro) (slides 8, 13 e 14).
  - 14:00–17:00 não linear: truque do kernel; exemplo 2D para 3D (slides 17, 18 e 19).
  - 17:00–18:20 kernels polinomial, RBF e sigmoidal (slide 23).
  - 20:00–21:00 vantagens: generaliza bem, alta dimensionalidade, robusta a ruído (slide 30).
  - 21:00–22:00 desvantagens: difícil de interpretar, sensível aos parâmetros, custoso (slide 31).
- **Não cobre:** C e gamma por nome; folga ε; canônico; Lagrangeana/dual; multiclasse; dados esparsos.
- **Divergências e extras:** 12:00 diz "menor ou igual a 1 → laranja" (o certo é −1, como ele mesmo disse em 11:00). 17:00 dá regras de bolso do autor (polinomial para dados normalizados etc.), que não estão nos slides. 00:00–06:00 é teoria do aprendizado estatístico (fora dos slides). 18:20–19:30 é SVR (regressão), só gancho do slide 3.
- **Nível e idioma:** iniciante a intermediário; português do Brasil; voz clara, ritmo de aula.
- **Veredito: `aprovar o trecho 06:00–22:05`** (a única cobertura em português de vantagens e desvantagens e da lista de kernels).

### a11-v6 — `_VDIhWvaOA4` — Máquinas de vetores de suporte (SVM) - Formulação do problema de otimização (Prof. Alexandre Levada, 13:09)

- **Cobre:**
  - 01:00–03:00 hiperplano w·x + b = 0, w perpendicular; b/‖w‖ de deslocamento da origem; infinitos (w, b) para o mesmo hiperplano (slide 5).
  - 03:00–04:00 hiperplano canônico: os mais próximos satisfazem |w·x + b| = 1 (slide 11).
  - 04:00–06:00 margens em +1 e −1; regiões acima de 1 e abaixo de −1 (slides 8 e 13).
  - 06:00–08:00 com y = ±1 as duas condições viram uma: y(w·x + b) − 1 ≥ 0 (slide 10).
  - 08:30–09:30 uma restrição por amostra; por isso a SVM é pesada (slide 31).
  - 09:00–11:00 largura da margem = 2/‖w‖; maximizar a margem = minimizar ‖w‖ (½‖w‖²) (slide 13).
  - 11:00–12:20 otimização com restrições de desigualdade; a solução (Lagrange e KKT) fica para o próximo vídeo.
- **Não cobre:** folga, C, gamma, kernel, multiclasse; Lagrange/dual só é anunciado.
- **Divergências:** notação w, b (o slide usa β, β0). 11:00 a legenda diz "maximizar a norma", mas o sentido é minimizar.
- **Nível e idioma:** intermediário (álgebra linear); português do Brasil. A prova é sem cálculo: assistir para ver a ideia, não decorar.
- **Veredito: `aprovar o trecho 01:00–12:15`.** É a única cobertura em vídeo dos slides 10 e 11 (hiperplano canônico).

### a11-v11 (opcional) — `Y-WFZd9_gtE` — SVM (Support Vector Machine) - Algoritmos de Aprendizado de Máquinas (Hashtag Programação, 23:06)

- **Cobre:** 01:00–03:00 limite no meio de pontos de classes diferentes; vetores de suporte e margens (slides 4 e 6) · 04:00–05:00 reta, plano, hiperplano (slide 9) · 05:00–07:00 elevar x ao quadrado, kernel, truque (calcula sem transformar), treino mais lento (slides 18, 19 e 31) · 07:00–12:00 código: `SVC(kernel="linear")`, `fit`, `coef_` (w1, w2), `intercept_` (w0), equação w1·x1 + w2·x2 + w0 = 0, margens em ±1 (slides 5 e 8) · 14:00–15:00 `support_vectors_` (slide 6) · 15:00–17:00 plota reta, vetores de suporte e margens.
- **Não cobre:** C, gamma, margem suave, kernels não lineares (só cita), multiclasse.
- **Divergências:** 06:00 diz que o algoritmo "busca a melhor dimensão" sozinho (quem escolhe o kernel é você). Chama coef_ de coeficiente angular (analogia com regressão). 17:00 em diante é avaliação (matriz de confusão), fora do tema.
- **Nível e idioma:** iniciante em Python; português do Brasil, fala rápida.
- **Veredito: `aprovar como complemento o trecho 00:55–17:10`.** Valor: mostra em código scikit-learn onde estão w, b e os vetores de suporte, e a prova traz trechos de scikit-learn.

### a11-v7 — `s1PdatomM5E` — 29 SVM - Como funciona o SVM (Michel Janos, 8:58)

- **Cobre:**
  - 00:00–01:00 limite no ponto médio entre os pontos extremos (slide 4).
  - 01:00–02:00 classificador de máxima margem; não é robusto a outliers (slides 7, 13 e 30).
  - 02:00–03:00 tolerar um outlier e aceitar um erro dá margem melhor; vetores de suporte nos limites da margem (slides 6 e 14).
  - 03:00–04:30 1D: ponto; 2D: reta; 3D: plano; acima, hiperplano (slide 9).
  - 05:30–07:00 dados em que o meio é "ruim" (chuva demais ou de menos) não se separam; elevando ao quadrado ganha-se uma dimensão e uma reta separa: truque do kernel (slides 17, 18 e 19).
  - 07:00–07:50 kernel polinomial; RBF (vizinhos próximos influenciam) (slide 23).
  - 07:50–08:30 regressão logística ≈ SVM linear; a diferença aparece nos kernels não lineares.
- **Não cobre:** equação, ε, C e gamma por nome, Lagrange/dual, multiclasse, vantagens e desvantagens.
- **Divergências:** o vídeo começa no meio de uma frase (recorte de uma aula maior). Diz que a margem é escolhida por **validação cruzada**; nos slides essa tolerância é o parâmetro C (slides 15 e 21), e o vídeo nunca diz "C".
- **Nível e idioma:** iniciante; português do Brasil; encadeamento claro (máxima margem → margem suave → kernel).
- **Veredito: `aprovar o trecho 00:00–08:35`.** É a melhor explicação em português da sequência do slide 7.

### a11-v12 (opcional) — `efR1C6CvhmE` — Support Vector Machines Part 1 (of 3): Main Ideas!!! (StatQuest with Josh Starmer, 20:32) — **inglês**

- **Cobre:** 00:15–02:00 limiar no ponto médio (slide 4) · 02:00–03:30 margem; classificador de máxima margem (slides 6, 7 e 13) · 03:30–05:00 sensível a outliers (slides 13 e 30) · 05:00–07:00 permitir erros (viés × variância), margem suave, classificador de vetores de suporte, vetores de suporte (slides 14 e 15) · 07:00–11:00 2D reta, 3D plano, acima hiperplano (slides 9 e 12) · 11:00–12:00 sobreposição que nem a margem suave resolve (slide 17) · 12:00–15:00 ideia da SVM: dimensão baixa → alta → classificador (dose e dose²) (slides 18 e 19) · 15:00–17:30 kernel polinomial com grau d · 17:30–18:30 kernel radial como vizinho mais próximo ponderado (slide 23) · 18:30–20:00 truque do kernel (slide 19).
- **Não cobre:** equação, canônico, C e gamma por nome, Lagrange/dual, multiclasse, vantagens e desvantagens.
- **Divergências:** diz que a margem suave é escolhida por validação cruzada (no scikit-learn, é o C). Nomes: "maximal margin classifier" = classificador de máxima margem; "support vector classifier" = classificador de vetor de suporte.
- **Nível e idioma:** iniciante absoluto; **inglês**, com humor. A explicação mais clara que existe dessa progressão.
- **Veredito: `aprovar como complemento o trecho 00:15–19:55`.** Opcional porque o v7 (português) cobre o mesmo caminho em 9 minutos.

### a11-v13 (opcional) — `sT7H8gBjrbM` — SVM's de margens suaves (Prof. Alexandre Levada, 11:22)

- **Cobre:** 00:00–01:00 a margem rígida é impossível na prática (classes se sobrepõem) (slides 14 e 20) · 01:00–02:00 variáveis de folga ε (slide 15) · 02:00–03:00 função objetivo ganha C·Σε (slides 15 e 21) · 05:50–08:40 os três tipos de vetores de suporte por ε: ε = 0 sobre a margem; entre 0 e 1 viola a margem do lado certo; maior que 1 erro de classificação (slide 15) · 10:00–11:00 a margem suave é o método mais usado na prática.
- **Não cobre:** efeito de C em gráficos, gamma, kernel, multiclasse. 03:00–06:00 e 09:00–10:00 são dual com α e KKT (avançado, fora da prova).
- **Divergências:** fórmulas yi(w·xi + b) ≥ 1 − εi; o slide 15 mostra só a ideia.
- **Nível e idioma:** intermediário a avançado; português do Brasil.
- **Veredito: `aprovar como complemento os trechos 00:00–03:10, 05:50–08:40 e 10:00–11:05`.** É o único vídeo que mostra bem os três casos de ε do slide 15.

### a11-v8 — `fqhHBCfNy6s` — Hyperparameters C & Gamma in Support Vector Machine (SVM) (Bhavesh Bhatt, 13:40) — **inglês**

- **Cobre:**
  - 00:55–02:00 gamma só vale para kernels RBF e polinomial, não para o linear; controla a distância de influência de um ponto; gamma baixo = raio grande; alto = só pontos próximos (slide 23).
  - 04:00–08:30 demonstração: gamma = 0,001 classifica tudo como classe 0 (≈ 50%); 0,1 chega a ≈ 80%; 1 chega a ≈ 93% (slide 24).
  - 08:00–09:30 C = penalidade por erro; C pequeno: margem larga, tolera erros; C grande: margem pequena, tenta errar menos (slides 15, 21 e 22).
  - 09:30–12:30 demonstração com gamma fixo: C = 0,1 (≈ 60%, margem larga), 1 (≈ 80%), 10 (≈ 94% no treino, margem encolhida, risco de overfitting) (slides 16 e 22).
  - 12:30–13:00 é preciso ajustar os hiperparâmetros (slide 31).
- **Não cobre:** C como "inverso da regularização" (slide 21); overfitting com gamma muito alto (slide 24); sigmoide; folga ε.
- **Divergências:** as acurácias são do **treino** (ele avisa em 12:00). Mais da metade é código (foque nos gráficos).
- **Nível e idioma:** iniciante em teoria; **inglês**, fala clara. Não achei vídeo em português que explique C e gamma com gráficos.
- **Veredito: `aprovar o trecho 00:55–13:20`.**

### a11-v15 (opcional) — `Qc5IyLW_hns` — Support Vector Machines Part 3: The Radial (RBF) Kernel (StatQuest, 15:52) — **inglês**

- **Cobre:** 01:00–02:00 RBF para dados sobrepostos · 02:00–03:00 comporta-se como vizinho mais próximo ponderado: perto pesa muito, longe quase nada (slide 23) · 03:00–05:00 a influência é função da distância ao quadrado; gamma escala essa distância: gamma = 1 → 0,11; gamma = 2 → 0,01; pontos distantes ≈ 0 (slides 23 e 24).
- **Não cobre:** overfitting/underfitting por gamma, C, sigmoide. 05:00–15:50 é a demonstração de dimensão infinita com série de Taylor (avançado, fora dos slides).
- **Nível e idioma:** iniciante nos 5 primeiros minutos, muito avançado depois; **inglês**.
- **Veredito: `aprovar como complemento só o trecho 01:00–05:00`.** Dá a imagem do "peso para a distância" do slide 23.

### a11-v3 — `ydiqpR5gw0E` — Kernel do SVM - Machine Learning 15 (Universo Discreto, 18:37)

- **Cobre:**
  - 01:00–03:00 exemplo com dois exames de sangue: o hiperplano ótimo é a reta que separa doentes de saudáveis (slides 3 e 4).
  - 03:00–04:00 vetores de suporte = amostras mais próximas do contorno; o hiperplano tem a mesma e maior margem possível dos dois lados (slides 4 e 6).
  - 04:00–05:00 caso não linear: precisa de uma curva (slides 17 e 18).
  - 05:00–07:00 o kernel representa os dados em outra dimensionalidade (2D → 3D) e torna fácil achar o hiperplano (slides 18 e 19).
  - 07:00–08:00 plano linear em 3D; volta-se à região original: "truque do kernel" (slide 19).
  - 08:00–09:30 kernels linear, polinomial (grau 3, 4 ou 5) e gaussiana/RBF (curva em sino) (slide 23).
- **Não cobre:** ε, C, gamma, sigmoide, equação, multiclasse. 09:30–18:00 é comparação de modelos com código (Titanic, TQDM): fora do tema.
- **Divergências:** diz que o kernel "sempre joga uma dimensão acima" (06:00), mas em 05:00 fala em 60D e 120D; é simplificação. Chama o RBF de "gaussiana".
- **Nível e idioma:** introdutório; português do Brasil; desenhos prontos e exemplos do dia a dia.
- **Veredito: `aprovar o trecho 01:00–09:50`.**

### a11-v16 (opcional) — `Q7vT0--5VII` — The Kernel Trick in Support Vector Machine (SVM) (Visually Explained, 3:18) — **inglês**

- **Cobre:** 00:00–01:00 a fronteira plana é vantagem e limitação; transformar os dados antes (f(x)) dá fronteira não linear (slides 17 a 19) · 01:00–02:00 o truque do kernel: o algoritmo só precisa do produto interno f(x)·f(x′), que a função kernel dá sem calcular f (slide 26) · 02:00–03:00 kernel linear = identidade; polinomial inclui interações; RBF = dimensão infinita com fórmula simples; gamma deixa a fronteira suave ou irregular (slides 23 e 24).
- **Não cobre:** ε, C, equação, multiclasse, vantagens e desvantagens.
- **Nível e idioma:** iniciante a intermediário; **inglês**; muito condensado.
- **Veredito: `aprovar como complemento o vídeo inteiro (00:00–03:15)`.** O caminho mais curto para a ideia dos slides 25 e 26.

### a11-v1 (opcional) — `ba7tMJZbGyA` — CLASSIFICAÇÃO com Máquinas de Vetores de Suporte (SVM) | Machine Learning #05 (Programação Dinâmica, 11:23)

- **Cobre:** 05:00–06:30 não linear → kernel; opções linear, polinomial, RBF e sigmoide no scikit-learn (slides 18 e 23) · 06:30–08:00 escolher o kernel conforme os dados; kernels não lineares custam mais processamento · 08:00–09:00 código: `train_test_split(test_size=0.3, random_state)`, `SVC()`, `fit` · 08:50–09:15 "C menor, margem mais suave; C maior, margem mais rígida" (slides 21 e 22) · 09:15–10:30 `predict` e `score` (97%).
- **Não cobre:** equação, ε, gamma (o aviso do scikit-learn sobre gamma em 09:15 não é explicado), truque do kernel em detalhe, multiclasse. 00:00–05:00 é Iris, gráficos e uma explicação rápida (repete os anteriores).
- **Nível e idioma:** iniciante em Python; português do Brasil.
- **Veredito: `aprovar como complemento só o trecho 05:00–10:20`.** Valor: código scikit-learn curto e completo, e a lista de kernels da documentação.

### a11-v14 (opcional) — `ny1iZ5A8ilA` — Support Vector Machines: All you need to know! (Intuitive Machine Learning, 14:58) — **inglês**

- **Cobre:** 00:00–01:00 hiperplano: ponto, reta, superfície (slide 9) · 01:00–02:50 máxima margem; vetores de suporte são os pontos mais difíceis e só eles influenciam a fronteira (slides 4, 6 e 12) · 06:50–09:30 multiplicadores de Lagrange; w = Σ αi yi xi; só os vetores de suporte têm α ≠ 0; a otimização e a regra de decisão passam a depender só do produto escalar entre pares de amostras (problema dual) (slides 25 e 26) · 10:00–11:00 margem rígida não tolera ruído; variáveis de folga ζ (slides 14 e 15) · 12:00–12:20 C pequeno: margem larga e erros; C grande: margem menor e menos tolerância; C → ∞ = margem rígida (slides 20 e 21) · 12:20–14:00 truque do kernel: substitui xi·xj por k; polinomial com grau d (slides 19 e 23) · 14:00–14:50 RBF e gamma: pequeno ≈ linear; grande = muito influenciado pelos vetores de suporte e overfitting (slide 24).
- **Não cobre:** hiperplano canônico, multiclasse, vantagens e desvantagens. 03:00–06:50 deduz a margem 2/‖w‖.
- **Divergências:** 11:00–12:00 diz que "C menor enfatiza a importância de ζ", que é o inverso do padrão; logo em seguida (12:00) ele conclui a direção correta. Fique com a conclusão.
- **Nível e idioma:** intermediário a avançado; **inglês**.
- **Veredito: `aprovar como complemento os trechos 00:00–02:50 e 06:50–14:55`,** sem exigir entender cada passo. A única cobertura em vídeo explícita dos slides 25 e 26 junto com v16.

### a11-v9 — `s7iC1ePvCWU` — Multiclass SVM | Multiclass Support Vector Machines | Multiclass Classification (Mahesh Huddar, 8:01) — **inglês**

- **Cobre:** 00:00–01:30 SVM é binário; com 3 classes não basta um hiperplano (slide 27) · 02:00–04:00 um-contra-resto: k classificadores (maçã vs resto, banana vs resto, laranja vs resto); vence o maior escore (0,7; 0,9; 0,3 → banana) (slide 29) · 04:00–04:30 desvantagem: desbalanceamento · 04:30–06:30 um-contra-um: k(k − 1)/2 classificadores, um por par; cada um vota; vence a classe com mais votos (1 × 2 × 0 → laranja) (slide 28) · 06:30–07:50 10 classes → 45 classificadores.
- **Não cobre:** o que o scikit-learn faz por padrão.
- **Divergências:** "one versus rest" = "one-vs-all" do slide. No um-contra-todos escolhe pelo **maior escore**, enquanto o exemplo do slide 29 escolhe a classe "que ganhou do resto"; mesma ideia.
- **Nível e idioma:** iniciante; **inglês**; passo a passo com exemplos. Não achei vídeo em português que cubra os dois métodos com exemplo (os dois que li cobrem um só, ou os dois em duas frases).
- **Veredito: `aprovar o trecho 00:00–07:50`.**

### a11-v4 (opcional) — `9EuqfpoI4p8` — Support Vector Machine Multiclasse - Pablo Dalsasso.wmv (Pablo Dalsasso, 5:28)

- **Cobre:** 02:05–03:00 SVM é binário; os problemas reais têm várias classes; dividir em problemas menores; a forma mais usada é "todos contra todos" (slide 27) · 03:00–03:30 k classes → k(k − 1)/2 máquinas, cada classe comparada uma vez com cada outra (slide 28) · 03:30–04:40 exemplo com 4 classes e uma **árvore de eliminação**.
- **Não cobre:** o um-contra-todos (slide 29); votação por maioria.
- **Divergências:** a decisão aqui é por **árvore de eliminação** (cada comparação descarta uma classe), enquanto o slide 28 e o scikit-learn usam voto da maioria. A contagem é a mesma. A legenda embaralha a fórmula em 03:00.
- **Nível e idioma:** introdutório; português do Brasil; gravação antiga.
- **Veredito: `aprovar como complemento só o trecho 02:05–04:40`.** Único vídeo em português que mostra a contagem k(k − 1)/2 com exemplo.

### a11-v10 — `cB__Oa85htg` — SVM - Support Vector Machine Linear, Não Linear - Teoria (computaçãoSemDrama, 11:19)

- **Cobre:**
  - 00:00–01:00 SVM linear de margens rígidas define uma fronteira linear a partir de dados linearmente separáveis, por um hiperplano (slides 3 e 8).
  - 01:00–02:30 w·x + b = 0; w perpendicular, b escalar; infinitos hiperplanos equivalentes, então |w·x + b| = 1 nos mais próximos (slides 5 e 11).
  - 02:30–04:30 quando não há separação linear, usam-se variáveis de folga ε: 0 = fora da região da margem e correta; maior que 1 = erro de classificação; penalidade (constante C) ajustada em dados de validação (slides 14, 15 e 21).
  - 04:30–06:30 mapeamento φ para espaço de maior dimensão (slide 19).
  - 06:30–08:00 formulação dual com multiplicadores de Lagrange; depende só do produto entre as imagens, calculado pelo kernel (slides 25 e 26).
  - 08:00–09:30 vantagens: mínimo global, alta dimensionalidade; desvantagens: caixa-preta, só atributos numéricos, custo O(n²) a O(n³) (slides 30 e 31).
  - 09:30–11:10 multiclasse: "decomposição de N" (um-contra-todos) e "de 1" (um-contra-um, voto da maioria, grafo acíclico dirigido) (slides 27 a 29).
- **Não cobre:** gamma; efeito de C; dados esparsos e robustez a outliers (slide 30).
- **Divergências:** a legenda é ruim e a fala é corrida e monótona (parece leitura de texto de slides). "Decomposição de N/de 1" é o nome que ele dá a um-contra-todos/um-contra-um. Afirma que SVM com RBF equivale a uma rede neural RBF e cita o teorema de Mercer (fora dos slides). Só cita 2 dos 3 casos de ε.
- **Nível e idioma:** intermediário, vocabulário denso; português do Brasil.
- **Veredito: `aprovar o trecho 00:00–11:00` como revisão no fim,** depois dos demais. É o que mais se aproxima das palavras dos slides.

## 4. Candidatos lidos e descartados

| ID | Título (canal, duração) | Motivo de descartar |
| :-- | :-- | :-- |
| `Toet3EiSFcM` | SVM Part 2: The Polynomial Kernel (StatQuest, 7:15, inglês) | Foco em expandir a fórmula do kernel polinomial (r, d, produto escalar de dois pontos); matemática além do que os slides pedem. O polinomial já está coberto em v12 e v3. |
| `_ElNbj1Y2OI` | Machine Learning com SVM (Nerd dos Dados, 32:53) | 02:00–14:30 é uma intro boa mas redundante, com erros: "o SVM cria uma máquina virtual... eleva os números às potências" (13:00) é uma descrição incorreta do kernel. O resto é código da Iris (coef_, intercept_, support_vectors_), já coberto por v11. |
| `4Zh7UeHqHvc` | Máquina de Vetores de Suporte - SVM (Tomás, 8:56) | Diz que os vetores de suporte são os pontos "que não estão próximos do limite de decisão" (03:00), o inverso do correto, e que o hiperplano parte do "ponto médio" entre as classes sem mencionar margem máxima. O resto é código da Iris. |
| `7y4uceXgYeo` | SVM - Máquina de Vetores de Suporte (Aulas de Computação, 16:34) | Intuição boa de hiperplanos A, B e C e de margem (01:00–06:00), mas redundante com v2 e v5. A parte multiclasse (07:30–09:00) é confusa: descreve "class I vs class II, II vs III" sem dizer um-contra-um nem um-contra-todos. O restante é código, com descrição enganosa de `predict`. |
| `VCXngi7-U4s` | SVM Não-Lineares (Eliton Fontana, 8:54) | Mostra o efeito de C e gamma em código (02:00–07:00), mas a explicação de gamma é confusa: diz que "quanto menor o gamma, mais ele dá importância ao argumento, à distância entre os pontos", o inverso do slide 23. Descartado em favor de v8. |
| `pF2fLlUnqE4` | SVM Lineares (Eliton Fontana, 8:26) | Código de `LinearSVC` com dados de temperatura e pressão; só mostra de passagem o efeito do parâmetro de regularização (07:00). Nada que v8 e v11 não façam melhor. |
| `4oDSHGJteBI` | SVM Explained: Hard Margin, Soft Margin, Support Vector Classifier (StudyPalz, 7:13, inglês) | Boa analogia (gatos e cachorros), cobre margem, vetores de suporte, hard × soft e C, mas redundante com v7 e v8. Diz (04:00) que a margem rígida "torce a cerca para qualquer formato", o que não procede para SVM linear sem separação. |
| `l7Tr2OyXNU8` | Nonlinear SVM .. The Kernel Trick (Noureddin Sadawi, 6:23, inglês) | Rápido e genérico (usa "mapear para espaço de maior dimensão" sem exemplo numérico); frases confusas ("função não linear aprendida por máquina linear... capacidade controlada por parâmetro independente da dimensão"). Redundante com v3 e v16. |
| `joTa_FeMZ2s` | SVM C Parameter (Udacity, 1:50, inglês) | Só 1 minuto de conteúdo e termina em um quiz sem responder (qual a relação entre C grande e fronteira suave?). |
| `pH51jLfGXe0` | Kernel and Gamma (Udacity, 1:21, inglês) | Só apresenta os parâmetros e abre um quiz; não explica gamma. |
| `5oVQBF_p6kY` | The C Parameter for SVMs (Casey Greene, 2:41, inglês) | Boa explicação de C pequeno, médio e grande, mas redundante com v8 e v14 (e sem falar de margem suave ou folga). |
| `tV5X77lGYP4` | RBF Kernel Explained (DataMListic, 4:22, inglês) | Começa com um bom exemplo de círculos concêntricos, mas depois vira demonstração de dimensão infinita com série de Taylor. A parte útil sobre gamma (03:00–04:00) é a mesma de v15. |
| `y0wQK3mnrNY` | Multiclass Learning for Scikit Learn (10:54, inglês) | Foco em meta-estimadores do scikit-learn (OneVsRest, OneVsOne, códigos de saída corretiva, multilabel); não é específico da SVM e mistura assuntos fora dos slides. A parte útil (um-contra-um, um-contra-resto) está melhor em v9. |
| `3lwicUTEgHs` | Multiclass Classification One vs All / One vs One (Mahesh Huddar, 10:04, inglês) | Bom, e o conteúdo bate com os slides 27 a 29, mas é genérico (não só SVM), mais longo e quase igual a v9, que é específico de SVM. |

Houve uma falha de download: `4_0kcqk868M` (João Paulo Papa, "Máquinas de Vetores de Suporte - Parte 1", 17:01, português) deu erro de download do YouTube (`FALHOU` na fila). Não foi avaliado; se o usuário quiser, dá para tentar de novo com `study transcribe 4_0kcqk868M`.

## 5. Lacunas

- **Slide 21: "C é o inverso da força de regularização" (convenção das bibliotecas).** Nenhum vídeo diz isso. v8 chama C de "penalidade por erro", v2 e v10 de "parâmetro de regularização". A direção (C pequeno tolera erros, C grande pune) é a mesma; o texto de apoio explica a convenção.
- **Slide 24: overfitting com gamma alto e underfitting com gamma baixo.** v8 mostra o ajuste melhorando de 0,001 a 1; só v14 (opcional) diz que gamma grande leva a overfitting. O texto cobre.
- **Slide 30: "lida bem com dados esparsos (muitos zeros)".** Nenhum vídeo diz isso. "Robusto a outliers" aparece só como "robusto a ruídos" (v5) e na discussão de margem suave (v7, v12).
- **Slides 25 e 26 (Lagrangeana e dual):** só em vídeos opcionais (v14, v16) e, de passagem, em v10. Como os slides só têm os títulos, o texto de apoio explica o mínimo.
- **Sigmoide (slide 23):** só citada pelo nome (v2, v5, v1); nenhum vídeo a explica.
- **Slide 29 em português:** nenhum vídeo em português explica o um-contra-todos com exemplo; v9 (inglês) e v10 (duas frases).
- **Hiperplano canônico (slide 11):** só v6 (matemático) e v10 (uma frase). O slide mostra três imagens sem texto.

## 6. Resumo da decisão

- **Aprovados (principais, 8):** v2, v5, v6, v7, v8 (inglês), v3, v9 (inglês), v10.
- **Aprovados (complementos opcionais, 8):** v11, v12 (inglês), v13, v15 (inglês), v16 (inglês), v1, v14 (inglês), v4.
- **Descartados (14) e 1 falha de download:** seção 4.
- **Slides sem nenhum vídeo:** só 1 e 2 (capas). Slides que dependem de vídeo opcional para estar bem cobertos: 15 (três casos de ε, v13), 24 (overfitting com gamma alto, v14) e 25 e 26 (Lagrangeana e dual, v14 e v16); nos demais, o vídeo principal cobre. Lacunas na seção 5.


## Redução por sobreposição (agente principal, 11/10/2026)

Pedido do usuário: se vários vídeos se sobrepõem, não é preciso manter todos, MAS sem trocar um vídeo didático por outro mais técnico (o usuário é engenheiro de software sem base em ciência de dados). Critério: mais didático para esse nível, com mais analogias e que cubra mais slides. Todos os vídeos abaixo foram lidos na auditoria e aprovados; saíram do bloco só por sobreposição (regra do usuário: só sai o que for duplicado sem valor a mais; se dois vídeos se completam, ficam os dois) com um mais didático ou mais completo. Aula 11: ficaram a11-v2, v7, v3, v5, v8, v9, v16 (obrigatórios) e v6, v13, v10, v17, v4, v11, v12 (opcionais: mais técnicos, ou complementos de outros vídeos). As transcrições continuam em `estudo/conteudo/transcripts/`; para trazer um de volta, basta reinseri-lo no `block.json`.

- a11-v15 (StatQuest with Josh Star: Support Vector Machines Part 3: The Radial (RBF) Kernel (Par)
- a11-v1 (Programação Dinâmica: CLASSIFICAÇÃO com Máquinas de Vetores de Suporte (SVM) | Mac)
- a11-v14 (Intuitive Machine Learni: Support Vector Machines: All you need to know!)
