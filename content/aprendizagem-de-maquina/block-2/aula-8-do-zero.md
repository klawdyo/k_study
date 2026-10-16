# Aula 8 do zero: Árvores de Decisão e de Regressão

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e um exemplo concreto, depois com o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção) e passa pelos 47 slides; os slides que são só figuras (marcados como [IMAGEM] na extração) são descritos pelo que o texto vizinho diz, e isso é avisado quando acontece.

**A pergunta que a aula inteira responde:** *como um algoritmo descobre sozinho, olhando dados históricos, quais perguntas de sim/não fazer (e em que ordem) para chegar a uma decisão?*

Analogia de software: é um programa de `if/else` aninhados que **você não escreve**; o algoritmo escreve as condições e os números de corte para você, a partir de exemplos.

Convenção: tudo que for **exemplo nosso** (não está nos slides) é marcado assim. Tudo que for **[Complemento]** é matéria fora dos slides, útil para entender, mas que a prova não deve cobrar.

---

## 1. O que é uma árvore de decisão (slides 1 a 3)

Os slides 1 e 2 são capa e título. O slide 3 define a árvore como uma **estrutura de dados** (você já conhece: nós ligados por conexões). Os termos do slide:

| Termo do slide | O que é | Analogia de software |
| :-- | :-- | :-- |
| **Nó (nodo)** | elemento que armazena uma informação | um objeto `Node` |
| **Raiz** | nó de partida, no topo | o `main()` da decisão: onde tudo começa |
| **Nós filhos** | os nós ligados por conexões a partir de um nó | sub-árvores |
| **Folha (nó terminal)** | nó sem filhos | `return` final |
| **Regras nos nós** | cada nó guarda um teste sobre um atributo | a condição de um `if` |
| **Decisão** | as folhas representam a decisão a tomar | o valor retornado |

Em palavras do slide 3: a árvore de decisão **armazena regras nos nós, e as folhas representam a decisão**.

Um jeito de enxergar, em código (**exemplo nosso**, inventado para a explicação):

```python
def classificar(sol, vento):
    if vento <= 4.5:
        if sol <= 5:
            return "não vai à praia"
        return "vai à praia"
    return "não vai à praia"
```

Isso é uma árvore de decisão com 3 folhas. A diferença para o software tradicional: aqui **você** inventou os números 4,5 e 5. No aprendizado de máquina, o **algoritmo de indução** examina uma base de exemplos (cada um com atributos e a resposta correta) e descobre **quais perguntas** e **quais números de corte** funcionam melhor.

Vocabulário rápido (cada termo em uma frase):

- **Atributo (feature):** uma coluna de entrada, como `sol` ou `vento`.
- **Alvo (target):** a coluna que queremos prever, como "vai à praia".
- **Classe:** cada valor possível do alvo quando ele é uma categoria ("sim", "não").
- **Indução:** o processo de construir a árvore a partir dos dados (o "treino").

> **Se perguntarem na prova:** a árvore é uma estrutura com raiz, nós internos que guardam regras (testes sobre atributos) e folhas que representam a decisão.

---

## 2. Como a árvore é construída e testada (slide 4)

O slide 4 diz duas coisas:

1. **Treinamento:** o algoritmo constrói a árvore **da raiz até as folhas, de cima para baixo (top-down)**. A cada passo ele identifica o **atributo mais importante, chamado de divisor**: aquele que faz a **maior diferença** para classificar as amostras existentes.
2. **Teste:** a árvore pronta é testada e usada para classificar um **novo conjunto de amostras independentes e separadas das usadas no treinamento**.

Analogia: o treino é você escrevendo o código olhando os exemplos; o teste é rodar o código em casos que você nunca viu. Se medir só nos casos que você usou para escrever, o resultado é otimista demais (assunto da Aula 4).

O resto do slide é uma figura, não descrita no texto extraído.

> **Se perguntarem na prova:** construção top-down, escolhendo a cada nó o atributo divisor que mais ajuda a separar as classes; teste com amostras independentes das de treino.

---

## 3. Exemplo da praia (slides 5 a 8)

Os slides 5 a 8 trazem um exemplo visual: **ir à praia ou não ir à praia**. O texto extraído mostra só os rótulos; os pontos do gráfico são imagem. O que o texto garante:

- Slide 6: dois grupos de pontos, "ir à praia" e "não ir à praia", provavelmente num plano com dois atributos.
- Slide 7: "**Separando os dados em duas classes**": primeiro teste, com as perguntas **SOL > ?** e **VENTO > ?**, e uma folha "NÃO VAI À PRAIA".
- Slide 8: o mesmo, com a árvore crescida: depois do primeiro teste, um segundo teste, e a folha "VAI À PRAIA".

A ideia que o exemplo ensina: **cada pergunta de sim/não corta o plano em dois pedaços**, e a sequência de perguntas isola a região dos "vai à praia" das demais.

**Exemplo nosso (números inventados, mas rodei no scikit-learn).** Dez dias, com nota de sol (0 a 10), nota de vento (0 a 10) e a decisão:

| Dia | Sol | Vento | Vai à praia? |
| :-- | :-- | :-- | :-- |
| 1 | 9 | 2 | sim |
| 2 | 8 | 3 | sim |
| 3 | 7 | 8 | não |
| 4 | 9 | 7 | não |
| 5 | 3 | 2 | não |
| 6 | 2 | 6 | não |
| 7 | 4 | 3 | não |
| 8 | 8 | 1 | sim |
| 9 | 1 | 9 | não |
| 10 | 6 | 2 | sim |

A árvore que o scikit-learn aprende:

```text
|--- vento <= 4.50
|   |--- sol <= 5.00
|   |   |--- class: 0     (não vai)
|   |--- sol >  5.00
|   |   |--- class: 1     (vai)
|--- vento >  4.50
|   |--- class: 0         (não vai)
```

Leitura em português: "se tem muito vento (acima de 4,5), não vai; se tem pouco vento mas pouco sol (até 5), não vai; pouco vento e muito sol, vai". É exatamente o formato SOL > ? / VENTO > ? do slide.

> **Se perguntarem na prova:** a árvore divide o espaço de atributos por perguntas sucessivas; cada folha corresponde a uma região associada a uma classe.

---

## 4. Exemplo "Está em forma?" (slides 9 e 10)

Os slides 9 e 10 repetem a ideia com outro exemplo: **está em forma ou não?** O slide 10 traz os testes:

