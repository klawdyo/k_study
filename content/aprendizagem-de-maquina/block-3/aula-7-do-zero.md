# Aula 7 do zero: métricas de avaliação para classificadores

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e um exemplo concreto, depois com o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção).

Convenções deste texto:

- O que está **nos slides** vem com o número do slide. O que é **exemplo nosso** (inventado aqui para você treinar) ou **complemento** (matéria de literatura que não está nos slides) vem marcado como tal.
- Alguns slides são só figura (matriz de confusão, curvas, relatórios). **Não conferi essas imagens**; quando uma seção depende de uma figura, digo isso.
- Onde o slide diverge da literatura, aparecem as duas versões e qual responder na prova.
- Fórmulas estão em blocos de código, em texto puro.

**A pergunta que a aula inteira responde:** *"quando o modelo diz sim ou não, como eu meço se ele está bom, e bom em quê?"*

Analogia de software: acurácia é como "% de testes que passaram". Só que, aqui, existem dois tipos de bug muito diferentes (alarme falso e alarme perdido), e as métricas desta aula servem para pesar cada tipo separadamente.

---

## 1. Por que avaliar classificadores (slides 1 a 3)

Os slides 1 e 2 são capa. O slide 3 diz apenas que, em problemas de classificação, você vai precisar de alguma maneira de avaliar o modelo, e que existem várias métricas para isso.

**Classificação** = o modelo devolve uma **categoria** (spam ou não spam; reserva cancelada ou mantida; fraude ou legítima), não um número contínuo como na regressão (aula 5).

**O primeiro choque de quem programa [complemento]:** numa suíte de testes, 990 de 1.000 passando é ótimo. Em AM, 99% de acerto pode ser um desastre: se 99% dos dados são de uma classe, um modelo que chuta sempre essa classe acerta 99% sem ter aprendido nada. As seções 3 e 4 mostram isso com números. Para enxergar *onde* o modelo erra, a aula começa pela **matriz de confusão**.

> **Se perguntarem na prova:** a escolha da métrica depende do problema; existe mais de uma métrica porque os erros têm custos diferentes.

---

## 2. Matriz de confusão (slides 4 a 9)

### 2.1 O que é (slide 4)

O slide 4 define: a **matriz de confusão (confusion matrix)** é uma tabela que indica os erros e acertos do modelo, **comparando com o resultado esperado**. (A figura do slide 4 não foi conferida.)

Analogia de software: é o log de testes agrupado por "o que eu esperava" x "o que o sistema respondeu".

### 2.2 Classe positiva e negativa (slides 5 e 9)

Em um problema de duas classes, escolhe-se uma como **positiva** (o evento que queremos detectar) e a outra como **negativa**. Positivo **não** significa "bom": uma fraude ou uma doença são "positivos".

Os dois exemplos dos slides:

| Slide | Problema | Positivo | Negativo |
| :-- | :-- | :-- | :-- |
| 5 | Classificador de reservas de hotel com grande chance de cancelamento | Será cancelada | Não será cancelada |
| 9 | Classificador de spam | É spam | Não é spam |

### 2.3 Os quatro resultados possíveis (slides 6, 7 e 9)

Cada previsão cai em um de quatro casos. Regra para não confundir:

- A **segunda palavra** (positivo/negativo) é o que o **modelo previu**.
- A **primeira palavra** (verdadeiro/falso) diz se o modelo **acertou**.

| Sigla | Nome (inglês) | Definição nos slides (hotel, slides 6 e 7) | Em spam (slide 9) |
| :-- | :-- | :-- | :-- |
| **VP** | Verdadeiro Positivo (TP) | Previu que seria cancelada e de fato foi | Disse spam e era spam |
| **VN** | Verdadeiro Negativo (TN) | Previu que NÃO seria cancelada e de fato não foi | Disse "não é spam" e não era |
| **FP** | Falso Positivo (FP) | Previu cancelamento, mas não foi cancelada | Disse spam, mas não era |
| **FN** | Falso Negativo (FN) | Previu que NÃO seria cancelada, mas foi | Disse "não é spam", mas era |

