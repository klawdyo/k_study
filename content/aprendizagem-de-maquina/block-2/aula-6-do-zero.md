# Aula 6 do zero: k-NN (k vizinhos mais próximos)

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e um exemplo concreto, depois com o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção) e cobre os 34 slides. Os slides 7, 9, 10, 14, 15 e 27 são só imagem (o texto extraído mostra apenas "[IMAGEM]"); eles são tratados pelo assunto da seção em que aparecem, sem eu ter visto as figuras. Onde o texto traz algo que **não está no slide**, está marcado como "exemplo nosso" ou "fora dos slides".

**A pergunta que a aula inteira responde:** *para classificar algo novo, basta olhar para os exemplos mais parecidos que eu já conheço e copiar o que a maioria deles diz?*

Analogia de software: é um `SELECT ... ORDER BY distancia LIMIT k` seguido de um `GROUP BY classe` com `COUNT`. Não existe fórmula treinada: existe uma **busca por semelhança** feita na hora.

---

## 1. Visão geral e origem (slides 1 a 3)

Os slides 1 e 2 são capa e título ("Algoritmo KNN"). O slide 3 diz:

- O **KNN** (do inglês *K-Nearest Neighbors*, K vizinhos mais próximos) foi proposto por **Fukunaga e Narendra em 1975**.
- É um dos classificadores **mais simples de implementar**, de **fácil compreensão**, e **ainda hoje pode obter bons resultados**, dependendo da aplicação.

Observe a frase "dependendo da aplicação": o slide não promete que o k-NN é sempre bom. As seções 7 e 10 mostram quando ele falha.

Convenção de grafia: a professora escreve **KNN**; neste texto uso "k-NN". É a mesma coisa. No código do scikit-learn a classe é `KNeighborsClassifier` (classificação) e `KNeighborsRegressor` (regressão).

> **Se perguntarem na prova:** autoria e ano (Fukunaga e Narendra, 1975); simples, fácil de entender, bons resultados dependendo da aplicação.

---

## 2. Características do k-NN (slides 4 e 5)

O slide 4 lista quatro características; o slide 5 acrescenta uma quinta e uma observação sobre treino e teste. Vamos uma por uma.

| Característica (slide) | O que significa | Analogia de software |
| :-- | :-- | :-- |
| **Algoritmo supervisionado** (4) | Aprende a partir de exemplos que já têm a resposta (rótulo ou valor alvo) | Uma tabela de histórico com a coluna "resultado correto" preenchida |
| **Classificação e regressão** (4) | Serve para prever uma **categoria** (classe) ou um **número** | Função que devolve uma enum ou um float |
| **Não paramétrico** (4) | Não faz exigências a respeito da distribuição dos rótulos; não ajusta um número fixo de coeficientes | Não existe uma "fórmula com 3 constantes" no final; o próprio conjunto de dados é o modelo |
| **Baseado em instâncias** (4) | Guarda os **exemplos** e os consulta; não resume tudo em uma equação | Cache de consultas em vez de um algoritmo fechado |
| **Preguiçoso (lazy)** (5) | **Não tem fase de treinamento e não produz um modelo** | Carga lazy: nada é calculado até alguém pedir |

Explicando os termos que a professora usa sem definir:

- **Rótulo (label)**: a resposta conhecida de cada exemplo (a classe "aprovado" ou o valor 7,5).
- **Distribuição dos rótulos**: o "formato" estatístico dos valores (por exemplo, em forma de sino, a famosa curva normal). Dizer que o k-NN é **não paramétrico** é dizer que ele **não assume** esse formato. Um modelo **paramétrico**, como a regressão linear da Aula 5, assume uma forma fixa (uma reta) e aprende só os parâmetros dela (α e β).
- **Preguiçoso**: o trabalho pesado fica para a hora da **predição**, não para a hora do "treino". O "treino" do k-NN é só guardar a tabela em memória.

### Por que dividir em treino e teste se não há treinamento? (slide 5)

O slide 5 afirma que **é necessário dividir o conjunto em treino mesmo sendo lazy**. Motivo dado: a divisão é **crucial para avaliar a capacidade de generalização** e **evitar o sobreajuste (overfitting)**. E acrescenta: testar com os **mesmos dados de treino resultaria em 100% de acerto (para K=1)**.

Por que 100%? Com K=1, o vizinho mais próximo de qualquer ponto **que já está na tabela** é ele mesmo (distância zero), e ele devolve o próprio rótulo. É como testar uma função de busca perguntando a ela justamente as chaves que você acabou de inserir.

Nota (exemplo nosso): o "100%" tem uma exceção. Se a base tiver dois pontos **idênticos** com rótulos **diferentes**, o k-NN com K=1 pode escolher o rótulo errado. Na prova, vale o slide: K=1 avaliado no treino dá 100%.

Trecho executado (exemplo nosso, base de vinhos do scikit-learn, K=1, avaliado no próprio treino):

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split

X, y = load_wine(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y)