| Nível | Teste do slide | Saídas |
| :-- | :-- | :-- |
| Raiz | `CORRIDA < 2,6` | SIM e NÃO levam a outros testes |
| Um filho | `ABDOMINAL < 50` | resultados "não está em forma" / "está em forma" |
| Outro filho | `ABDOMINAL < 38` | resultados "está em forma" / "não está em forma" |

Atenção a dois pontos que o texto extraído deixa claro:

1. A árvore tem **três testes** (um na raiz e dois no segundo nível) e o atributo `ABDOMINAL` aparece **duas vezes**, com **cortes diferentes** (50 e 38). Isso antecipa o slide 43: um atributo numérico pode ser reusado.
2. O texto extraído **não diz qual ramo (SIM ou NÃO) leva a qual teste de ABDOMINAL**, nem a qual folha cada seta vai: isso está só na figura. Por isso não afirmo aqui a ordem exata das folhas.

O esqueleto em código (**exemplo nosso**, ordem dos ramos escolhida por nós, só para ilustrar que são três `if` no total):

```python
def esta_em_forma(corrida, abdominal):
    if corrida < 2.6:
        if abdominal < 50:
            return "está em forma"
        return "não está em forma"
    if abdominal < 38:
        return "está em forma"
    return "não está em forma"
```

> **Se perguntarem na prova:** o mesmo atributo numérico pode aparecer em níveis diferentes da árvore com cortes diferentes (no slide, ABDOMINAL < 50 e ABDOMINAL < 38).

---

## 5. Dividir para conquistar e as famílias de algoritmos (slide 11)

O slide 11 diz que a árvore usa a estratégia **dividir para conquistar**: um problema complexo é dividido em problemas mais simples, e **recursivamente** aplica-se a mesma estratégia. As soluções dos subproblemas são combinadas, na forma de uma árvore, para resolver o problema original.

Analogia: é o `merge sort` e a busca binária. Você parte o problema, resolve as partes pequenas com o mesmo método e junta.

Os algoritmos citados no slide 11:

| Algoritmo | Quem / quando (segundo o slide) | Observação do slide |
| :-- | :-- | :-- |
| **ID3** (Iterative Dichotomiser 3) | Quinlan, 1979 | o primeiro da lista |
| **C4.5 e C5.0** | Quinlan, 1993 | **sucessores do ID3** |
| **CART** (Classification And Regression Tree) | Breiman et al., 1984 | **é o que o scikit-learn usa** |

**Divergência de data.** O slide diz ID3 em 1979. Na literatura o artigo mais citado de ID3 é de 1986. **Na prova, responda 1979** (versão do slide).

**[Complemento: fora dos slides]** Na literatura, o ID3 e o C4.5 se associam a ganho de informação (entropia) e o CART a Gini; o C4.5 usa uma variação chamada razão de ganho. Os slides apresentam entropia e Gini como "critérios de divisão" sem amarrar cada um a um algoritmo, então não use essa associação como fato "da professora".

> **Se perguntarem na prova:** dividir para conquistar; ID3 (1979), C4.5/C5.0 (1993, sucessores do ID3), CART (1984); o scikit-learn usa CART.

---

## 6. Árvore de decisão x árvore de regressão (slide 12)

O slide 12: os modelos em árvore se chamam **árvores de decisão** quando o problema é de **classificação** (alvo é categoria) e **árvores de regressão** quando é de **regressão** (alvo é número). A interpretação do modelo e os algoritmos de indução são **muito semelhantes** nos dois casos.

| | Árvore de decisão (classificação) | Árvore de regressão |
| :-- | :-- | :-- |
| Alvo | categoria ("fraude", "não fraude") | número (preço, tempo) |
| Folha devolve | a classe da folha (a mais frequente entre os exemplos de treino que caíram ali) | um número (a **média** dos alvos dos exemplos da folha) |
| Qualidade do corte | Gini ou entropia (slide 31) | erro quadrático médio, MSE (slide 31) |
| Classe no scikit-learn | `DecisionTreeClassifier` | `DecisionTreeRegressor` |

A parte "folha devolve a classe mais frequente" e "a média na folha" não está literalmente no slide 12; vem do slide 32 (média da previsão) e é a leitura padrão. Mais adiante (seção 12) há um exemplo numérico.

> **Se perguntarem na prova:** classificação gera árvore de decisão; regressão gera árvore de regressão; a lógica de indução é muito semelhante.

---

## 7. A árvore como regiões do espaço (slides 13 e 14)

Os slides 13 e 14 dão a definição geométrica. Cada **nó** corresponde a uma **região** do espaço definido pelos atributos (se há dois atributos, x1 e x2, o espaço é um plano). Três afirmações do slide, importantes para a prova:

1. As regiões definidas pelas **folhas** são **mutuamente excludentes**: a **interseção** das regiões de quaisquer duas folhas é **vazia** (slide 14). Um exemplo nunca cai em duas folhas.
2. A **união** de todas as regiões (todas as folhas) é **U**, o espaço inteiro (slides 13 e 14). Não sobra nenhum canto sem folha.
3. Consequência (slide 14): a árvore **abrange todo o espaço de instâncias**, portanto pode **fazer predição para qualquer exemplo de entrada**.

Analogia de software: as folhas são como o `default` de um `switch` completo; não existe entrada sem destino.

O que as figuras dos slides mostram (segundo a legenda): uma árvore e a divisão correspondente no espaço x1 × x2. Como cada teste é do tipo "atributo ≤ número", cada corte é uma **reta paralela a um eixo** e as regiões são retângulos (ou "caixas" em mais dimensões). Isso é a consequência geométrica dos testes simples; os slides mostram a figura, e a frase "retas paralelas aos eixos" é a leitura dela.

> **Se perguntarem na prova:** as regiões das folhas são mutuamente excludentes (interseção vazia) e a união delas cobre todo o espaço; logo a árvore prevê para qualquer entrada.

---

## 8. Critérios de divisão: o problema (slide 15)

O slide 15 abre a seção "Critérios de divisão". A pergunta: **em cada nó, qual atributo (e qual corte) devo usar?**

Intuição: você tem um balde com bolas de duas cores misturadas e quer separá-las fazendo perguntas. Uma boa pergunta deixa um lado com quase só bolas azuis e o outro com quase só vermelhas. Uma pergunta ruim deixa os dois lados tão misturados quanto antes. Precisamos de um **número** que meça "mistura" para comparar as perguntas. Esse número é a **impureza**:

- **Nó puro:** todas as amostras são da mesma classe (impureza zero).
- **Nó impuro:** classes misturadas (impureza alta).

Há duas medidas nos slides: **entropia** (com **ganho de informação**) e **índice de Gini**.

---

## 9. Entropia e ganho de informação (slides 16 a 24)

### 9.1 Entropia (slides 16 e 17)

O slide 16: a **entropia mede a aleatoriedade** de uma variável aleatória. Se ela pode assumir valores a1, ..., av com probabilidades p1, ..., pv, a entropia é dada por uma fórmula que aparece como imagem no slide. O slide 19 mostra a versão para duas classes (texto extraído):

```text
Entropia = −(p1 · log₂ p1 + p2 · log₂ p2)
```

Para qualquer número de classes (a forma geral, igual à da imagem do slide 16):

```text
H = −Σ pᵢ · log₂(pᵢ)     (a soma é sobre as classes i)
```

Dois fatos que valem ouro: se um p vale 0, o termo é considerado 0; e `log₂(1) = 0`.

**Intuição.** Entropia é a "incerteza": quantas perguntas de sim/não, em média, você precisa para adivinhar a classe de um exemplo sorteado do nó. Se o nó é 100% de uma classe, não precisa de pergunta nenhuma: 0. Se é 50/50, precisa de uma pergunta: 1.

**Tabela de pontos (exemplo nosso, duas classes, p = proporção da classe "sim"):**

| p (sim) | p (não) | Entropia |
| :-- | :-- | :-- |
| 0,0 | 1,0 | 0 |
| 0,1 | 0,9 | ≈ 0,469 |
| 0,25 | 0,75 | ≈ 0,811 |
| 0,5 | 0,5 | 1 |
| 1,0 | 0,0 | 0 |

**Cuidado com a faixa.** O valor máximo 1 só vale para **duas classes**. Com C classes igualmente prováveis, a entropia máxima é log₂(C). Exemplo (conferido por cálculo): três classes com 1/3 cada dão H ≈ 1,585, **maior que 1**. O slide 25 diz que a entropia varia em [0, 1], o que é correto para o caso binário que o curso usa.

O slide 17 diz o papel da entropia na árvore: ela mede a **aleatoriedade (dificuldade para predizer) do atributo alvo**; a cada nó de decisão, o atributo que **mais reduz** a aleatoriedade do alvo é escolhido para dividir os dados.

### 9.2 Ganho de informação (slide 18)

O slide 18: o **ganho de informação** é uma **redução na entropia**. `ganho(S, A)` é a redução esperada na entropia de S ao ordenar (dividir) pelo atributo A. Informalmente, é a **diferença entre a entropia do conjunto de exemplos e a soma ponderada da entropia das partições**.

O slide 19 escreve em texto:

```text
Ganho = Entropia(pai) − Σ Peso(filho) · Entropia(filho)
```

onde o **peso** de um filho é a fração dos exemplos do pai que foram para ele. Na forma completa:

```text
Ganho(S, A) = H(S) − Σ (|S_v| / |S|) × H(S_v)
```

Aqui `|S|` é a quantidade de exemplos do nó pai e `|S_v|` a quantidade que foi para o filho v. **Por que ponderar:** um filho com 1 exemplo não deve valer tanto quanto um com 50. É a média ponderada da entropia dos filhos.

**Regra de decisão:** calcula-se o ganho de cada atributo candidato e escolhe-se o **maior**.

### 9.3 O exemplo passo a passo (slides 19 a 24)

**Slides 19 e 20.** Seis exemplos, alvo com **Sim = 50% (3 amostras)** e **Não = 50% (3 amostras)**. A entropia do pai:

```text
H(pai) = −(½·log₂ ½ + ½·log₂ ½) = −(½·(−1) + ½·(−1)) = 1
```

**Slides 21, 22 e 23.** Três atributos candidatos, cada um dividindo os 6 exemplos em dois grupos:

- Slide 21: **Salário** (ALTO / BAIXO).
- Slide 22: **Localização** (Perto / Longe).
- Slide 23: **Função** (interessante / desinteressante).

**Slide 24: resultados.**

```text
Ganho de Salário      = 0,08
Ganho de Localização  = 0
Ganho de Função       = 1
```

O maior é **Função**, que vira o teste da raiz. O slide acrescenta: **se tivesse optado por Salário, a árvore continuaria crescendo** (os filhos continuariam impuros).

**Quais contagens produzem esses números?** O texto extraído lista os rótulos mas não diz como se distribuem entre os filhos (isso está na figura). As contagens abaixo são **exemplo nosso**, escolhidas porque reproduzem exatamente os ganhos do slide (calculei):

| Atributo | Filho 1 (sim / não) | Filho 2 (sim / não) | Entropia filho 1 | Entropia filho 2 | Entropia ponderada | Ganho |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Salário | 1 / 2 | 2 / 1 | 0,918 | 0,918 | 3/6·0,918 + 3/6·0,918 = 0,918 | 1 − 0,918 = **0,082** |
| Localização | 1 / 1 (2 exemplos) | 2 / 2 (4 exemplos) | 1 | 1 | 2/6·1 + 4/6·1 = 1 | 1 − 1 = **0** |
| Função | 3 / 0 | 0 / 3 | 0 | 0 | 0 | 1 − 0 = **1** |

Nota sobre a linha de Localização: para dar ganho zero, cada filho precisa manter a proporção 50/50 do pai (aqui, partes de 2 e 4 exemplos, ambas metade sim e metade não). O que importa: **filhos tão misturados quanto o pai = ganho 0**.

Passo a passo do cálculo de Salário (as contas são as mesmas para qualquer atributo):

```text
H(filho com 1 sim e 2 não) = −(1/3·log₂ 1/3 + 2/3·log₂ 2/3) = 0,528 + 0,390 = 0,918
Ganho(Salário) = 1 − (3/6 · 0,918 + 3/6 · 0,918) = 1 − 0,918 = 0,082  ≈ 0,08
```

Moral: ganho 0 significa "esta pergunta não ajudou nada"; ganho igual à entropia do pai (aqui, 1) significa "esta pergunta resolveu tudo".

**Ganho calculado no exemplo da praia (exemplo nosso).** No exemplo da seção 3 há 4 "sim" e 6 "não". O melhor primeiro corte, `vento ≤ 4,5`, manda 6 dias para a esquerda (4 sim, 2 não) e 4 dias para a direita (0 sim, 4 não):

