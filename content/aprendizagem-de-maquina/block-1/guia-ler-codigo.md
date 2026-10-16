# Como ler um trecho de código de AM, do zero

Este guia é para quem **programa bem** e **nunca viu scikit-learn**. A prova não pede que você escreva código; pede que você **leia** 5 a 10 linhas e diga: "a ordem está certa?", "falta algo?", "onde está o erro de lógica?". O código sempre "roda"; o erro é **conceitual**.

A chave de tudo é uma ideia só, que você já conhece da engenharia de software: **o teste de aceitação não pode usar informação da produção**. Em AM, o conjunto de **teste** faz o papel de "dados que o modelo nunca viu". Toda vez que uma linha de código deixa o modelo, o escalonador ou o imputador "enxergarem" o teste, o resultado fica **otimista** (parece melhor do que será no mundo real). Isso se chama **vazamento de dados (data leakage)**.

---

## 1. `X` e `y`: entrada e resposta

Pense numa tabela de banco de dados. Cada linha é um exemplo (um cliente); cada coluna, uma característica.

```python
X = df.drop("inadimplente", axis=1)   # tudo, menos a resposta
y = df["inadimplente"]                # só a resposta (o alvo, target)
```

- `X` (maiúsculo, é uma tabela) = os **atributos (features)**: o que o modelo pode olhar.
- `y` (minúsculo, é uma coluna) = o **alvo (target)**: o que queremos prever. É o "gabarito".
- `drop(coluna, axis=1)`: remove uma **coluna** (`axis=1` = colunas; `axis=0` = linhas). Devolve uma cópia sem ela.

**Primeiro erro clássico:** deixar o alvo dentro de `X`. É como passar o gabarito junto com a prova. O modelo "acerta" 100 % no laboratório e falha em produção, onde o gabarito não existe.

---