Resumo para guardar: **FP = alarme falso**. **FN = alarme perdido** (o caso deixou de ser detectado).

> Observação: nomes como "erro tipo I" e "erro tipo II" costumam ser associados a FP e FN na estatística, mas **isso não está nos slides** e depende de qual hipótese se escolhe como nula. Use VP/VN/FP/FN, que é o que a aula usa.

### 2.4 A tabela (slide 8) e a orientação no scikit-learn

O slide 8 é só figura (não conferida). Na literatura é comum desenhar a matriz com **linhas = classe real** e **colunas = classe prevista**. Na tabela abaixo, a ordem é a de um desenho "positivo primeiro":

| | Previsto positivo | Previsto negativo |
| :-- | :--: | :--: |
| **Real positivo** | VP | FN |
| **Real negativo** | FP | VN |

**Pegadinha: o scikit-learn ordena as classes pelo valor (0 antes de 1).** Com rótulos 0 (negativo) e 1 (positivo), `confusion_matrix(y_true, y_pred)` devolve:

```
[[ VN  FP ]      linha 0 = real 0 (negativo)
 [ FN  VP ]]     linha 1 = real 1 (positivo)
   col 0 = previsto 0   col 1 = previsto 1
```

Ou seja, no scikit-learn **VN fica no canto superior esquerdo e VP no inferior direito**, o contrário do desenho "positivo primeiro". Verifiquei: com `y_true = [0,0,0,0,1,1,1,1,1,1]` e `y_pred = [0,0,1,0,1,1,1,0,1,1]` a saída é `[[3 1], [1 5]]`, isto é VN = 3, FP = 1, FN = 1, VP = 5.

> **Se perguntarem na prova:** antes de extrair VP/FP/FN/VN de uma tabela, **leia os rótulos dos eixos** (qual é linha, qual é coluna, qual classe vem primeiro). Nunca presuma a ordem.

---

## 3. Acurácia (slides 10 a 15)

### 3.1 Definição (slides 10 e 11)

O slide 11 diz: a **acurácia (accuracy)** é uma boa indicação geral de como o modelo performou; compara o total de previsões **corretas** com o total de previsões **feitas**; representa a fração de previsões corretas no conjunto de **teste**.

```
Acurácia = (VP + VN) / (VP + VN + FP + FN)
```

### 3.2 O exemplo do hotel com números (slides 12 e 18)

Os slides 12 e 18 mostram o hotel com a matriz em figura (não conferida), e o slide 18 informa **acurácia = 72%**. Para podermos calcular tudo ao longo da aula, **exemplo nosso**, coerente com esses 72%: 100 reservas de teste, das quais 30 foram realmente canceladas e 70 não.

```
                      Previsto: cancela    Previsto: não cancela
Real: cancelou (30)         VP = 20               FN = 10
Real: não cancelou (70)     FP = 18               VN = 52
```

Acurácia = (20 + 52) / 100 = 72/100 = 0,72 = 72%. Vamos reaproveitar esses quatro números nas seções 4, 5, 6, 7.

(Os números da figura real do slide podem ser outros; só a acurácia de 72% vem do slide.)

### 3.3 O grande perigo: amostras desbalanceadas (slides 13 e 14)

**Slide 13 (spam).** A maioria das amostras não é spam. Se chutarmos que **todos não são spam**, a taxa de acerto é de 99% (o slide usa 99%), **independente do algoritmo**. Alta acurácia, mas não é um bom algoritmo. O slide resume: como a acurácia foca só nas previsões corretas, ela **pode esconder falhas do modelo**.

**Slide 14 (fraude em cartão).** Em 1.000.000 de previsões, o modelo previu que 998.000 transações não eram fraude e realmente não eram. Acurácia de 99,8%. Mas 2.000 transações são fraudes, e o objetivo do classificador é detectá-las. O slide conclui que você estaria validando como ótimo um modelo que falha em detectar fraudes.

Matriz do slide 14 (deduzida das contas do próprio slide, com a fraude como positivo): VP = 0, FP = 0, FN = 2.000, VN = 998.000.