```text
H(pai)         = −(0,4·log₂ 0,4 + 0,6·log₂ 0,6) = 0,971
H(esquerda)    = H(4 sim, 2 não) = 0,918
H(direita)     = H(0 sim, 4 não) = 0
Ganho          = 0,971 − (6/10 · 0,918 + 4/10 · 0) = 0,971 − 0,551 = 0,420
```

> **Se perguntarem na prova:** entropia mede aleatoriedade/dificuldade de predizer o alvo; ganho de informação = entropia do pai menos a soma ponderada da entropia dos filhos; escolhe-se o atributo de **maior** ganho; no exemplo, Função (ganho 1) vence Salário (0,08) e Localização (0).

---

## 10. Índice de Gini (slides 25 a 29)

### 10.1 A definição e a comparação com a entropia (slide 25)

O slide 25: o Índice de Gini é "outro algoritmo de árvore de decisão" que, **semelhante à entropia, mede o grau de desordem** da variável, mas o cálculo é diferente (a fórmula é imagem). A fórmula padrão é:

```text
Gini(S) = 1 − Σ pᵢ²     (soma sobre as classes i)
```

Casos de duas classes:

```text
nó puro:   Gini = 1 − (1² + 0²)       = 0
nó 50/50:  Gini = 1 − (0,5² + 0,5²)   = 0,5
```

O slide 25 afirma:

1. Gini está em **[0, 0,5]** e a entropia em **[0, 1]**.
2. A entropia é **computacionalmente mais complexa** (usa logaritmos), então o Gini é **mais rápido**.
3. Mas os resultados com entropia são **um pouco melhores**.

**Divergências, com as duas versões:**

| Ponto | Versão do slide | Literatura |
| :-- | :-- | :-- |
| Faixa | Gini em [0, 0,5] e entropia em [0, 1] | vale **só para 2 classes**; com C classes o Gini máximo é 1 − 1/C e a entropia máxima é log₂ C (3 classes iguais: Gini ≈ 0,667 e entropia ≈ 1,585) |
| Qualidade | entropia dá resultados "um pouco melhores" | a diferença prática costuma ser desprezível; as árvores quase sempre ficam parecidas |
| Velocidade | Gini é mais rápido | concorda |

**Na prova:** se a pergunta é "qual critério é mais rápido?", responda Gini. Se for "qual dá resultados um pouco melhores?", a versão da professora é entropia. Se a questão mencionar **duas classes**, as faixas [0, 0,5] e [0, 1] estão certas.

### 10.2 O Gini de uma divisão (slides 26 e 27)

Como com a entropia, cada filho tem seu Gini e a divisão é avaliada pela **média ponderada** dos filhos, onde o peso é a fração dos exemplos:

```text
Gini_divisão = (n_E / n) × Gini(E) + (n_D / n) × Gini(D)
```

**Slide 26: variável A** (8 exemplos no total):

```text
Para A = 1:  prob(0) = 1/3,  prob(1) = 2/3,  peso = 3/8
   Gini = 1 − [(1/3)² + (2/3)²] = 0,44
Para A = 0:  prob(0) = 3/5,  prob(1) = 2/5,  peso = 5/8
   Gini = 1 − [(3/5)² + (2/5)²] = 0,48
Gini_A = 3/8 · 0,44 + 5/8 · 0,48 = 0,46
```

**Slide 27: variável B**, com o corte "B < 27" (4 e 4 exemplos):

```text
Para B < 27:  prob(0) = 1/4, prob(1) = 3/4, peso = 4/8
   Gini = 1 − [(1/4)² + (3/4)²] = 0,37
Para B ≥ 27:  prob(0) = 3/4, prob(1) = 1/4, peso = 4/8
   Gini = 1 − [(3/4)² + (1/4)²] = 0,37
Gini_B = 4/8 · 0,37 + 4/8 · 0,37 = 0,37
```

Dois avisos sobre os slides, ambos conferidos por conta:

1. **Notação.** Os slides escrevem `1 − (1/3)² + (2/3)²`, sem os colchetes. Lida literalmente (1 menos o primeiro quadrado mais o segundo) daria outro número. A conta correta, e a que produz 0,44, é `1 − [(1/3)² + (2/3)²]`: os dois quadrados são **somados primeiro** e depois subtraídos de 1.
2. **Arredondamento.** Os valores exatos são Gini(A=1) = 0,4444, Gini(A=0) = 0,48, Gini_A = **0,4667**; Gini(B) = 0,375 e Gini_B = **0,375**. O slide arredondou ou truncou (0,46 e 0,37). Na prova use os valores do slide; a decisão (B tem Gini menor) não muda.

### 10.3 A decisão e a continuação (slides 28 e 29)

Slide 28: **devemos escolher o atributo com MENOR índice Gini**. Como 0,37 < 0,46, o teste da raiz usa a **Var B**, com ramos `< 27` e `≥ 27`.

Slide 29: depois da primeira divisão, **prossegue-se a construção** buscando, em cada ramo, o próximo atributo com menor Gini.

**Atenção à direção (pegadinha clássica).**

| Critério | Escolhe |
| :-- | :-- |
| Ganho de informação (entropia) | o **maior** ganho |
| Gini | o **menor** Gini ponderado |

A lógica é a mesma: queremos filhos **mais puros**. O ganho mede "quanto a impureza caiu" (maior é melhor); o Gini ponderado mede "quanta impureza sobrou" (menor é melhor).

**Gini ponderado no exemplo da praia (exemplo nosso).** Pai: 4 sim e 6 não.

```text
Gini(pai)      = 1 − (0,4² + 0,6²) = 0,48
Gini(esq.)     = 1 − [(4/6)² + (2/6)²] = 0,444
Gini(dir.)     = 1 − [0² + 1²] = 0
Gini_divisão   = 6/10 · 0,444 + 4/10 · 0 = 0,267
```

A divisão caiu de 0,48 para 0,267, uma boa melhoria. Confira no scikit-learn: `tree_.impurity` da raiz é 0,48 e do filho esquerdo 0,444.

> **Se perguntarem na prova:** Gini = 1 − Σ pᵢ²; compara-se a média ponderada dos filhos; **escolhe-se o menor Gini**; no exemplo B (0,37) vence A (0,46).

---

## 11. Como achar o valor do corte (slides 30 e 31)

O slide 30 coloca a pergunta que fica pendente na árvore: depois de escolher a Var B, **como encontrar o melhor valor de split** (aquele "27")? Quem responde é o slide 31, que descreve o **algoritmo CART** ("o Python usa o algoritmo CART").