knn = KNeighborsClassifier(n_neighbors=1).fit(X_train, y_train)
print(knn.score(X_train, y_train))   # saída: 1.0  (100% no treino, sem valor nenhum)
```

> **Se perguntarem na prova:** o k-NN é supervisionado, serve para classificação e regressão, é não paramétrico, baseado em instâncias e lazy (sem fase de treinamento, não produz modelo). Mesmo assim se divide em treino e teste, para medir generalização; K=1 testado no treino dá 100%.

---

## 3. A ideia principal (slides 6 e 7)

O slide 6 diz que a ideia principal é determinar o **rótulo de uma amostra** com base nas **amostras vizinhas** do conjunto de treinamento. O algoritmo **assume que coisas semelhantes existem nas proximidades**; em outras palavras, **coisas semelhantes estão próximas umas das outras**. O slide 7 é só uma figura.

Para "estar próximo" fazer sentido, cada exemplo precisa virar um **ponto num espaço**:

- Cada **atributo (feature)** é um eixo. Um cliente com idade e renda vira um ponto de 2 dimensões; com 13 atributos, vira um ponto de 13 dimensões.
- **Distância** entre dois pontos é a medida de quão parecidos os dois exemplos são. Pequena distância = muito parecidos.

Intuição de software: a tabela de clientes com colunas `idade`, `renda`, `risco`. Chega um cliente novo sem a coluna `risco`. Em vez de aplicar uma fórmula, o k-NN pergunta: "quais são os K clientes mais parecidos com ele? Qual risco a maioria deles tem?" e copia a resposta.

---

## 4. Exemplo do slide 8 e os dois pontos-chave

O slide 8 traz um exemplo: **problema de classificação com dois rótulos e K=7**. A variável K é a **quantidade de vizinhos mais próximos** usados para decidir a classe da nova amostra. Das sete amostras de treino mais próximas, **4 são do rótulo A e 3 do rótulo B**; como há mais vizinhos A, a nova amostra recebe **A**.

O mesmo slide fecha com a frase que organiza a aula inteira: **dois pontos-chave devem ser determinados para aplicar o k-NN: a métrica de distância e o valor de K**.

- **Métrica de distância**: como medir "perto" (slides 21 a 27, seção 11).
- **Valor de K**: quantos vizinhos votam (slides 12 a 15, seção 8).

---

## 5. Exemplo numérico completo (exemplo nosso)

Vamos fazer na mão o que o k-NN faz. Os dados abaixo são **inventados por mim** para ilustrar; não vêm dos slides. Cada exemplo tem 2 atributos (x1, x2) e uma classe (A ou B). Queremos classificar o ponto novo **q = (0, 0)**.

### Passo 1: calcular a distância de q até cada ponto

Distância euclidiana (a "linha reta", detalhada na seção 11): d = √((x1 − 0)² + (x2 − 0)²).

| Ponto | (x1, x2) | Classe | Conta | Distância |
| :-- | :-- | :-- | :-- | :-- |
| P1 | (1, 1) | B | √(1 + 1) = √2 | 1,414 |
| P2 | (2, 1) | A | √(4 + 1) = √5 | 2,236 |
| P3 | (2, 2) | A | √(4 + 4) = √8 | 2,828 |
| P4 | (3, 3) | B | √(9 + 9) = √18 | 4,243 |
| P5 | (4, 4) | B | √(16 + 16) = √32 | 5,657 |

### Passo 2: ordenar do mais perto ao mais longe e votar

A ordem já está crescente: P1, P2, P3, P4, P5. Com os rótulos na ordem: **B, A, A, B, B**.

| K | Vizinhos escolhidos | Votos | Classe prevista |
| :-- | :-- | :-- | :-- |
| 1 | P1 | B = 1 | **B** |
| 3 | P1, P2, P3 | A = 2, B = 1 | **A** |
| 5 | P1 a P5 (todos) | A = 2, B = 3 | **B** |

A **mesma amostra recebe classes diferentes** conforme o K: B com K=1, A com K=3, B com K=5. Isso mostra, em miniatura, por que escolher K é decisão importante (seção 8). Note também que K=5 é igual ao número total de pontos: é o caso extremo em que o modelo devolve sempre a classe majoritária da base (3 B contra 2 A), seja qual for o ponto q.

Para **regressão** (slide 4 diz que o k-NN também faz regressão), a previsão é a **média** dos valores dos K vizinhos. Se P1 a P5 tivessem os valores 10, 20, 30, 40, 50, com K=3 a previsão seria (10 + 20 + 30) / 3 = 20.

### Passo 3 (opcional): votar com peso pela distância

Veremos na seção 9 a variação ponderada. Para já deixar o exemplo pronto, com K=3 (vizinhos P1 B, P2 A, P3 A):

| Peso usado | Soma do peso de A | Soma do peso de B | Classe |
| :-- | :-- | :-- | :-- |
| Sem peso (um voto cada) | 2 | 1 | A |
| 1/d (o que o scikit-learn faz com `weights='distance'`) | 1/2,236 + 1/2,828 = 0,447 + 0,354 = 0,801 | 1/1,414 = 0,707 | A |
| 1/d² (o que o slide 16 descreve) | 1/5 + 1/8 = 0,325 | 1/2 = 0,500 | **B** |

Os três métodos podem discordar. É exatamente a divergência que a seção 9 explica.

### O mesmo cálculo em Python (exemplo nosso, executado)

```python
import numpy as np
from collections import Counter

X = np.array([[1, 1], [2, 1], [2, 2], [3, 3], [4, 4]])
y = np.array(list("BAABB"))
q = np.array([0, 0])

dist = np.sqrt(((X - q) ** 2).sum(axis=1))   # distância de q a cada linha
print(dist.round(3))                          # [1.414 2.236 2.828 4.243 5.657]

for k in (1, 3, 5):
    vizinhos = np.argsort(dist)[:k]           # índices dos k menores
    print(k, Counter(y[vizinhos]).most_common(1)[0][0])