```
Acurácia = (0 + 998.000) / 1.000.000 = 0,998
Recall   = 0 / (0 + 2.000) = 0
```

### 3.4 Vantagem e desvantagem (slide 15)

- **Vantagem:** simples e de fácil entendimento.
- **Desvantagem:** se quisermos minimizar FP e FN, a acurácia **não é uma métrica útil**. (Ela trata os dois tipos de erro como iguais e não separa o desempenho por classe.)

> **Se perguntarem na prova:** "base com 95% de uma classe e o modelo tem 95% de acurácia: ele é bom?" Resposta: não se sabe; pode estar chutando a classe majoritária. Use matriz de confusão, precisão, recall, F1.

---

## 4. Precisão (slides 16 a 19)

### 4.1 Definição (slide 17)

O slide 17 pergunta: *qual a proporção de identificações positivas que foi realmente correta?* É a métrica que prioriza **reduzir os falsos positivos**.

```
Precisão = VP / (VP + FP)
```

O denominador é "tudo que o modelo chamou de positivo". Analogia: de todos os alertas que o monitoramento disparou, quantos eram incidentes reais?

O slide mostra o raciocínio: diminuo FP, diminuo o denominador, a fração aumenta, precisão maior. Números do slide:

```
VP = 30, FP = 10  ->  Precisão = 30 / 40 = 0,75
VP = 30, FP = 2   ->  Precisão = 30 / 32 = 0,9375  (o slide escreve 0,93)
```

O slide **trunca** 0,9375 para 0,93; arredondando daria 0,94. Se uma questão trouxer 0,93 ou 0,94, é o mesmo cálculo.

### 4.2 Hotel com números (slide 18, exemplo nosso)

Com VP = 20 e FP = 18 (seção 3.2):

```
Precisão = 20 / (20 + 18) = 20/38 ≈ 0,526
```

Leitura: de cada 100 vezes que o modelo avisa "vai cancelar", só ~53 estavam certas.

### 4.3 Quando a precisão importa (slide 19)

O slide 19: a precisão pode ser usada quando os **falsos positivos são mais prejudiciais que os falsos negativos**. Os dois exemplos do slide:

1. **Vídeo adequado para criança** (positivo = recomendar). FP = recomendar e não ser adequado. FN = não recomendar o que poderia; "menos ruim".
2. **Recomendação de investimentos.** FP = recomendar investimento em maus negócios. FN = negar investimento que na verdade era rentável (deixa de ganhar; "menos ruim").

(O spam não está no slide 19. Em spam, o FP seria um e-mail legítimo na pasta de lixo: é um bom **exemplo nosso** de FP caro, mas lembre que quem apresenta isso como slide 19 está errado.)

> **Se perguntarem na prova:** precisão = VP/(VP+FP), reduz FP; use quando recomendar errado é pior do que deixar de recomendar.

---

## 5. Revocação, recall ou sensibilidade (slides 20 a 24)

### 5.1 Definição (slide 21)

O slide 21: a **revocação (recall, sensibilidade, TPR, "taxa de verdadeiros positivos")** é a proporção de casos positivos que foram **identificados corretamente**. Prioriza **reduzir os falsos negativos**.

```
Revocação = VP / (VP + FN)
```

O denominador é "todos os positivos reais". Analogia: de todos os incidentes que realmente aconteceram, quantos o monitoramento percebeu?

Mesmo raciocínio do slide: diminuo FN, diminuo o denominador, a fração cresce, revocação maior.

Hotel (exemplo nosso): VP = 20, FN = 10.

```
Revocação = 20 / (20 + 10) = 20/30 ≈ 0,667
```

De 30 reservas que realmente seriam canceladas, o modelo pegou 20.

### 5.2 Fraude e saúde (slides 22 a 24)

- **Slide 22 (fraude em cartão):** positivo = fraude; FN = o modelo diz que não é fraude, mas na verdade é. A figura do slide não foi conferida.
- **Slide 23 (diagnóstico de doença grave):** sugere-se modelo com **alta revocação** para diminuir FN. FN = dizer que não tem a doença e a pessoa ter; consequência: privar a pessoa de tratamento. FP é "menos ruim": descobre-se depois que não tem a doença.
- **Slide 24:** gráfico com o título "Baixa Revocação" (figura não conferida; o slide só rotula a ideia de que a revocação está baixa).