Passos do slide 31:

1. **Varredura de atributos:** percorre todas as features (**respeitando a configuração `max_features`**, seção 15).
2. **Avaliação de candidatos:** para cada feature, testa **todos os valores únicos** como possíveis pontos de corte **binários**.
3. **Cálculo de qualidade:** em cada tentativa, calcula a "perda" ou impureza gerada: **Gini ou Entropia** (classificação) ou **MSE** (regressão).
4. **Decisão gulosa (greedy):** compara tudo e escolhe a combinação **feature + valor** de **menor impureza** (ou maior ganho de informação).

**"Guloso"** significa que, em cada nó, escolhe-se o melhor corte **daquele momento**, sem tentar prever se outra escolha renderia uma árvore melhor mais abaixo. Analogia: um algoritmo de troco que sempre pega a maior moeda. Rápido e razoável, mas sem garantia de ótimo global.

### As duas versões sobre o ponto de corte

**O que o slide 31 diz:** o algoritmo testa "todos os valores únicos" como candidatos. O slide 32 mostra a varredura sobre os valores ordenados, separando 1 valor de um lado e o resto do outro, depois 2 e o resto, etc.

**O que o scikit-learn realmente faz (conferido rodando):** os candidatos são os **pontos médios entre dois valores consecutivos** (na ordem crescente), não os próprios valores. Exemplo: para o atributo `[7, 13, 21, 30, 35, 38, 42]`, o sklearn escolheu o limiar **25,5**, que é o ponto médio entre 21 e 30. Nunca "A ≤ 21". O resultado prático é o mesmo particionamento (os exemplos até 21 vão para a esquerda), só muda o número escrito na regra.

Mini-exemplo da quantidade de candidatos (**exemplo nosso**): o atributo `vento` do exemplo da praia tem 7 valores distintos (1, 2, 3, 6, 7, 8, 9), logo há 6 cortes candidatos: 1,5; 2,5; 4,5; 6,5; 7,5; 8,5. O melhor foi 4,5 (entre 3 e 6), exatamente o que a árvore da seção 3 usa.

**Na prova:** "o algoritmo testa todos os cortes binários possíveis entre os valores ordenados do atributo e fica com o de menor impureza". Se a questão disser "todos os valores únicos", esta é a versão do slide e vale. Se pedir o número da regra no scikit-learn, é o ponto médio.

---

## 12. CART na regressão: cortes e custo (slide 32)

O slide 32 mostra a mesma varredura para **regressão**, com o atributo `A = [7, 13, 21, 30, 35, 38, 42]`:

1. Testa um split: `{7}` de um lado e `{13, 21, 30, 35, 38, 42}` do outro.
2. Em cada lado, usa a **média da previsão** (a média dos alvos daquele lado).
3. **Calcula a função custo** (o slide escreve "previsto − real").
4. Testa outro split: `{7, 13}` e `{21, 30, 35, 38, 42}`; de novo média e custo.
5. **Escolhe o split que minimize a função de custo.**

O slide fala "previsto − real"; na prática o erro de cada exemplo é elevado ao quadrado e somado (ou tirada a média), que é o **erro quadrático médio (MSE)** citado no slide 31. Sem o quadrado, erros positivos e negativos se cancelariam.

**Exemplo numérico completo (exemplo nosso).** Atributo A como no slide; alvos inventados, y = 10, 12, 20, 31, 33, 40, 44.

| Split (esquerda / direita) | Média esq. | Média dir. | Soma dos erros ao quadrado |
| :-- | :-- | :-- | :-- |
| {7} / {13..42} | 10,0 | 30,0 | 730,0 |
| {7, 13} / {21..42} | 11,0 | 33,6 | 343,2 |
| {7, 13, 21} / {30..42} | 14,0 | 37,0 | **166,0** |
| {7..30} / {35..42} | 18,25 | 39,0 | 334,75 |
| {7..35} / {38, 42} | 21,2 | 42,0 | 454,8 |
| {7..38} / {42} | 24,3 | 44,0 | 741,3 |

Como se calcula uma linha (a de menor custo): lado esquerdo tem y = 10, 12, 20, média 14; erros ao quadrado = (10−14)² + (12−14)² + (20−14)² = 16 + 4 + 36 = 56. Lado direito tem y = 31, 33, 40, 44, média 37; erros = 36 + 16 + 9 + 49 = 110. Total = 56 + 110 = **166**.

Vence o split `{7, 13, 21}` / `{30, 35, 38, 42}`. O sklearn (`DecisionTreeRegressor(max_depth=1)`) confirmou: limiar 25,5, previsão 14,0 à esquerda e 37,0 à direita.

**Consequência importante:** a árvore de regressão prevê **constante por pedaço**. Qualquer entrada com A ≤ 25,5 recebe 14,0, e qualquer outra recebe 37,0. Isso gera a "escada" de degraus e a incapacidade de **extrapolar** (seção 20).

```python
import numpy as np
from sklearn.tree import DecisionTreeRegressor, export_text

X = np.array([[7], [13], [21], [30], [35], [38], [42]])
y = np.array([10, 12, 20, 31, 33, 40, 44])

reg = DecisionTreeRegressor(max_depth=1).fit(X, y)
print(export_text(reg, feature_names=["A"]))
```

Saída (conferida):

```text
|--- A <= 25.50
|   |--- value: [14.00]
|--- A >  25.50
|   |--- value: [37.00]
```

> **Se perguntarem na prova:** na regressão, cada folha prevê a média dos alvos; o CART testa vários cortes, calcula o custo (erro) com essas médias e escolhe o corte de menor custo.

---

## 13. Regras de parada (slide 33)

O slide 33: depois da primeira divisão, o algoritmo tenta dividir mais as partições, **com a mesma lógica** de redução da entropia. Ele divide progressivamente até que **não seja possível mais dividir**, seja porque:

1. **A subamostra é um único exemplo** (não há o que separar), ou
2. **Encontrou uma regra de parada.**

A regra de parada principal do slide é quando **todos os nós folha são puros** (todas as amostras da folha têm a mesma classificação). As **outras regras de parada** são os **critérios de poda** (slides 34 a 36).

Analogia: a recursão do `dividir()` precisa de um caso-base. Aqui os casos-base são "nó puro", "sobrou um exemplo" e "o critério de poda mandou parar".