# saída: 1 B / 3 A / 5 B
```

É o pseudocódigo do slide 10 (que é imagem; ver seção 6). Quatro linhas: calcular distâncias, ordenar, pegar K, contar votos.

---

## 6. Pseudocódigo do k-NN (slides 9 e 10)

Os slides 9 e 10 são imagens (o 10 é intitulado "Pseudocódigo do KNN"). O algoritmo padrão, que o exemplo acima já percorreu, é:

1. Receber o ponto novo.
2. **Calcular a distância** do ponto novo até **todos** os exemplos de treino.
3. **Ordenar** as distâncias em ordem crescente.
4. Pegar os **K** exemplos mais próximos.
5. **Classificação:** contar os votos por classe e devolver a mais votada. **Regressão:** devolver a média dos valores.

Dedução importante, que reaparece nas desvantagens: no passo 2 o algoritmo percorre **a base de treino inteira para cada predição**. Logo a "carga" (treino) é rápida e a **predição é cara**.

---

## 7. A maldição da dimensionalidade (slide 11)

O slide 11 (com uma figura) afirma: **em alta dimensão, todos os pontos parecem estar "longe" uns dos outros na mesma proporção**. Consequência dada: o k-NN **perde a capacidade de distinguir quem é realmente um vizinho próximo**, e as predições passam a ser baseadas em **ruído**.

Entendendo do zero:

- **Dimensão** = número de atributos. Muitos atributos = alta dimensão.
- Cada atributo novo é um eixo novo, e o espaço cresce muito rápido. Os pontos ficam espalhados num espaço enorme, quase sem vizinhos de fato "colados".
- Analogia de software: se você compara dois registros por 500 campos e a maioria difere em algum campo, nenhum par parece "quase igual". A noção de "mais parecido" perde o sentido porque o mais parecido e o menos parecido têm distâncias quase iguais.

Esse efeito chama-se **maldição da dimensionalidade (curse of dimensionality)**. O slide 22 repete que a distância Euclidiana "sofre muito" com ela, e o slide 19 a cita como desvantagem.

O que fazer (fora dos slides): reduzir o número de atributos, seja escolhendo só os relevantes (**seleção de atributos**), seja comprimindo-os com técnicas como a PCA (**redução de dimensionalidade**, assunto de outra aula). A seção 10 retoma isto.

> **Se perguntarem na prova:** alta dimensão faz as distâncias parecerem todas iguais; o k-NN perde o poder de discriminar vizinhos e prevê com base em ruído.

---

## 8. Como escolher o K (slides 12 a 15)

### O que o slide 12 diz

- **Não existe um valor único** de K; ele **varia de acordo com a base de dados**.
- **É recomendável sempre utilizar valores ímpares.**
- Pode-se usar um **algoritmo de otimização** para achar o melhor K, mas isso pode **deixar o desempenho geral do modelo bem lento** na etapa de seleção.
- Outra maneira é **testar um conjunto de valores** e achar o K **empiricamente** (na prática, por tentativa).

Por que ímpar? Em duas classes, com K par pode haver empate (3 votos A e 3 votos B com K=6). Com K ímpar não há empate. Observação (fora dos slides): isso só garante a ausência de empate com **duas** classes. Com três classes e K=3, o resultado 1-1-1 ainda é empate. O slide diz "sempre ímpares"; na prova, responda o que o slide diz e use o raciocínio de "evitar empates".

"Testar empiricamente" na prática é a **validação cruzada** (assunto da Aula 4): treinar e avaliar com vários K e ficar com o que teve melhor nota média. Vamos ver o código logo abaixo (exemplo nosso).

### A tabela do slide 13

O slide 13 organiza os efeitos de K muito grande e muito pequeno. Reproduzo cada item:

| | K muito pequeno | K muito grande |
| :-- | :-- | :-- |
| Quem entra na votação | **Apenas os objetos muito parecidos** são considerados | **Vizinhos podem ser muito diferentes** do ponto novo |
| Estabilidade | **Predição pode ser instável** | A predição é **tendenciosa para a classe majoritária** |
| Outliers | **Sensível a outliers** | **Mais resistente a outliers** |
| Risco | Pode gerar **overfitting** | Suavização excessiva, pode gerar **underfitting** |

E o slide também repete a recomendação: **K igual a número ímpar, para evitar empates**.

Explicando os termos:

- **Outlier**: ponto fora do padrão (um cliente com renda absurda, um erro de digitação). Com K=1, um único outlier no treino cria uma "ilha" de classe errada ao redor dele. Com K grande, esse ponto é só um voto entre muitos e é diluído; por isso o slide diz que K grande é **mais resistente a outliers**.
- **Overfitting (sobreajuste)**: o modelo "decora" o treino, inclusive o ruído, e erra em dados novos. Analogia: um código com um `if` para cada caso de teste.
- **Underfitting (subajuste)**: o modelo é simples demais e não capta o padrão. Analogia: uma função que devolve sempre a média.
- **Fronteira de decisão (decision boundary)**: a "linha" (ou superfície) no espaço onde a classe prevista muda de A para B. Com K pequeno ela é recortada e irregular; com K grande, suave e simples.
- **Classe majoritária**: a classe com mais exemplos na base. Com K enorme, ela tende a vencer sempre, porque a maioria dos votos vem dela. No limite, K igual ao tamanho do treino, com votos uniformes, prevê sempre a classe majoritária (isso foi o que vimos em K=5 no exemplo numérico da seção 5).

Cuidado com a armadilha de leitura: "K grande ignora detalhes" **não** significa "K grande é pior para outliers". O slide diz o contrário: K grande é mais resistente a outliers, e seu defeito é a suavização excessiva e o viés para a classe majoritária.

Os slides 14 e 15 são só figuras ("Como escolhemos o K?"), em geral gráficos que comparam a fronteira de decisão e/ou o erro para vários K. Como não pude conferi-los, não afirmo o que mostram. Para a prova, o que vale é a tabela do slide 13.

### Escolhendo K por validação cruzada (exemplo nosso, executado)

Aqui já uso um **Pipeline** com padronização dentro (explicado na seção 12), para a validação cruzada não vazar informação.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

for k in (1, 3, 5, 7, 9, 11, 15, 21):
    modelo = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    nota = cross_val_score(modelo, X_train, y_train, cv=5).mean()
    print(k, round(nota, 3))
# saída com a base de vinhos: 1:0.951  3:0.951  5:0.959  7:0.959
#                             9:0.943  11:0.959  15:0.967  21:0.959
```

Leitura: não há um K "mágico". As notas variam pouco entre 5 e 21; o melhor aqui foi K=15 (0,967), mas a diferença é pequena. É o que o slide 12 diz: o K depende dos dados e se acha **testando**.

Para testar K e outras opções ao mesmo tempo existe a busca em grade (`GridSearchCV`), que roda a validação cruzada para cada combinação:

```python
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

pipe = Pipeline([("scaler", StandardScaler()),
                 ("knn", KNeighborsClassifier())])
grade = {"knn__n_neighbors": [1, 3, 5, 7, 9, 11, 15, 21],
         "knn__weights": ["uniform", "distance"]}
busca = GridSearchCV(pipe, grade, cv=5).fit(X_train, y_train)
print(busca.best_params_)   # {'knn__n_neighbors': 15, 'knn__weights': 'uniform'}
print(busca.score(X_test, y_test))   # 0.981 no teste, que não participou da escolha
```