**Exemplo nosso (valor em reais é inventado, não vem do slide 22):** se cada fraude não detectada custa 50 mil reais e cada bloqueio indevido custa uma ligação de confirmação, vale aceitar muitos FP para derrubar os FN.

> **Se perguntarem na prova:** recall = VP/(VP+FN), reduz FN; use quando deixar passar um caso positivo é pior do que um alarme falso.

---

## 6. F1-Score (slides 25 a 29)

### 6.1 Definição (slide 26)

O slide 26: o **F1-Score** é o equilíbrio entre revocação e precisão; é a **média harmônica** entre as duas. Quando o F1 está baixo, é indício de que a precisão **ou** a revocação está baixa.

```
F1 = 2 × (Precisão × Revocação) / (Precisão + Revocação)
```

**Por que harmônica e não aritmética?** [Complemento, não está nos slides] Se a precisão é 1,0 e a revocação é 0,02:

```
Média aritmética = (1,0 + 0,02) / 2 = 0,51        (parece "razoável")
F1 (harmônica)   = 2 × (1,0 × 0,02) / (1,0 + 0,02) = 0,04/1,02 ≈ 0,039
```

A média harmônica é puxada para o valor menor. Para ter F1 alto, os dois precisam ser altos.

### 6.2 Hotel com números (slides 28 e 29, exemplo nosso)

Com precisão ≈ 0,526 e revocação ≈ 0,667:

```
F1 = 2 × (0,526 × 0,667) / (0,526 + 0,667) ≈ 0,588
```

Também sai direto das contagens: F1 = 2·VP / (2·VP + FP + FN) = 40 / (40 + 18 + 10) = 40/68 ≈ 0,588. Note que **VN não aparece**.

### 6.3 O que o slide 27 diz e a divergência com a literatura

O slide 27 afirma, em resumo, que, quando o F1 está alto, a acurácia obtida é **relevante** (VP, VN, FP, FN sem grandes distorções), e que o F1 pode ser visto como uma **medida de confiabilidade da acurácia**.

**Duas versões:**

- **Slide 27 (professora):** F1 alto indica que a acurácia é relevante / confiável.
- **Literatura:** o F1 é a média harmônica de precisão e recall e **não usa VN**. Logo ele não mede a acurácia nem sua confiabilidade; ele mede o equilíbrio entre acertar os positivos e não gerar alarmes falsos.

> **Se perguntarem na prova:** para "o que o F1 mede?", responda **equilíbrio (média harmônica) entre precisão e revocação**. Se a alternativa repetir a frase do slide 27 (F1 como confiabilidade da acurácia), é a versão da professora; marque se for a única que fala de F1 como indicador de acurácia relevante.

---

## 7. Especificidade (slides 30 a 32)

### 7.1 Definição (slide 31)

O slide 31: a **especificidade (specificity)** é a proporção de casos **negativos** identificados corretamente. Foca nos falsos positivos. Responde: *de todos os valores negativos, quantos eu realmente classifiquei como negativos?*

```
Especificidade = VN / (VN + FP)
```

Ela é o "espelho" da revocação: a revocação olha os positivos reais, a especificidade olha os **negativos reais**.

### 7.2 Hotel com números (slide 32, exemplo nosso)

```
Especificidade = 52 / (52 + 18) = 52/70 ≈ 0,743
```

De 70 reservas que não seriam canceladas, o modelo reconheceu 52.

### 7.3 Taxa de falsos positivos (FPR) [complemento, mas necessário para a ROC]

```
FPR = FP / (FP + VN) = 1 − Especificidade
```

No hotel: 18/70 ≈ 0,257 (= 1 − 0,743). O slide 33 usa a expressão "1 − especificidade" como eixo da curva ROC.

### 7.4 Quadro das quatro métricas no mesmo exemplo