## 2. `train_test_split`: separar treino e teste

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
```

Analogia: **treino** = ambiente de desenvolvimento (o modelo estuda aqui); **teste** = homologação com dados que ele nunca viu (a nota final sai daqui).

| Parâmetro | O que faz | Analogia |
| :-- | :-- | :-- |
| `test_size=0.2` | 20 % das linhas vão para o teste, 80 % para o treino | tamanho da amostra de homologação |
| `random_state=42` | fixa a "semente" do sorteio; o mesmo código dá a mesma divisão sempre | seed de gerador aleatório: **reprodutibilidade** |
| `stratify=y` | mantém em treino e teste **a mesma proporção de classes** de `y` | amostragem estratificada: se 4 % são inadimplentes, os dois conjuntos terão ~4 % |
| `shuffle=True` (padrão) | embaralha as linhas antes de cortar | sortear em vez de pegar "as primeiras 80 %" |

Quando usar o quê:
- **Classes desbalanceadas** (96 % de uma classe): use `stratify=y`. Sem isso, o teste pode ficar sem nenhum exemplo da classe rara.
- **Dados no tempo** (vendas diárias, sensores): use `shuffle=False` (ou `TimeSeriesSplit`). Embaralhar mistura futuro com passado.
- **Sempre** fixe `random_state` se quiser resultados que outra pessoa consiga repetir.

---

## 3. A ideia de estimador: `fit`, `transform`, `predict`, `score`

No scikit-learn quase tudo é um **objeto com estado** (como uma instância de classe com atributos internos). Existem dois tipos:

1. **Transformador (transformer):** muda os dados (escalar, imputar, codificar, PCA). Métodos: `fit`, `transform`, `fit_transform`.
2. **Modelo (estimator/classifier/regressor):** aprende a prever. Métodos: `fit`, `predict`, `score`.

| Método | O que faz | Analogia |
| :-- | :-- | :-- |
| `fit(X_train)` | **aprende** parâmetros a partir dos dados passados (média e desvio, mínimo e máximo, a mediana a usar, os componentes do PCA, as regras de uma árvore) | construtor + "calibrar" o objeto |
| `transform(X)` | **aplica** o que foi aprendido, sem aprender nada novo | chamar um método puro com a configuração já guardada |
| `fit_transform(X_train)` | `fit` e depois `transform`, na mesma chamada | atalho |
| `predict(X_test)` | devolve a previsão do modelo para cada linha | `model.predict(x)` = inferência |
| `score(X_test, y_test)` | compara previsão com o gabarito e devolve uma nota (acurácia em classificação) | teste automatizado |

```python
scaler = StandardScaler()
scaler.fit(X_train)                  # guarda média e desvio DO TREINO
X_train_s = scaler.transform(X_train)
X_test_s  = scaler.transform(X_test) # usa a média e o desvio DO TREINO
```

### Regra de ouro: `fit` só no treino

- `fit` / `fit_transform` → **somente** em `X_train`.
- `transform` / `predict` / `score` → no treino **e** no teste (o teste só é "consumido", nunca "estudado").

Por quê? Em produção, os dados novos chegam **depois**; você não conhece a média deles. Se na avaliação o escalonador calcula a média incluindo o teste, o teste deixa de ser "dado novo". Se você vir `fit_transform(X_test)` ou `fit(X)` com `X` inteiro **antes** do split, é erro.

---

## 4. O catálogo de chamadas que aparecem

### Limpeza e preparação (transformadores)

| Chamada | O que faz | O que **aprende** no `fit` |
| :-- | :-- | :-- |
| `SimpleImputer(strategy="median")` | preenche ausentes (`NaN`) com média, mediana ou moda (`"most_frequent"`) | a mediana (ou média/moda) de cada coluna **do treino** |
| `StandardScaler()` | padroniza: média 0, desvio 1 (z-score) | média e desvio do treino |
| `MinMaxScaler()` | reescala para [0, 1] | mínimo e máximo do treino (**muito sensível a outliers**) |
| `OneHotEncoder(handle_unknown="ignore")` | categoria nominal vira colunas 0/1 ("Natal", "Caicó" → duas colunas) | a lista de categorias vistas no treino |
| `OrdinalEncoder(categories=[[...]])` | categoria **ordinal** vira inteiro respeitando a ordem que você informa (Fundamental < Médio < Superior) | as categorias (ou a ordem que você deu) |
| `PCA(n_components=0.95)` | reduz a quantidade de colunas mantendo 95 % da variância | os componentes principais do treino |
| `SMOTE`, `RandomOverSampler` (biblioteca `imblearn`) | aumentam a classe rara: o `SMOTE` cria exemplos **sintéticos** interpolando vizinhos; o `RandomOverSampler` **repete** exemplos existentes | usam o conjunto passado; método é `fit_resample(X, y)` |
| `NearMiss`, `RandomUnderSampler` | **reduzem** a classe majoritária | idem |

Detalhes de leitura:
- `OneHotEncoder` x `OrdinalEncoder`: nominal (cidade, cor) → one-hot; ordinal (escolaridade, tamanho P/M/G) → ordinal. `LabelEncoder` numera categorias na ordem alfabética e serve em geral para o **alvo**; em atributo nominal cria uma ordem falsa.
- `PCA` e escalas: o PCA procura direções de maior variância; se uma coluna está em milhares (renda) e outra em unidades (filhos), a de milhares domina. **Padronize antes**.
- `SMOTE`/`NearMiss` mudam o **número de linhas**. Só se aplicam ao **treino**. Por isso usam `fit_resample` e não `transform`.

### Modelos e métricas

| Chamada | Em uma frase |
| :-- | :-- |
| `KNeighborsClassifier(n_neighbors=5)` | k-NN: classifica pelos 5 vizinhos mais próximos; usa **distância**, logo precisa de **escala** |
| `SVC(kernel="rbf")` | SVM: também baseado em distância; precisa de escala |
| `DecisionTreeClassifier`, `RandomForestClassifier` | árvores: **não** precisam de escala |
| `LogisticRegression()` | classificação binária/multiclasse, **apesar do nome**; o alvo tem de ser classes discretas |
| `accuracy_score(y_true, y_pred)`, `classification_report(...)` | acurácia; relatório com precisão, revocação (recall) e F1 **por classe** |

### Pandas que aparece

```python
df.dropna()                    # remove LINHAS com algum NaN (axis=0, padrão)
df.dropna(axis=1)              # remove COLUNAS com algum NaN (cuidado!)
df.dropna(subset=["rotulo"])   # remove só linhas em que "rotulo" é NaN
df["renda"].fillna(valor)      # preenche NaN com um valor (média, mediana...)
df["idade"].quantile(0.25)     # Q1: valor abaixo do qual estão 25 % dos dados
df["idade"].clip(lower=a, upper=b)   # limita: abaixo de a vira a; acima de b vira b
pd.get_dummies(df["cidade"])   # one-hot direto no pandas
df.drop("id", axis=1)          # tira a coluna id
```

`quantile` serve para a **regra do IQR** (amplitude interquartil) de outliers: `IQR = Q3 - Q1`; limites `Q1 - 1.5*IQR` e `Q3 + 1.5*IQR`. **Winsorizar** = trocar o valor fora do limite **pelo próprio limite** (é o que o `clip` faz). Remover linhas é outra opção, mas só no treino.

---

## 5. Validação cruzada, pipelines e divisores

### `Pipeline`: a esteira que repete as etapas na ordem certa

```python
pipe = Pipeline([
    ("imp", SimpleImputer(strategy="median")),
    ("sc",  StandardScaler()),
    ("clf", SVC()),
])
pipe.fit(X_train, y_train)          # cada etapa faz fit_transform no treino, em ordem
pipe.score(X_test, y_test)          # cada etapa só faz transform no teste
```

É um CI: "etapa 1 → etapa 2 → modelo", garantindo que **nada é ajustado com o teste**. Os nomes (`"imp"`, `"sc"`, `"clf"`) são apenas rótulos. Para balanceamento use o `Pipeline` de `imblearn.pipeline`, que aplica o `SMOTE` só no `fit` (treino) e **não** na hora de prever.

### `ColumnTransformer`: tratar cada coluna do seu jeito

```python
prep = ColumnTransformer([
    ("num", StandardScaler(), ["idade", "renda"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["cidade"]),
])
```

Diz: "padronize as numéricas, one-hot nas categóricas". Costuma ser a primeira etapa de um `Pipeline`.

### `cross_val_score`, `StratifiedKFold`, `KFold`, `TimeSeriesSplit`

- **Validação cruzada (cross-validation):** em vez de um único corte treino/teste, repete o corte **k vezes** (k dobras, *folds*). Em cada rodada, uma dobra serve de teste e as demais de treino. Resultado: k notas, cuja média é mais estável que uma nota só.
- `cross_val_score(pipe, X, y, cv=cv, scoring="f1")` devolve um array de notas. O primeiro argumento deve ser o **Pipeline inteiro** para que o pré-processamento seja refeito em cada dobra.
- `KFold(n_splits=5)`: corta em 5 pedaços (pode embaralhar com `shuffle=True`).
- `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`: igual, mas **mantém a proporção de classes** em cada dobra. Use em classificação, sobretudo desbalanceada.
- `TimeSeriesSplit(n_splits=5)`: respeita o tempo; o treino é sempre **anterior** ao teste.
- `GridSearchCV(pipe, param_grid, cv=cv)`: testa combinações de hiperparâmetros por validação cruzada **dentro do treino**.

---

## 6. Quadro: o que cada chamada faz e o que ela não deve ver

| Chamada | Pode ver | **Não** pode ver | Motivo |
| :-- | :-- | :-- | :-- |
| `SimpleImputer.fit` | treino | teste | a mediana "vaza" informação do teste |
| `StandardScaler.fit` / `MinMaxScaler.fit` | treino | teste | média, desvio, mínimo e máximo são do treino |
| `OneHotEncoder.fit` | treino | teste | categorias aprendidas no treino |
| Limites de outliers (`quantile`) | treino | teste | os limites são "parâmetros aprendidos" |
| `PCA.fit` | treino **padronizado**, sem o alvo | teste, `y` | senão o componente contém o teste ou o gabarito |
| `SMOTE.fit_resample` / `NearMiss` | só treino | teste | o teste deve ficar com a distribuição real |
| `model.fit` | treino | teste | o modelo não pode estudar a prova |
| Escolha de hiperparâmetro | validação / dobras do treino | teste | senão o teste participou da escolha |
| `model.score` / `predict` final | teste | (é o único uso do teste) | a nota que vale |
| `transform` | treino e teste | ninguém é proibido | só aplica |

Frase para memorizar: **"aprende no treino, aplica nos dois, avalia no teste uma vez."**

---

## 7. A ordem canônica de um pipeline correto

1. **Limpeza estrutural que não usa estatística**: remover identificadores (`id`), **duplicatas**, padronizar formatos (datas, "AUTOMATICO" x "automático"), trocar valores sentinela (como −999) por `NaN`, remover linhas **sem rótulo**. (Pode vir antes da divisão porque não "aprende" nada com os dados.)
2. **Separar `X` e `y`** (o alvo fora de `X`).
3. **Dividir** treino e teste (`stratify=y`, `random_state`; sem embaralhar se for série temporal).
4. **Imputar ausentes**: `fit` no treino, `transform` nos dois.
5. **Tratar outliers**: limites calculados no treino, **antes** de normalizar.
6. **Codificar categorias** (one-hot / ordinal).
7. **Escalar/normalizar** (`fit` no treino).
8. **Reduzir dimensão** (PCA) e/ou selecionar atributos: `fit` no treino.
9. **Balancear** (SMOTE, undersampling): **só o treino**.
10. **Treinar** o modelo no treino (e escolher hiperparâmetros por validação cruzada **dentro do treino**).
11. **Avaliar uma vez** no teste, com métrica adequada (F1/recall se desbalanceado).

Observações: 4 e 6 às vezes trocam de lugar (por exemplo, imputar a moda de uma categoria antes de codificá-la), mas ambas vêm **depois** da divisão. Em código real, os passos 4 a 9 ficam dentro de um `Pipeline`/`ColumnTransformer`, e a validação cruzada refaz tudo em cada dobra.

---

## 8. Os 12 erros de lógica mais comuns

Cada item: código errado, depois a correção.

**1. Pré-processar antes de dividir** (vazamento por `fit` na base inteira).
```python
X_s = StandardScaler().fit_transform(X)
X_train, X_test = train_test_split(X_s)[:2]
```
Correção: `split` primeiro; `scaler.fit(X_train)`; `transform` nos dois.

**2. `fit_transform` no teste.**
```python
X_train_s = sc.fit_transform(X_train)
X_test_s  = sc.fit_transform(X_test)
```
Correção: `X_test_s = sc.transform(X_test)`.

**3. Alvo dentro de `X`.**
```python
X = df                      # df ainda tem a coluna "fraude"
model.fit(X, df["fraude"])
```
Correção: `X = df.drop("fraude", axis=1)`.

**4. Treinar no teste ou avaliar no treino.**
```python
model.fit(X_train, y_train)
print(model.score(X_train, y_train))
```
Correção: `model.score(X_test, y_test)`; comparar treino x teste revela overfitting.

**5. Escolher hiperparâmetro olhando o teste.**
```python
for k in (1, 3, 5, 7):
    acc = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train).score(X_test, y_test)