**Exemplo nosso:** no exemplo da praia, o nó `vento > 4,5` tem 4 dias, todos "não": é puro, vira folha. O nó `vento ≤ 4,5` tem 4 sim e 2 não: ainda mistura, então divide por `sol ≤ 5` e fica com folhas puras.

---

## 14. Poda e overfitting (slides 34 e 35)

### 14.1 Por que podar (slide 34)

O slide 34: à medida que a árvore cresce, o **número de exemplos que chega a cada nó inferior diminui**; por isso, a **expansão exagerada** faz a **precisão de classificação cair**. Duas causas, ambas do slide:

1. **Atributos com baixo poder preditivo** (ou altamente **correlacionados** com atributos já usados nos nós de cima) entram na árvore, tornando-a **excessivamente especializada** (overfitting).
2. Os nós inferiores, **especialmente as folhas**, ficam muito **suscetíveis a ruído**.

Em contrapartida: uma árvore **muito pequena** não usa toda a informação do treino e também erra mais (**underfitting**).

**Analogia.** Uma árvore sem limite é como um código com um `if` para cada caso de teste: acerta 100% dos testes que você viu e falha nos novos. Uma árvore minúscula é como `return "sempre a mesma resposta"`: simples demais.

**Exemplo nosso.** Num conjunto de 10 linhas, uma árvore sem limites cresce até que cada folha seja pura: acerta 100% do treino (verifiquei: acurácia de treino 1,0). Mas, se alguns rótulos tiverem ruído, as folhas finais estarão explicando o ruído, e os dados novos vão discordar.

### 14.2 Como se evita (slide 35)

O slide 35: costuma-se definir um **número mínimo de amostras para cada novo nó** ou um **número máximo de nós folha**. Se o novo nó teria menos amostras que o mínimo, ou o máximo de folhas já foi atingido, o nó **não é criado**, e todas as amostras daquele ramo recebem o **mesmo resultado**. O objetivo: modelos **generalizáveis**, que mantenham bons resultados em outras bases.

Resumo: o ramo vira folha antes de ficar puro.

### 14.3 Pré-poda e pós-poda

O slide 35 descreve parar o crescimento (isso é a **pré-poda**, "poda durante a construção"). Os slides não usam as palavras pré-poda e pós-poda.

**[Complemento: fora dos slides]** Existe também a **pós-poda**: deixar a árvore crescer inteira e depois remover ramos. O scikit-learn faz isso com o parâmetro `ccp_alpha` (poda por custo-complexidade): ela busca a subárvore que minimiza a impureza mais α vezes o número de folhas, e normalmente se escolhe o α comparando o desempenho em dados de validação. Não está nos slides; a prova do curso provavelmente só cobra os parâmetros da seção seguinte.

---

## 15. Parâmetros no scikit-learn (slides 36 e 37)

### 15.1 Parâmetros de poda (slide 36)

| Parâmetro | Significado | Efeito para combater overfitting |
| :-- | :-- | :-- |
| `max_depth` | profundidade máxima | **diminuir** simplifica a árvore |
| `min_samples_split` | mínimo de amostras para dividir um nó | **aumentar** simplifica |
| `min_samples_leaf` | mínimo de amostras em cada folha | **aumentar** simplifica |
| `max_leaf_nodes` | máximo de folhas | **diminuir** simplifica |
| `min_impurity_decrease` | mínimo de redução de impureza para aceitar o corte | **aumentar** simplifica |

Regra de bolso: valores de "máximo" menores e valores de "mínimo" maiores = árvore mais simples (menos overfitting, mais risco de underfitting).

### 15.2 Parâmetros do processo de split (slide 37)

O slide 37 é uma tabela que separa o que cada parâmetro controla **dentro do processo de dividir**:

| Parâmetro | O que controla no processo |
| :-- | :-- |
| `criterion`: `"gini"`, `"entropy"` ou `"squared_error"` | a fórmula do erro/impureza (Gini ou entropia na classificação; erro quadrático na regressão) |
| `splitter`: `"best"` ou `"random"` | se a busca pelo corte é **exaustiva** (best) ou **aleatória** (random) |
| `min_samples_split` | se o nó atual "tem permissão" de se dividir |
| `max_features` | quantas colunas o algoritmo "enxerga" em cada nó |

Para lembrar: `criterion` = **qual régua**; `splitter` = **como procura** (testa tudo ou sorteia); `min_samples_split` = **se pode dividir**; `max_features` = **quantas colunas olhar**. O `max_features` é o que o slide 31 chamou de "configuração de max_features" na varredura.

**Pegadinha:** `squared_error` é critério de **regressão**; para classificação use `gini` ou `entropy`. Os dois grupos de parâmetros (slides 36 e 37) repetem `min_samples_split` de propósito: ele é ao mesmo tempo critério de poda e controle do processo de split.

### 15.3 Código de verdade (exemplo nosso, executado)

Ordem correta de um fluxo com árvore: importar, separar treino e teste, criar o modelo com os parâmetros de poda, **treinar só no treino**, prever no teste, avaliar.

```python
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# dados do exemplo da praia: colunas sol e vento
X = np.array([[9,2],[8,3],[7,8],[9,7],[3,2],[2,6],[4,3],[8,1],[1,9],[6,2]])
y = np.array([1,1,0,0,0,0,0,1,0,1])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=0, stratify=y)

model = DecisionTreeClassifier(max_depth=2, min_samples_leaf=1, random_state=0)
model.fit(X_train, y_train)          # aprende SOMENTE com o treino
y_pred = model.predict(X_test)       # prevê no teste
print(accuracy_score(y_test, y_pred))

print(export_text(model, feature_names=["sol", "vento"]))
```

`export_text` imprime as regras da árvore como `if/else` (a "caixa branca" do slide 44). Com 10 exemplos o teste tem só 3 linhas, então o número é frágil; o exemplo serve para mostrar a **ordem das chamadas**.

**Erros de lógica típicos (o tipo de pegadinha de código da prova):**

```python
model.fit(X_test, y_test)                      # errado: treinou no conjunto de teste
model.predict(X_train)                         # avalia no treino e infla o resultado
X_scaled = StandardScaler().fit_transform(X)   # desnecessário para árvore (seção 19.1)
model.predict(X_test); model.fit(X_train, y_train)   # ordem invertida: prevê antes de treinar
```

---

## 16. A indução em pseudocódigo (slides 38 a 41)