| Métrica | Fórmula | Hotel (nosso) | Quem não entra na conta |
| :-- | :-- | :-- | :-- |
| Acurácia | (VP+VN)/total | 0,72 | nenhum |
| Precisão | VP/(VP+FP) | 0,526 | VN, FN |
| Revocação | VP/(VP+FN) | 0,667 | VN, FP |
| Especificidade | VN/(VN+FP) | 0,743 | VP, FN |
| F1 | 2PR/(P+R) | 0,588 | VN |

---

## 8. Curva ROC e AUC (slides 33 e 34)

### 8.1 O que o slide 33 diz

O slide 33: **ROC (Receiver Operating Characteristics)** e **AUC (Area Under the Curve)** são métricas muito usadas em classificação **binária**. Funcionam de forma parecida com a matriz de confusão: plota-se a **sensibilidade** (taxa de verdadeiros positivos) contra **1 − especificidade** (taxa de falsos positivos). Além disso, passa-se um parâmetro **threshold (T)**, que "geralmente é escolhido como 0,5".

Eixos:

- Eixo Y: **TPR** = sensibilidade = revocação = VP/(VP+FN).
- Eixo X: **FPR** = 1 − especificidade = FP/(FP+VN).

### 8.2 Divergência: um limiar ou todos?

O slide diz que o limiar T é "geralmente 0,5". Mas **a curva ROC existe justamente porque varia T**:

- Cada limiar T dá **um ponto** (FPR, TPR) do gráfico.
- A **curva** é o conjunto de pontos obtido ao varrer **todos** os limiares.
- O ponto do T = 0,5 é só um dos pontos da curva.

**Limiar (threshold)** = o corte que transforma o score do modelo (por exemplo, probabilidade 0,82) em decisão: score ≥ T vira positivo, score < T vira negativo. Subir T deixa o modelo mais "exigente": tende a ter menos FP (precisão em geral sobe) e menos positivos encontrados (recall em geral cai). Baixar T faz o oposto. Isso é uma **tendência**, não uma lei exata.

> **Se perguntarem na prova:** "o que varia ao longo da curva ROC?" Resposta: o limiar de decisão. Se a questão copiar o slide ("passa-se um T, geralmente 0,5"), entenda que 0,5 é o valor usual quando se fixa um único corte.

### 8.3 Exemplo nosso: construindo os pontos à mão

Oito amostras: quatro negativas e quatro positivas, com o score que o modelo deu (maior = mais positivo). Verifiquei com `roc_curve`.

```
negativos (real 0): scores 0,10  0,30  0,40  0,80
positivos (real 1): scores 0,35  0,60  0,70  0,90
```

Para cada limiar T, "positivo" = score ≥ T:

| Limiar T | FPR (FP / 4) | TPR (VP / 4) |
| :-- | :-- | :-- |
| acima de 0,90 (nada é positivo) | 0 | 0 |
| 0,90 | 0 | 0,25 |
| 0,80 | 0,25 | 0,25 |
| 0,60 | 0,25 | 0,75 |
| 0,40 | 0,50 | 0,75 |
| 0,35 | 0,50 | 1,00 |
| 0,10 (tudo é positivo) | 1,00 | 1,00 |

Observe: os extremos são sempre (0,0) (nada é positivo) e (1,1) (tudo é positivo). Em T = 0,5 temos um ponto intermediário (FP = 1, VP = 3, ou seja FPR = 0,25 e TPR = 0,75).

### 8.4 Como é a figura (descrição, sem desenho)

Imagine um quadrado de lado 1, com FPR no eixo horizontal e TPR no vertical.

| Elemento | Onde fica | Significa |
| :-- | :-- | :-- |
| **Diagonal** (do canto inferior esquerdo (0,0) ao superior direito (1,1)) | y = x | Modelo que chuta ao acaso; AUC = 0,5 |
| **Canto superior esquerdo** (FPR = 0, TPR = 1) | ponto (0, 1) | Classificador perfeito: acha todos os positivos sem nenhum alarme falso |
| **Curva de um bom modelo** | acima da diagonal, abraçando o canto superior esquerdo | Quanto mais alta e mais afastada da diagonal, melhor |
| **Curva abaixo da diagonal** | y < x | Pior que o acaso (ver 8.6) |