Dois detalhes que a prova gosta de cobrar: (1) o **teste final** só é usado **uma vez**, depois de escolher K; (2) o nome do parâmetro dentro do Pipeline leva o prefixo do passo (`knn__n_neighbors`).

> **Se perguntarem na prova:** K depende dos dados; recomenda-se ímpar para evitar empate; K pequeno: sensível a outliers, instável, overfitting; K grande: mais resistente a outliers, mas viés para a classe majoritária e suavização excessiva (underfitting); acha-se K de forma empírica (testando valores) ou por otimização, que deixa a seleção lenta.

---

## 9. Variação: k-NN com distância ponderada (slide 16)

No k-NN comum (**votação uniforme**), todo vizinho vale um voto. O vizinho colado e o vizinho no limite do raio de K têm o mesmo peso.

O slide 16 propõe a variação **KNN com distância ponderada**: **ponderar a contribuição de cada um dos K vizinhos de acordo com sua distância** até o ponto que queremos classificar (o slide chama de xj), dando **maior peso aos vizinhos mais próximos**. A fórmula do slide: podemos ponderar o voto de cada vizinho de acordo com o **quadrado do inverso de sua distância**. Em fórmula (o slide traz como figura; a escrita abaixo é a tradução da frase):

```
peso_i = 1 / d_i²        (slide 16: quadrado do inverso da distância)
voto da classe c = soma de peso_i dos vizinhos i que pertencem a c
classe prevista  = a classe com maior soma
```

(O "quadrado do inverso" de d é (1/d)², que é igual a 1/d².)

Para regressão, a média fica ponderada: previsão = Σ(peso_i × valor_i) / Σ(peso_i).

### Divergência: slide 16 (1/d²) versus scikit-learn (1/d)

- **Slide 16:** peso = **1/d²** (quadrado do inverso).
- **scikit-learn, `weights='distance'`:** a documentação define o peso como o **inverso da distância**, ou seja, **1/d**, não 1/d².
- Para obter 1/d² no scikit-learn é preciso passar uma **função** (callable) em `weights`, como na linha abaixo.

O slide 34 diz: "Distance já atribui pesos maiores para os vizinhos mais próximos", sem dizer a fórmula exata.

Em cada caso o resultado pode mudar, como mostrou a tabela do passo 3 da seção 5 (K=3: sem peso e com 1/d dão A, e com 1/d² dá B). Código executado:

```python
# peso 1/d² via função (callable): recebe o array de distâncias
knn = KNeighborsClassifier(n_neighbors=3, weights=lambda d: 1 / d ** 2)
knn.fit(X, y)
print(knn.predict([[0, 0]]))        # ['B']   (1/d²)
print(KNeighborsClassifier(n_neighbors=3, weights='distance')
      .fit(X, y).predict([[0, 0]])) # ['A']   (1/d)
```

Detalhe fora dos slides: se o ponto novo coincide exatamente com um de treino (distância 0), 1/d seria uma divisão por zero. O scikit-learn trata isso dando o voto todo ao vizinho de distância zero; no seu `lambda` próprio, você teria de tratar o caso.

> **Se perguntarem na prova:** a variação ponderada dá mais peso aos vizinhos mais próximos. Se a questão cita a fórmula do slide, é **1/d²** (quadrado do inverso da distância). Se a questão fala do parâmetro do scikit-learn, `weights='distance'` usa 1/d. Se houver conflito direto na alternativa, responda o que a professora ensinou (1/d²) e mencione que a biblioteca usa 1/d, se a prova permitir justificar.

---

## 10. Vantagens e desvantagens do k-NN (slides 17 a 20)

São quatro slides de afirmações que caem muito em prova. Vou transformar cada frase em uma explicação, na ordem dos slides.

### Vantagens (slides 17 e 18)

| Vantagem (slide) | Por que é verdade | Analogia de software |
| :-- | :-- | :-- |
| **Extremamente fácil de implementar** (17) | Calcular distância, ordenar, contar votos: poucas linhas (veja o código da seção 5) | Menos de 10 linhas, sem biblioteca de otimização |
| **Lazy: não requer treinamento antes de prever** (17) | Não existe fase de ajuste de parâmetros; os dados são o modelo | Sem etapa de build |
| **Inserção de novos dados instantânea** (17) | Basta acrescentar a linha na base; não é necessário treinar de novo | `INSERT` na tabela e já vale; um modelo comum precisaria ser retreinado |
| **Apenas dois parâmetros: K e a função de distância** (17) | Exemplos de distância no slide: Euclidiana, Manhattan | Só duas configurações para ajustar |
| **Aplicável em problemas complexos** (18) | Como não assume formato (não paramétrico), consegue fronteiras curvas e irregulares | Não força os dados a caberem numa reta |
| **Fácil de entender** (18) | "Parece com quem?" é uma lógica que qualquer pessoa entende e explica | Regra de negócio que o cliente consegue ler |
| **Nenhuma suposição sobre os dados** (18) | É a característica de não paramétrico (slide 4) | |
| **Classificação e regressão** (18) | Votação para classes, média para números | |
| **Funciona facilmente em problemas multiclasse** (18) | Com 2, 5 ou 20 classes, o algoritmo é o mesmo: vota-se entre todas | Basta o `Counter` ter mais chaves |
| **Pode ser paralelizado** (18) | A distância do ponto novo a cada exemplo é uma conta independente; dá para dividir os exemplos entre processadores | `map` seguido de `reduce`; cada distância não depende da outra |

Observações:

- "Apenas dois parâmetros" refere-se a K e à função de distância. No scikit-learn existem outros hiperparâmetros (weights, algorithm, leaf_size...), vistos na seção 14, mas a ideia do slide é que o **algoritmo básico** exige só esses dois.
- "Paralelizar" aparece no parâmetro `n_jobs` do scikit-learn (fora dos slides): `KNeighborsClassifier(n_jobs=-1)` usa todos os núcleos.
- "Inserção instantânea" é o outro lado da moeda do "lazy": não há treino, então não há retreino. O custo vai para a predição.

### Desvantagens (slides 19 e 20)