Os slides 38 a 41 mostram o **algoritmo de indução da árvore de decisão** em pseudocódigo. No texto extraído, o pseudocódigo é **imagem**: não é possível conferir cada linha. O que o texto dos slides preserva:

- Slide 39 tem "ou", "ou": o pseudocódigo oferece alternativas (por exemplo, o critério de parada ou o tipo de teste).
- **Slide 41:** "**No sklearn, as divisões são apenas binárias.**" (cada nó gera exatamente duas saídas).

Como o slide 42 comenta o pseudocódigo linha por linha (as linhas 8, 9, 10 e 12), a leitura do pseudocódigo fica garantida pela tabela do slide 42.

Esqueleto geral do algoritmo (**exemplo nosso**, em português, só para você não ficar sem referência; não é a transcrição do slide):

```text
construir(dados):
    se os dados são todos da mesma classe: devolve uma folha com essa classe
    se acabaram os atributos ou algum critério de parada vale: devolve folha com a classe majoritária
    escolhe o melhor atributo/corte (ganho máximo ou Gini mínimo)
    para cada saída do teste:
        filho = construir(dados daquela saída)
    devolve o nó com o teste e os filhos
```

---

## 17. Pseudocódigo x scikit-learn (slide 42)

O slide 42 é uma tabela que compara os passos do pseudocódigo (o clássico, multivalorado) com **como o scikit-learn faz (CART)**. É matéria típica de prova. Reproduzo as quatro linhas:

| Passo no pseudocódigo | Como o sklearn faz |
| :-- | :-- |
| Linha 8: "Se atributo é discreto..." | **Trata tudo como numérico.** Se for uma categoria (0 ou 1), trata como escala e busca o corte em **0,5** |
| Linha 9: "Remove atributo da lista" | **Não remove.** No CART, um atributo pode ser usado várias vezes em níveis diferentes enquanto continuar ajudando a reduzir a impureza |
| Linha 10: "Para cada valor j..." | Testa **apenas duas direções**: valor ≤ limite e valor > limite |
| Linha 12: "Se Dj está vazio..." | **Evita nós vazios** por meio de `min_samples_leaf`: só divide se houver dados suficientes dos dois lados |

Exemplo (conferido): um atributo binário `b` com valores 0 e 1, alvo igual a `b`:

```text
|--- b <= 0.50
|   |--- class: 0
|--- b >  0.50
|   |--- class: 1
```

O sklearn trata `b` como número e corta em 0,5.

**Contraste importante:** o pseudocódigo clássico (estilo ID3) cria **uma saída por valor** do atributo discreto e **remove** o atributo depois de usá-lo. O sklearn (CART) faz **testes binários** e **pode reusar** o atributo. A linha 9 e a linha 10 resumem isso.

> **Se perguntarem na prova:** sklearn = tudo numérico (binário corta em 0,5), não remove o atributo, só divide em ≤ e >, evita nó vazio com `min_samples_leaf`.

---

## 18. Reuso de atributos (slide 43)

O slide 43 responde: **um atributo pode ser usado de novo no mesmo ramo?**

| Tipo de atributo | Pode reusar no mesmo ramo? | Motivo (do slide) |
| :-- | :-- | :-- |
| **Binário (0 ou 1)** | **Não** | A primeira divisão **já esgota** toda a informação (limpa a impureza) |
| **Numérico (contínuo)** | **Sim** | Podem existir **múltiplos cortes** que refinam a decisão |
| **Categórico (multivalor)** | **Sim** | No sklearn (binário) é preciso várias perguntas sim/não para isolar cada categoria |

**Por que o binário não repete.** Depois de perguntar "b ≤ 0,5?", cada lado só tem b = 0 ou só tem b = 1. Perguntar de novo geraria um filho vazio, sem valor.

**Exemplo do slide (figura):** os rótulos jovem/adulto/idoso e os testes `Idade ≤ 60` e `Idade ≤ 20` mostram uma categoria de 3 valores isolada com duas perguntas binárias sobre o mesmo atributo (primeiro uma, depois a outra mais abaixo). Isso também ilustra o reuso do numérico: a `Idade` aparece duas vezes, com cortes diferentes. Na seção 4, o `ABDOMINAL` fez o mesmo (50 e 38).

> **Se perguntarem na prova:** binário não reusa (a 1ª divisão esgota); numérico reusa (cortes refinados); categórico reusa (várias perguntas sim/não).

---

## 19. Vantagens (slide 44)

O slide 44 lista as vantagens. Cada uma com seu comentário:

1. **Ignora variáveis redundantes e seleciona só as características relevantes.** Colunas inúteis simplesmente não são escolhidas como divisor.
2. **Funciona imediatamente, sem hiperparâmetros complexos para corrigir e ajustar.** (Na prática, há os parâmetros de poda da seção 15; mas o modelo roda com os valores padrão.)
3. **Interpretável:** o processo de previsão é um conjunto de regras recursivas organizadas em ramos e folhas. Veja `export_text`.
4. **Pouco esforço de preparação dos dados:** métodos baseados em árvores **normalmente não requerem normalização**. Além disso, o slide diz que "conseguem lidar com valores faltantes, categóricos e numéricos".
5. **Complexidade logarítmica na etapa de predição.**
6. **Capazes de lidar com problemas com múltiplos rótulos.**

### 19.1 Sobre "sem normalização"

O algoritmo só compara **ordens** dos valores (a pergunta é "atributo ≤ corte?"). Multiplicar uma coluna por 1000 não muda a árvore, só o número escrito na regra. Conferido: com `vento` e `sol` multiplicados por 1000, a regra passou a ser `vento ≤ 4500`, com a mesma estrutura. Daí: normalizar ou padronizar **não é necessário** (ao contrário de k-NN e regressão com regularização).

### 19.2 A tensão: categóricos e faltantes

Aqui há duas versões que parecem contradizer-se:

| Fonte | O que diz |
| :-- | :-- |
| Slide 44 | árvores "conseguem lidar com valores faltantes, categóricos e numéricos" (afirmação sobre métodos de árvore em geral) |
| Slide 42 | o sklearn "trata tudo como numérico" |

Como conciliar:

- Em teoria (algoritmos como ID3/C4.5 e o conceito de árvore), a árvore pode ter testes sobre categorias e regras para dados faltantes. É a versão do slide 44.
- No sklearn, os atributos precisam ser **números**. Conferido: `fit([["a"],["b"]], [0,1])` dá erro "could not convert string to float". Então, para usar categorias, é preciso **codificá-las** (por exemplo, one-hot) antes.
- Sobre faltantes: o `DecisionTreeClassifier` das versões recentes aceita NaN (conferi na versão 1.5.1, instalada aqui), mas versões antigas não aceitavam; não dependa disso sem checar a versão. **[Complemento: fora dos slides]**