O slide 34 diz exatamente isso: *quanto mais alta e mais distante da linha diagonal, melhor.* (A figura do slide 34 não foi conferida.)

### 8.5 AUC (slide 34)

Se é difícil comparar curvas a olho, resume-se a ROC em um número: a **AUC**, a área sob a curva ROC. O slide 34: é um número **de 0 a 1** que mostra como o modelo está performando; **quanto mais próximo de 1, melhor**.

No exemplo da seção 8.3, a AUC é 0,75 (verifiquei com `roc_auc_score`).

**Interpretação probabilística** [complemento]: a AUC é a probabilidade de o modelo dar um score maior a um positivo sorteado do que a um negativo sorteado. No exemplo: de 16 pares (positivo, negativo), 12 têm o positivo acima do negativo: 12/16 = 0,75.

### 8.6 Faixas de AUC e AUC menor que 0,5 [complemento, fora dos slides]

- AUC = 1,0: separação perfeita.
- AUC = 0,5: equivale ao acaso (a diagonal).
- AUC < 0,5: pior que o acaso; em geral indica que o modelo está **invertido** (trocar as classes dá 1 − AUC).
- Faixas como "0,7 a 0,9 é bom, acima de 0,9 é excelente" são **regras práticas que variam de autor para autor**. Os slides só dizem "0 a 1; mais perto de 1 é melhor". Não decore faixas como se fossem da professora.

### 8.7 A ROC pede scores, não rótulos (e o que acontece se passar rótulos)

Para a curva fazer sentido, passe **probabilidades ou scores** (`predict_proba(X_test)[:, 1]`). O que acontece se passar `predict` (0/1)?

- O `roc_auc_score` **funciona e devolve um número**, sem erro. Verifiquei.
- Com rótulos binários a "curva" tem **um único ponto interior** (o do corte já aplicado), e a AUC passa a ser `(1 + TPR − FPR) / 2`. Verifiquei: no experimento da seção 11, TPR = 0,806 e FPR = 0,007 deram 0,8995 por `roc_auc_score(y_test, y_pred)`, igual à fórmula, contra 0,9736 com as probabilidades.
- Ou seja, não é "área de um ponto degenerado": é a área do polígono que liga (0,0), esse ponto e (1,1). Funciona, mas **joga fora a informação de ranking** e subestima o modelo. É o erro de lógica clássico em questões de código.

---

## 9. Na prática no scikit-learn (slides 35 e 36)

Os slides 35 e 36 são figuras (relatório de classificação, não abertas por mim). O texto do slide 35 define **suporte** como o **número de amostras de cada espécie**. "Espécie" indica que o exemplo dos slides tem várias classes (multiclasse), e não é um problema binário.

`classification_report(y_true, y_pred)` mostra, por classe, precisão, revocação, F1 e **suporte (support)** (quantas amostras reais há daquela classe), mais as linhas `accuracy`, `macro avg` e `weighted avg`.

**Exemplo nosso (não é o do slide)**, binário, mesmos dados da seção 2.4 (executei; a saída abaixo é a real):

```python
from sklearn.metrics import classification_report

y_true = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
y_pred = [0, 0, 1, 0, 1, 1, 1, 0, 1, 1]
print(classification_report(y_true, y_pred, target_names=["Classe 0", "Classe 1"]))
```

```text
              precision    recall  f1-score   support

    Classe 0       0.75      0.75      0.75         4
    Classe 1       0.83      0.83      0.83         6

    accuracy                           0.80        10
   macro avg       0.79      0.79      0.79        10
weighted avg       0.80      0.80      0.80        10
```

Como ler: para a "Classe 1" (positiva): VP = 5, FP = 1, FN = 1, então precisão = 5/6 = 0,83 e revocação = 5/6 = 0,83. Para a "Classe 0", o relatório trata a classe 0 como se fosse a positiva (precisão = 3/4, revocação = 3/4). A linha `support` mostra 4 e 6: o teste tem 4 negativos e 6 positivos.

---

## 10. Mais de duas classes e o parâmetro `average` [complemento, fora dos slides]