```
Correção: `GridSearchCV` ou `cross_val_score` **no treino**; teste só no final, uma vez.

**6. Codificar nominal como número ordenado.**
```python
df["cidade"] = LabelEncoder().fit_transform(df["cidade"])
```
Correção: `pd.get_dummies(df["cidade"])` ou `OneHotEncoder`. Ordinais (escolaridade) sim, com `OrdinalEncoder` e ordem explícita.

**7. Balancear antes de dividir (ou balancear o teste).**
```python
X_res, y_res = SMOTE().fit_resample(X, y)
X_train, X_test, y_train, y_test = train_test_split(X_res, y_res)
```
Correção: dividir com `stratify=y`; `SMOTE().fit_resample(X_train, y_train)`; teste intocado.

**8. Normalizar antes de tratar outliers.**
```python
X[["renda"]] = MinMaxScaler().fit_transform(X[["renda"]])
X["renda"] = X["renda"].clip(upper=X["renda"].quantile(0.95))
```
Correção: tratar outliers (limites do treino) e **depois** normalizar; o máximo extremo estraga a escala min-max.

**9. Calcular limites de outlier com o teste, ou remover linhas do teste.**
```python
q3 = X_test["renda"].quantile(0.75)
X_test = X_test[X_test["renda"] <= q3 + 1.5 * (q3 - q1)]
```
Correção: limites do **treino**; no teste, no máximo `clip` com os mesmos limites; não descarte linhas (a nota fica artificial e `X_test` deixa de casar com `y_test`).

**10. Embaralhar dados temporais.**
```python
train_test_split(X, y, test_size=0.2, shuffle=True)
```
Correção: `shuffle=False` ou `TimeSeriesSplit`; treino = passado, teste = futuro.

**11. Pré-processar fora do `Pipeline` e depois usar validação cruzada.**
```python
X_s = StandardScaler().fit_transform(X)
cross_val_score(SVC(), X_s, y, cv=5)
```
Correção: `cross_val_score(Pipeline([("sc", StandardScaler()), ("clf", SVC())]), X, y, cv=5)`.

**12. Métrica inadequada ou tratamento errado do ausente/alvo.**
```python
df["rotulo"] = df["rotulo"].fillna(df["rotulo"].mean())   # inventa classe 0,07
df.dropna(axis=1, inplace=True)                           # apaga coluna inteira por 2 NaN
print(accuracy_score(y_test, y_pred))                     # com 96 % de uma classe
```
Correção: remover linhas sem rótulo (`dropna(subset=["rotulo"])`), imputar só atributos (no treino), usar F1/recall da classe rara com `classification_report`, comparar com um classificador que sempre prevê a maioria.

---

## 9. Checklist de 30 segundos para a prova

Ao ler qualquer trecho, percorra de cima para baixo e pergunte:

1. O **alvo** está fora de `X`?
2. Há `fit` ou `fit_transform` em **algo que contém o teste** (ou a base inteira antes da divisão)?
3. O teste recebe só `transform`/`predict`?
4. Balanceamento, PCA, imputação e limites de outlier acontecem **depois** de dividir e **só com o treino**?
5. **Outliers antes de normalizar?** Nominal com one-hot?
6. Divisão **estratificada**? Dados temporais **sem embaralhar**? `random_state` fixo?
7. Quem está sendo **avaliado**: treino ou teste? Quem escolheu o hiperparâmetro?
8. A **métrica** serve ao problema (desbalanceado: F1/recall, não só acurácia)?
9. A validação cruzada recebe um **Pipeline** ou dados já pré-processados?
10. Falta algo óbvio: ausentes, duplicatas, id, texto não codificado, escala (se k-NN/SVM)?

Se a resposta "ruim" aparece em qualquer item, você achou o erro de lógica.