| Desvantagem (slide) | Por que acontece |
| :-- | :-- |
| **Não funciona bem com dados de dimensão elevada** (19) | Com muitos atributos, fica difícil aprender com a distância de cada dimensão (maldição da dimensionalidade, seção 7) |
| **Alto custo de previsão para grandes conjuntos** (19) | Para cada previsão, compara-se o ponto novo com todo o treino (seção 6) |
| **Baixa performance com variáveis categóricas explicativas** (19) | Distância entre categorias não é natural; "azul" não está a 2 unidades de "verde". Mesmo codificando (por exemplo, one-hot) a distância fica pouco informativa. Ver Hamming, seção 11 |
| **Sensível à escolha do K** (19) | Seção 8: K pequeno sobreajusta, K grande suaviza demais |
| **Não tem modelo explícito** (20) | Não há equação nem coeficientes para inspecionar; o "modelo" é a base inteira, o que dificulta explicar uma regra geral |
| **Custoso por comparar a nova amostra a cada exemplo do treino** (20) | É o mesmo ponto do custo de previsão, visto pelo lado da comparação exaustiva |
| **Afetado por variáveis irrelevantes ou redundantes** (20) | Cada atributo entra na distância com o mesmo direito de voto; um atributo inútil soma ruído à distância e esconde os que importam |
| **Sensível à escala dos dados** (20) | O atributo de maior magnitude domina a distância (seção 12) |
| **Escolher o melhor K pode ser difícil** (20) | Exige testar vários valores (seção 8) |

Dois pontos para fixar:

- **Variáveis categóricas:** o slide 19 diz "baixa performance". A prova pode trazer a afirmação "o k-NN lida naturalmente com variáveis categóricas"; está errada pelo slide.
- **Variáveis irrelevantes:** diferente de um modelo que aprende pesos e consegue "zerar" uma coluna inútil (como o Lasso da Aula 5), o k-NN trata todos os atributos como igualmente importantes na distância. Logo, ele precisa que você limpe os atributos antes.

> **Se perguntarem na prova:** vantagens: simples, lazy (sem treino), inserção instantânea, só dois parâmetros, sem suposições sobre os dados, classificação e regressão, multiclasse, paralelizável. Desvantagens: alta dimensão, custo de previsão alto, categóricas, sensível a K e à escala, sem modelo explícito, afetado por variáveis irrelevantes ou redundantes.

---

## 11. Métricas de distância (slides 21 a 27)

O slide 21 diz que **calcular a distância é fundamental** para o k-NN, que existem diversas métricas e que a escolha **varia de acordo com o problema**. Lista: **Euclidean, Hamming, Manhattan, Mahalanobis, Minkowski**.

**O que é uma "métrica de distância"?** Uma regra para transformar dois exemplos num número que diz quão diferentes são. Zero significa idênticos; quanto maior, mais diferentes. Imagine uma função `distancia(a, b)` que você pode trocar sem mexer no resto do algoritmo. Essa troca é uma das duas decisões do slide 8.

### Euclidiana (slide 22)

O slide diz: é **a mais utilizada** e representa a **distância mais curta** entre dois pontos. É **extremamente sensível à escala (exige padronização)** e **sofre muito com a maldição da dimensionalidade**. Fórmula (a figura do slide é imagem; esta é a fórmula padrão):

```
d(p, q) = √( Σ (p_i − q_i)² )      com i de 1 até n
```

É o teorema de Pitágoras estendido a n dimensões: a "linha reta" ("em linha reta", como um pássaro voa).

### Minkowski (slide 23)

O slide diz que é outro exemplo de distância, onde p = (p1, ..., pn) e q = (q1, ..., qn) são dois pontos n-dimensionais e **r é uma constante que deve ser escolhida**. A fórmula é uma figura. A forma padrão é:

```
d(p, q) = ( Σ |p_i − q_i|^r )^(1/r)
```

- Com **r = 1**, vira a distância de **Manhattan**.
- Com **r = 2**, vira a **Euclidiana**.
- Por isso o slide 33 a chama de **generalização** das duas.

Lembrete de grafia: o slide escreve "Minkowsky"; o correto é Minkowski.

### Manhattan (City Block, L1) (slide 24)

Soma das diferenças absolutas em cada atributo:

```
d(p, q) = Σ |p_i − q_i|
```

Analogia (fora dos slides): o caminho de um carro numa cidade em grade, andando só em horizontais e verticais, como em Manhattan. O slide 24 diz **quando usar**: **dados altamente dimensionais** ou quando se quer **reduzir a influência de outliers**; é **menos sensível a valores discrepantes** que a Euclidiana (porque não eleva a diferença ao quadrado, então um valor extremo pesa menos).

Conta comparativa (exemplo nosso): entre (0, 0) e (3, 4), a Euclidiana é √(9 + 16) = 5, e a Manhattan é 3 + 4 = 7.

### Hamming (slide 25)

O slide diz: a distância de Hamming calcula a distância entre dois **vetores binários**; **não mede "tamanho", mas sim diferença**; **conta em quantas posições os valores são diferentes**; é uma **boa opção para variáveis categóricas (one-hot)**.

O **one-hot** é uma codificação: a categoria vira um vetor de zeros com um único 1. Exemplo nosso: cores com a ordem (vermelho, verde, azul): vermelho = [1, 0, 0], verde = [0, 1, 0], azul = [0, 0, 1].

Exemplo nosso: [1, 0, 1, 1] e [1, 1, 1, 0] diferem na 2ª e na 4ª posição; distância de Hamming = **2** (conferido em Python). Detalhe: ao trocar de uma categoria one-hot para outra (vermelho para verde), mudam **duas** posições (a do 1 que some e a do 1 que aparece), então a distância é 2.

Cuidado: o slide 19 lista categóricas como desvantagem. Não há contradição: Hamming é **a melhor opção dentro** do k-NN para esse tipo de dado, mas continua sendo um ponto fraco do algoritmo.

### Mahalanobis (slide 26)

O slide: é a distância entre dois pontos no **espaço multivariado**; **usar quando as variáveis são correlacionadas**; se as variáveis **não são correlacionadas**, a Euclidiana dá o **mesmo resultado** que a Mahalanobis. A legenda do slide: **x** é o vetor da observação, **m** o vetor da média das variáveis independentes e **C** a covariância das variáveis independentes. Fórmula (figura no slide; esta é a forma padrão com a notação da legenda):