Os slides 35 e 36 mostram um relatório com várias espécies, então a pergunta "e se tiver mais de duas classes?" é natural. As métricas por classe ficam iguais; o que muda é **como juntar** os resultados em um só número.

**Exemplo nosso:** 3 classes, 20 amostras (suportes 10, 6 e 4). Matriz (linhas = real, colunas = previsto):

```
            prev 0  prev 1  prev 2
real 0 (10)    8       1       1
real 1 (6)     1       4       1
real 2 (4)     1       0       3
```

Precisão por classe (coluna): 8/10 = 0,80; 4/5 = 0,80; 3/5 = 0,60. Revocação por classe (linha): 8/10 = 0,80; 4/6 ≈ 0,67; 3/4 = 0,75. Acurácia = (8 + 4 + 3)/20 = 0,75.

| `average=` | O que faz | F1 no exemplo |
| :-- | :-- | :-- |
| `"macro"` | média simples dos F1 de cada classe (todas pesam igual) | 0,731 |
| `"weighted"` | média dos F1 ponderada pelo suporte | 0,752 |
| `"micro"` | soma VP, FP, FN de todas as classes e calcula uma vez | 0,750 (igual à acurácia) |
| `None` | devolve um valor por classe | [0,80, 0,727, 0,667] |

- A **macro** serve para ver se o modelo vai bem na **classe pequena**, porque cada classe vale igual.
- A **weighted** é dominada pela classe grande.
- Em multiclasse com um rótulo por amostra, **micro-precisão = micro-recall = micro-F1 = acurácia** (confirmado no exemplo).

**O erro que todo iniciante comete.** O padrão das funções é `average="binary"`, que só funciona com 2 classes. Com 3 classes:

```python
precision_score(y_true, y_pred)   # ValueError: Target is multiclass but average='binary'.
```

Verifiquei o erro. Corrija com `average="macro"` (ou `"weighted"`, `"micro"`, `None`).

**Outros parâmetros úteis:**

- `pos_label=`: diz qual classe é a "positiva" no modo binário (por padrão, o rótulo `1`). Em `[0,1,1]` x `[0,1,0]`, `precision_score(..., pos_label=0)` considera a classe 0 como positiva.
- `zero_division=`: o que devolver quando o denominador é zero (ex.: o modelo nunca previu positivo e a precisão é 0/0). Sem ele, o scikit-learn avisa (`UndefinedMetricWarning`) e usa 0.

---

## 11. Fluxo completo e ordem correta das chamadas [complemento: a prova cobre trechos de código]

A ordem que o scikit-learn espera:

```
1. separar dados em treino e teste       train_test_split
2. criar o modelo                         ex.: LogisticRegression()
3. treinar SÓ com o treino                model.fit(X_train, y_train)
4. prever no teste                        model.predict(X_test)   e  model.predict_proba(X_test)[:, 1]
5. medir comparando com o REAL do teste   métrica(y_test, previsão)
```

Código completo e executável (`python -I`, scikit-learn instalado; os dados são sintéticos, com 10% de positivos, para lembrar o desbalanceamento). Executei e os valores comentados são os reais:

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, roc_curve,
)

# 1. dados (90% negativos, 10% positivos) e separação treino/teste
X, y = make_classification(n_samples=1000, weights=[0.9, 0.1], random_state=0)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

# 2 e 3. criar e treinar (apenas com o treino)
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 4. prever no teste: rótulos (0/1) e probabilidade da classe positiva
y_pred = model.predict(X_test)
y_probs = model.predict_proba(X_test)[:, 1]

# 5. métricas: SEMPRE (real, previsto)
cm = confusion_matrix(y_test, y_pred)           # [[VN, FP], [FN, VP]] = [[267, 2], [6, 25]]
print(cm)
print(accuracy_score(y_test, y_pred))           # 0.973
print(precision_score(y_test, y_pred))          # 0.926
print(recall_score(y_test, y_pred))             # 0.806
print(f1_score(y_test, y_pred))                 # 0.862