**Se perguntarem na prova:** se a afirmação for "árvores de decisão lidam com valores faltantes, categóricos e numéricos", marque como **vantagem** (slide 44). Se a questão for sobre o **scikit-learn**, lembre do slide 42: tudo é tratado como numérico, categorias são tratadas como escala.

### 19.3 Sobre "complexidade logarítmica"

Prever é percorrer um caminho da **raiz até uma folha**: o custo é proporcional à **profundidade** (número de perguntas). Em uma árvore razoavelmente **balanceada**, a profundidade cresce como log₂(n), e daí vem a "complexidade logarítmica" do slide. **Não é garantido**: uma árvore muito desbalanceada tem profundidade maior (no pior caso, ≈ n). Para a prova, repita o slide ("logarítmica na predição").

### 19.4 Sobre "múltiplos rótulos"

Um problema de **múltiplos rótulos/saídas** é aquele em que cada exemplo tem **mais de uma resposta** ao mesmo tempo (por exemplo, "contém gato" e "contém cachorro" na mesma foto). Árvores suportam isso. Conferido: `DecisionTreeClassifier().fit(X, Y)` com `Y` de duas colunas devolve `predict` com duas colunas.

Diferente de **multiclasse** (uma única resposta entre várias opções). Cuidado ao ler "múltiplos rótulos" e "multiclasse" na prova: não são o mesmo.

### 19.5 Complemento sobre outliers

**[Complemento: fora dos slides]** Como a árvore só compara ordens, um valor extremo em um **atributo** costuma incomodar menos do que em modelos que usam distâncias ou coeficientes. Já um valor extremo no **alvo** (em regressão) puxa a média da folha. O slide 44 não afirma robustez a outliers.

---

## 20. Desvantagens (slide 45)

O slide 45 lista:

1. **Overfitting:** uma árvore crescida até sua profundidade máxima pode **decorar** o conjunto de treino ("o temido overfitting").
2. **Mitigação:** "podar", **atribuindo uma profundidade máxima ou uma quantidade máxima de folhas** (as opções do slide 35/36).
3. **Instabilidade (alta variância):** pequenas variações nos dados de treino podem resultar em **árvores completamente distintas**.

**Variância, em uma frase:** mudar um pouco os dados muda muito o modelo. Analogia: um compilador cuja saída muda completamente por uma alteração de um caractere no código-fonte.

Por que acontece: o primeiro corte é escolhido pelo melhor Gini/ganho; se dois atributos estão quase empatados, uma pequena mudança nos dados troca o vencedor, e tudo que vem abaixo muda.

**[Complemento: fora dos slides]**

- Cortes são paralelos aos eixos (consequência da seção 7): fronteiras diagonais ou curvas viram "escadinha".
- Em regressão, a árvore prevê degraus e **não extrapola**: fora do intervalo visto no treino, repete o valor da última folha. Conferido: treinada com A = 1, 2, 3, 4 e y = 2, 4, 6, 8, a árvore prevê **8** para A = 10 e para A = 100. Uma regressão linear daria 20 e 200.
- Instabilidade é o que motiva métodos de comitê (por exemplo, florestas de árvores), assunto de outra aula.

---

## 21. Exercício (slides 46 e 47)

Os slides 46 e 47 trazem um **exercício**. O slide 46 é uma imagem (enunciado não extraído). O slide 47 dá o **link do dataset** no Kaggle: "biomechanical features of orthopedic patients" (características biomecânicas de pacientes ortopédicos).

O que se pode afirmar com segurança: é um exercício prático de aplicar árvore de decisão a esse conjunto. Como o enunciado exato está em imagem, não afirmo o que se pede. Se for refazer em casa, o fluxo é o da seção 15.3: carregar os dados, separar treino e teste, criar `DecisionTreeClassifier`, treinar, avaliar e inspecionar as regras com `export_text`. O plano é **exemplo nosso**.

---

## 22. Armadilhas e resumo de prova

| # | Armadilha / ponto de prova | Resposta |
| :-- | :-- | :-- |
| 1 | Escolha do divisor | **maior ganho** de informação, ou **menor Gini** ponderado |
| 2 | Escala dos dados | árvore **não precisa** de normalização/padronização; `StandardScaler` é desnecessário |
| 3 | Regressão | a folha prevê a **média**; o corte de menor custo (MSE) é escolhido |
| 4 | Reuso | numérico e categórico reusam; binário não |
| 5 | Divisões no sklearn | **binárias** (≤ e >); categoria/binário vira número e corta em 0,5 |
| 6 | Overfitting | mais `max_depth` = mais complexo; mais `min_samples_split`/`min_samples_leaf` = mais simples |
| 7 | Faixa do Gini e da entropia | [0, 0,5] e [0, 1] só valem para **2 classes** |
| 8 | Entropia x Gini | Gini mais rápido; entropia "um pouco melhor" (versão do slide) |
| 9 | Regiões das folhas | disjuntas e cobrem tudo; a árvore prevê para qualquer entrada |
| 10 | Corte numérico | slide: todos os valores únicos; sklearn: ponto médio entre vizinhos |
| 11 | Complexidade da predição | logarítmica (slide), proporcional à profundidade |
| 12 | Ordem do código | importar, separar, criar, `fit` no treino, `predict` no teste, avaliar |
| 13 | Parâmetros do split | `criterion` (régua), `splitter` (busca), `min_samples_split` (pode dividir), `max_features` (quantas colunas) |
| 14 | Datas | ID3 1979, C4.5/C5.0 1993, CART 1984 |

**Fórmulas em uma linha (para memorizar):**

```text
Entropia   H = −Σ pᵢ · log₂(pᵢ)
Ganho      = H(pai) − Σ (|S_v| / |S|) × H(S_v)
Gini       = 1 − Σ pᵢ²
Gini_split = (n_E / n) × Gini(E) + (n_D / n) × Gini(D)
```

**Pré-prova rápida:** feche o texto e responda em voz alta. (1) Como o algoritmo escolhe o divisor? (2) O que significa "guloso"? (3) Por que binário não repete e numérico repete? (4) O que cada um dos quatro parâmetros do slide 37 controla? (5) Qual a diferença entre o pseudocódigo clássico e o sklearn?