```
d(x) = √( (x − m)ᵀ · C⁻¹ · (x − m) )
```

Explicando:

- **Variáveis correlacionadas**: duas colunas que andam juntas (altura e peso, por exemplo). Se você as trata como independentes, está "contando duas vezes" a mesma informação.
- **Covariância**: medida de quanto duas variáveis variam juntas. A matriz C reúne isso para todos os pares de atributos.
- A Mahalanobis usa o inverso de C (C⁻¹) para **descontar** a redundância entre atributos e para considerar a escala de cada um. Quando as variáveis não têm correlação, C é diagonal e o efeito sobra só como escala, e a conta vira a Euclidiana (no caso exato de variâncias iguais a 1, ela coincide com a Euclidiana).

Observação de precisão: o slide define a distância entre uma observação x e a média m. Em k-NN, o uso é entre dois pontos x e y, trocando m por y; é a mesma ideia.

O slide 27 é só imagem.

### Resumo das métricas

| Métrica | Ideia | Quando o slide indica |
| :-- | :-- | :-- |
| Euclidiana | Linha reta, a mais usada | Padrão; exige padronização |
| Manhattan | Soma das diferenças absolutas | Muitas dimensões; reduzir efeito de outliers |
| Minkowski | Generaliza as duas (r=1 e r=2) | Quando se quer escolher o r |
| Hamming | Conta posições diferentes | Vetores binários, categóricas (one-hot) |
| Mahalanobis | Considera correlação entre variáveis | Variáveis correlacionadas |

> **Se perguntarem na prova:** Euclidiana = mais curta e mais usada, sensível à escala; Manhattan = menos sensível a outliers e boa para dimensão alta; Minkowski = generalização (r=1 Manhattan, r=2 Euclidiana); Hamming = diferença de posições em vetores binários, boa para categóricas (one-hot); Mahalanobis = variáveis correlacionadas, e vira Euclidiana se não houver correlação.

---

## 12. A escala dos atributos: padronize antes (slides 20 e 22)

Os slides 20 e 22 dizem que o k-NN é **sensível à escala dos dados** e que a Euclidiana **exige padronização**. Vamos ver por que, com um exemplo nosso.

Dois clientes comparados com o cliente 1 (idade em anos e renda em reais):

| Cliente | Idade | Renda mensal |
| :-- | :-- | :-- |
| 1 | 30 | 3000 |
| 2 | 40 | 3000 |
| 3 | 30 | 3500 |

- Distância de 1 a 2: só a idade muda (10 anos): √(10² + 0²) = **10**.
- Distância de 1 a 3: só a renda muda (500 reais): √(0² + 500²) = **500**.

O cliente 3 parece 50 vezes "mais distante", só porque a **renda tem números maiores**, não porque essa diferença seja mais importante. O atributo de maior escala **domina** a distância e a idade fica quase irrelevante (conferido em Python: 10,0 contra 500,0).

**Padronização** (também chamada de *z-score*): transformar cada atributo para ter **média 0 e desvio padrão 1**, por meio de (valor − média) / desvio padrão. Assim todos os atributos passam a ter a mesma ordem de grandeza. A alternativa é a **normalização min-max**, que reescala para o intervalo de 0 a 1. A professora usa a palavra "padronização" no slide 22.

Em scikit-learn, a ferramenta é o `StandardScaler`. A regra de ouro, que vira questão de "a ordem do código está certa?": **a média e o desvio devem ser calculados só com o treino** (`fit` no treino) e **depois aplicados** (`transform`) no teste. Se você calcular com a base inteira antes de dividir, o teste "vaza" informação para o treino (**vazamento de dados, data leakage**). A forma mais segura é colocar o scaler dentro de um **Pipeline**, que encadeia os passos e aplica a ordem certa sozinho.

Código executado (base de vinhos, 13 atributos de escalas bem diferentes, exemplo nosso):

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

# sem padronizar
puro = KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train)
print(puro.score(X_test, y_test))    # 0.722