# AUC e curva: com as PROBABILIDADES, não com y_pred
print(roc_auc_score(y_test, y_probs))           # 0.974
fpr, tpr, thresholds = roc_curve(y_test, y_probs)
```

Comparação útil: um "modelo bobo" que prevê sempre 0 neste mesmo teste tem acurácia 0,897 e **recall 0** (verifiquei). Compare com a acurácia 0,973 do modelo real: a acurácia sozinha diferencia pouco, o recall mostra o abismo.

### Erros de lógica típicos (formato de prova)

| Código | O que há de errado |
| :-- | :-- |
| `model.fit(X_test, y_test)` e depois avaliar no mesmo teste | Treinou no teste: a nota é otimista e inútil |
| `precision_score(y_pred, y_test)` | Argumentos invertidos (previsto, real). A métrica troca de papel: precisão vira recall. Verifiquei no hotel: 0,526 virou 0,667 |
| `roc_auc_score(y_test, model.predict(X_test))` | Passou rótulos 0/1 em vez de probabilidades; roda, mas gera AUC pobre (seção 8.7) |
| `accuracy_score(y_train, model.predict(X_train))` apresentado como desempenho | Mediu no treino, não no teste |
| `precision_score(y_test, y_pred)` com 3 classes | `ValueError` por falta de `average=` |
| `confusion_matrix(y_pred, y_test)` | Matriz transposta: o que era FP vira FN |
| Avaliar acurácia como "a" métrica em base 90/10 | Esconde que o recall é baixo |

---

## 12. Conclusão (slide 37)

O slide 37 diz, em resumo:

- As métricas auxiliam a **escolher o melhor modelo** entre as possibilidades.
- **Todas essas métricas variam entre 0 e 1, e quanto mais próxima de 1, melhor.**
- **Não existe a melhor métrica**: depende do cenário e dos objetivos. As métricas apenas ajudam a tomar a decisão.

### Guia de escolha [resumo nosso, a tabela não está no slide]

| Situação | Métrica a priorizar | Motivo |
| :-- | :-- | :-- |
| Classes equilibradas e erros de custo parecido | Acurácia | Simples e representativa |
| Classes muito desbalanceadas | Matriz de confusão, recall da classe rara, F1 | A acurácia esconde a falha na classe rara |
| Falso positivo é mais caro (vídeo infantil, investimento: slide 19) | Precisão | Reduz FP |
| Falso negativo é mais caro (doença grave: slide 23; fraude: slide 22) | Revocação | Reduz FN |
| Querer equilibrar precisão e revocação | F1 | Média harmônica |
| Importam os negativos reais | Especificidade | VN/(VN+FP) |
| Comparar modelos sem fixar o limiar | AUC da ROC | Resume todos os limiares |

### Tabela de fórmulas

```
Acurácia       = (VP + VN) / (VP + VN + FP + FN)
Precisão       = VP / (VP + FP)
Revocação      = VP / (VP + FN)        (= sensibilidade = TPR)
Especificidade = VN / (VN + FP)        (= 1 − FPR)
FPR            = FP / (FP + VN)
F1             = 2 × P × R / (P + R)
```

### Perguntas rápidas para se testar

1. Em qual métrica o VN não entra? (precisão, revocação e F1)
2. Qual dos dois erros, FP ou FN, a revocação procura reduzir? (FN)
3. Qual valor tem a AUC de um modelo que chuta ao acaso? (0,5, a diagonal)
4. No scikit-learn, qual é o primeiro argumento das métricas? (o real, `y_true`)
5. Quais são os eixos da ROC? (X: 1 − especificidade = FPR; Y: sensibilidade = TPR)

---

## 13. O que ficou sem cobrir

- As **figuras** dos slides 4, 8, 9, 11, 12, 14, 17, 18, 21 a 24, 26, 28, 29, 31 a 36 não foram abertas: o texto só usa o que está escrito nos slides e as contas que indicam. A matriz e as métricas do hotel dos slides 12, 18, 28, 29 e 32 são **exemplo nosso** coerente com a acurácia de 72% do slide 18.
- Confira os slides 35 e 36 (relatório por espécie) diretamente na aula antes da prova.