# com padronização dentro do Pipeline
pipe = Pipeline([
    ("scaler", StandardScaler()),                 # 1º passo: padroniza
    ("knn", KNeighborsClassifier(n_neighbors=5)), # 2º passo: classifica
])
pipe.fit(X_train, y_train)    # o scaler aprende média/desvio só do treino
print(pipe.score(X_test, y_test))    # 0.944
```

A acurácia de teste foi de **0,722 para 0,944** apenas por padronizar. O Pipeline garante a ordem: `fit` do scaler no treino, `transform` no treino, `fit` do k-NN; na predição, `transform` do teste com a média e o desvio do treino, depois o `predict`.

Erros típicos que a prova pode mostrar em código:

1. Chamar `scaler.fit(X)` antes de `train_test_split` (vazamento).
2. Usar `scaler.fit_transform(X_test)` (o teste não deve ajustar o scaler).
3. Treinar o k-NN com `X_train` padronizado e depois prever com `X_test` **sem** padronizar (escalas diferentes).
4. Aplicar o k-NN em colunas de texto sem convertê-las em número (a distância exige números).

> **Se perguntarem na prova:** o k-NN é sensível à escala; a distância Euclidiana exige padronização; a padronização aprende os parâmetros só com o treino.

---

## 13. O k-NN em tarefas não supervisionadas (slides 28 e 29)

O slide 28: embora o k-NN seja famoso por ser **supervisionado**, a lógica de "vizinhos mais próximos" é muito poderosa também no mundo **não supervisionado**. Sem rótulos, o k-NN **deixa de prever uma categoria** e passa a **descrever a estrutura e o relacionamento entre os dados**.

O slide 29 dá três usos:

1. **Detecção de outliers (anomalias):** se um ponto está **muito longe de seus vizinhos mais próximos**, é um outlier. Algoritmo famoso: **LOF (Local Outlier Factor)**. Analogia: um registro de log completamente diferente dos 10 mais parecidos é suspeito.
2. **Imputação de dados faltantes (KNN Imputer):** em vez de preencher o valor ausente com a média da coluna toda, o algoritmo olha os **K registros mais parecidos** com o incompleto e usa os valores deles. Analogia: preencher o campo vazio copiando de clientes parecidos, em vez de usar a média global.
3. **Redução de dimensionalidade: t-SNE e UMAP:** usam vizinhos próximos para criar **mapas em 2D ou 3D** que **preservam a estrutura local** dos dados originais, facilitando a visualização de agrupamentos que ainda não conhecemos.

Tradução dos termos: **não supervisionado** é quando os dados não têm rótulo (não há "resposta certa" a copiar); **imputação** é preencher valores ausentes; **redução de dimensionalidade** é reduzir o número de atributos para poder, por exemplo, desenhar os dados num gráfico.

No scikit-learn (fora dos slides): `LocalOutlierFactor` e `KNNImputer`, ambos em módulos do scikit-learn; t-SNE (`sklearn.manifold.TSNE`); UMAP é uma biblioteca separada.

---

## 14. Hiperparâmetros do k-NN no scikit-learn (slides 30 a 34)

O slide 30 diz que as bibliotecas de Python e R têm um conjunto de **hiperparâmetros** ajustáveis e que é importante conhecê-los para **potencializar o desempenho** do k-NN.

**Hiperparâmetro** é uma configuração que você define **antes** do ajuste e que o algoritmo não aprende sozinho (K é um). Diferente de um **parâmetro**, que o modelo aprende dos dados (como o β da regressão linear). O k-NN quase não tem parâmetros aprendidos, e por isso o ajuste fica quase todo nos hiperparâmetros.

Resumo do que os slides 31 a 34 listam:

| Hiperparâmetro (slide) | O que faz | Valores citados |
| :-- | :-- | :-- |
| `n_neighbors` (31; o slide escreve "N-neighbourd") | Número de vizinhos considerados (o K) | Padrão do scikit-learn: 5 (fora dos slides) |
| `algorithm` (31, 32) | Como procurar os vizinhos | `'auto'`, `'ball_tree'`, `'kd_tree'`, `'brute'` |
| `p` (33) | Escolhe a potência da distância | `p=1` Manhattan; `p=2` Euclidiana |
| `metric` (34) | Tipo de distância | Padrão: `minkowski` |
| `weights` (34) | Peso dos vizinhos | `'uniform'`, `'distance'` ou uma função (`callable`) |

### algorithm (slides 31 e 32)

O slide 31 afirma:

- A opção **'auto'** deixa a cargo do algoritmo escolher a técnica mais adequada ao problema, **olhando para o resultado obtido nas observações anteriores** (assim está no slide).
- **'ball_tree'** é aconselhável para problemas com **grande número de dimensões**, diferente do 'kd_tree'; em contrapartida, o **custo computacional é maior**.

O slide 32 afirma:

- A vantagem do **'kd_tree'** é sobre o **'brute'** em problemas de **Big Data** com muitas observações, porque ele **utiliza o conhecimento prévio adquirido das distâncias anteriores** para inferir.
- A ideia: se o ponto A está **muito distante** de B, e B **muito próximo** de C, então A e C estão **muito distantes**, **sem precisar calcular** a distância explicitamente. (Isso é a desigualdade triangular; fora dos slides.)
- **'brute'** calcula a distância para **todos os pontos possíveis**.

Explicando do zero:

- **brute (força bruta):** o `for` simples que compara com todo mundo. Exato e simples, mas lento com muitas linhas.
- **kd_tree e ball_tree:** estruturas de dados em árvore, construídas uma vez, que **organizam os pontos no espaço** para pular regiões inteiras sem medir cada ponto. Analogia: um índice de banco de dados que evita o *full table scan*. O kd_tree divide o espaço com cortes perpendiculares aos eixos; o ball_tree agrupa os pontos em "bolas" (esferas). Estes detalhes de como dividem são fora dos slides; no slide só vale a recomendação de uso acima.
- **Regra prática fora dos slides:** o kd_tree costuma ir bem até cerca de 20 dimensões; acima disso o ball_tree ou o brute tendem a ser melhores. O número 20 vem da literatura e da documentação do scikit-learn, não dos slides.

Divergência registrada sobre o 'auto':

- **Slide 31:** o 'auto' escolhe "olhando para o resultado obtido nas observações anteriores".
- **Documentação do scikit-learn:** o 'auto' decide a estrutura com base nos **dados passados ao `fit`** (número de amostras, dimensões, métrica, esparsidade). Ele não aprende com resultados de predições anteriores.
- Executado (exemplo nosso): com a base de vinhos (13 atributos), `KNeighborsClassifier(algorithm='auto')` escolheu internamente o `kd_tree`.

Importante para a prova: **os algoritmos kd_tree, ball_tree e brute dão o mesmo resultado** (os mesmos vizinhos); mudam apenas **tempo e memória**. Nenhum deles "melhora a acurácia".

### p e metric (slides 33 e 34)

O slide 33: **p=1** ativa a distância de **Manhattan**; **p=2**, a **Euclidiana**. **Se nenhum p for informado**, ativa-se a **Minkowski**, que é a generalização das duas.

Divergência a notar: no scikit-learn, `metric='minkowski'` é o padrão e `p=2` também é o padrão, de modo que o comportamento padrão é **equivalente à Euclidiana**. Na biblioteca, o p é um valor sempre presente (padrão 2). O slide diz que "sem p" fica Minkowski; na prática, a Minkowski com p=2 **é** a Euclidiana. Na prova, responda o que o slide diz (Minkowski, generalização) e saiba que na prática o padrão resulta na Euclidiana.

O slide 34 diz que o parâmetro `metric` escolhe o tipo de distância mais adequado ao problema (padrão: minkowski). Também diz que **weights** é o inverso da distância e pode ser configurado de **três maneiras**:

- **`'uniform'`**: mesmo peso para todos os vizinhos.
- **`'distance'`**: pesos maiores para os vizinhos mais próximos (na biblioteca, 1/d; ver seção 9).
- **`callable`**: você incorpora uma função específica.

### Resumo em código

Padrões do scikit-learn, executados (exemplo nosso):

```python
print(KNeighborsClassifier(n_neighbors=3).get_params())
# {'algorithm': 'auto', 'leaf_size': 30, 'metric': 'minkowski',
#  'metric_params': None, 'n_jobs': None, 'n_neighbors': 3, 'p': 2,
#  'weights': 'uniform'}
```

Um modelo configurado com tudo o que os slides citam:

```python
knn = KNeighborsClassifier(
    n_neighbors=7,         # K ímpar
    weights='distance',    # ou 'uniform', ou uma função
    algorithm='kd_tree',   # 'auto', 'ball_tree', 'kd_tree', 'brute'
    metric='minkowski',    # padrão
    p=1,                   # 1 = Manhattan; 2 = Euclidiana
)
```

---

## 15. Custo computacional: treino rápido, previsão cara

Esta seção reúne o que os slides 17 e 19/20 dizem, em termos de "custo" (a conta é fora dos slides, para dar a noção).

| Etapa | k-NN | Observação |
| :-- | :-- | :-- |
| Treino | Praticamente nulo: guarda os dados | Com kd_tree ou ball_tree há um custo extra de construir a árvore (da ordem de N log N, fora dos slides) |
| Previsão (brute) | Compara com os N exemplos, cada um com d atributos: da ordem de N × d | Cresce com a base e com os atributos |
| Previsão (kd_tree) | Bem menor em baixa dimensão | Perde a vantagem em alta dimensão |
| Memória | Guarda a base inteira | Base de milhões de linhas ocupa muita memória |

Contraste com um modelo comum (como a regressão linear da Aula 5): treina uma vez, de forma cara, e depois prevê quase de graça (uma conta com poucos coeficientes). O k-NN inverte: treina de graça e prevê caro. É exatamente a ideia de **lazy**.

---

## 16. Armadilhas e resumo para a prova

Lista de afirmações que costumam aparecer, com o veredicto:

| Afirmação | Veredicto | Por quê |
| :-- | :-- | :-- |
| "O k-NN não precisa de dados de treino" | Falso | Precisa dos exemplos rotulados; não precisa é de uma fase de treinamento (slide 5) |
| "O k-NN produz um modelo explícito" | Falso | Slides 5 e 20: não tem modelo explícito |
| "K=1 avaliado no treino dá 100%" | Verdadeiro | Slide 5 |
| "K grande causa overfitting" | Falso | K grande causa underfitting; K pequeno causa overfitting (slide 13) |
| "K pequeno é mais resistente a outliers" | Falso | K pequeno é sensível a outliers (slide 13) |
| "K par é recomendado" | Falso | Recomenda-se ímpar, para evitar empates (slides 12 e 13) |
| "O k-NN assume distribuição normal" | Falso | Não paramétrico (slide 4) |
| "O k-NN funciona bem com milhares de atributos" | Falso | Maldição da dimensionalidade (slides 11 e 19) |
| "Padronizar os atributos é opcional com Euclidiana" | Falso | Ela exige padronização (slide 22) |
| "Inserir novo dado exige retreinar" | Falso | Inserção instantânea (slide 17) |
| "Só funciona com duas classes" | Falso | Funciona facilmente em multiclasse (slide 18) |
| "A previsão é rápida em bases grandes" | Falso | Alto custo de previsão (slides 19 e 20) |
| "Manhattan é menos sensível a outliers que a Euclidiana" | Verdadeiro | Slide 24 |
| "Hamming serve para vetores binários e categóricas (one-hot)" | Verdadeiro | Slide 25 |
| "Com variáveis não correlacionadas, a Mahalanobis equivale à Euclidiana" | Verdadeiro | Slide 26 |
| "kd_tree, ball_tree e brute escolhem vizinhos diferentes" | Falso | Mudam só a velocidade; os vizinhos são os mesmos (exato) |

### Divergências em um só lugar

| Tema | Slide | Biblioteca ou literatura | O que responder |
| :-- | :-- | :-- | :-- |
| Peso na votação ponderada | 16: 1/d² | `weights='distance'`: 1/d | Fórmula do slide: 1/d². Se a questão fala da biblioteca: 1/d. |
| Como o 'auto' escolhe | 31: olhando resultados anteriores | Documentação: usa os dados do `fit` | Responder o slide; saber a versão da documentação |
| Padrão de distância | 33: sem p, Minkowski | Padrão é Minkowski com p=2, igual à Euclidiana | Responder o slide; saber que na prática dá Euclidiana |
| K ímpar sempre | 12 e 13 | Só evita empate com 2 classes | Responder o slide: use ímpares |
| 20 dimensões para kd_tree | Não está nos slides | Regra prática | Não é cobrada pelos slides |

### Quando usar k-NN (exemplo nosso)

- Base pequena ou média, poucos atributos relevantes, atributos numéricos já padronizados.
- Bom como **linha de base (baseline)** para comparar com modelos mais sofisticados.
- Evitar com dezenas de milhares de atributos, com muitas variáveis categóricas ou quando a predição precisa ser muito rápida sobre uma base gigante.

### Fixe isto

1. Supervisionado, não paramétrico, baseado em instâncias, lazy; classificação (votação) e regressão (média).
2. Dois pontos-chave: **métrica de distância** e **K**.
3. K pequeno: overfitting e sensível a outlier; K grande: underfitting, viés para a classe majoritária, mais resistente a outliers; K ímpar evita empate.
4. Distância ponderada: peso maior aos mais próximos (slide: 1/d²; biblioteca: 1/d).
5. Euclidiana exige padronização; Manhattan é menos sensível a outliers; Minkowski generaliza (r=1, r=2); Hamming para binários e one-hot; Mahalanobis para variáveis correlacionadas.
6. Treino quase nulo, previsão cara; inserção instantânea; paralelizável; multiclasse.
7. Desvantagens: alta dimensão, categóricas, sensível a K e à escala, sem modelo explícito, variáveis irrelevantes.
8. Hiperparâmetros: `n_neighbors`, `algorithm` (`auto`, `ball_tree`, `kd_tree`, `brute`), `p`, `metric`, `weights` (`uniform`, `distance`, callable).
9. Usos não supervisionados: LOF (outliers), KNNImputer (imputação), t-SNE e UMAP (redução de dimensionalidade).
