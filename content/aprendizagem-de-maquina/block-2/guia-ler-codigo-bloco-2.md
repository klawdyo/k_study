# Guia de Leitura de Código · Bloco 2 (scikit-learn)

> **Para a prova:** o objetivo não é escrever código em um editor nem decorar assinaturas de funções. A prova traz **trechos curtos de código scikit-learn** para você avaliar:
> 1. A **ordem das ações** está correta?
> 2. Há algum **erro de lógica** (não de sintaxe)?
> 3. As classes e métodos usados correspondem ao problema em questão?

---

## 1. Padrão Universal do scikit-learn: Os 4 Verbos

No scikit-learn, quase todo modelo segue a mesma interface com quatro métodos principais:

```python
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

modelo = LinearRegression()        # 1. Instanciação com hiperparâmetros
modelo.fit(X_train, y_train)       # 2. Treinamento (ajuste dos parâmetros com os dados)
y_pred = modelo.predict(X_test)    # 3. Predição (inferência em novos dados)
# score calcula a métrica padrão: R² em regressão, Acurácia em classificação
pontuacao = modelo.score(X_test, y_test) # 4. Avaliação
```

---

## 2. A Ordem das Ações e os Maiores Erros de Lógica

### A ordem correta de um fluxo de avaliação

1. **Dividir** em treino e teste (`train_test_split`).
2. **Ajustar o pré-processamento só no treino** (`scaler.fit_transform(X_train)`).
3. **Treinar** o modelo (`fit`) com os dados já transformados.
4. **Prever** no teste, aplicando só `transform` (`model.predict(scaler.transform(X_test))`).
5. **Medir** com a métrica compatível com a tarefa.

Se um passo aparece antes do que ele depende, ou se algo "aprende" com o teste, há erro de lógica. Um `Pipeline` mantém essa ordem automaticamente.

### Erro 1: Vazamento de Dados no Pré-Processamento (*Data Leakage*)
* **Regra de Ouro:** Toda transformação estatística (média, desvio padrão, imputação) DEVE aprender apenas com os dados de **treino**.

```python
# ERRADO (vazamento de dados clássico):
scaler = StandardScaler()
X_norm = scaler.fit_transform(X) # Calculou média e desvio usando o dataset inteiro!
X_train, X_test, y_train, y_test = train_test_split(X_norm, y)

# CORRETO:
X_train, X_test, y_train, y_test = train_test_split(X, y)
scaler = StandardScaler()
X_train_norm = scaler.fit_transform(X_train) # Aprende parâmetros e transforma o treino
X_test_norm = scaler.transform(X_test)       # Apenas aplica os parâmetros aprendidos!
```

**O mesmo vale dentro da validação cruzada.** Se você padroniza `X` inteiro e depois chama `cross_val_score`, cada fold de validação já influenciou a média e o desvio. O certo é colocar o scaler num `Pipeline` e passar o pipeline ao `cross_val_score`:

```python
pipe = Pipeline([('scaler', StandardScaler()), ('knn', KNeighborsClassifier(n_neighbors=5))])
scores = cross_val_score(pipe, X, y, cv=5)   # o scaler é re-ajustado a cada rodada
```

**Escolher hiperparâmetros olhando o teste** (ex.: o melhor K do k-NN) é outro tipo de vazamento: a nota do teste fica otimista. Escolha K em validação (ou com validação cruzada no treino) e use o teste uma única vez, no fim.

---

### Erro 2: Onde a Escala é Importante vs. Onde é Indiferente

| Modelo | Exige Normalização/Padronização? | Por quê? |
| :-- | :-- | :-- |
| **k-NN (`KNeighborsClassifier` / `Regressor`)** | **Sim (praticamente obrigatório)** | O algoritmo calcula distâncias geométricas (L1, L2). Variáveis com números grandes dominam a distância e anulam variáveis menores. |
| **Regressão com Regularização (`Ridge`, `Lasso`)** | **Fortemente recomendado** | A penalidade (λ Σ β² no Ridge; λ Σ do módulo de β no Lasso) pune coeficientes grandes. Sem padronização, a penalidade pune desproporcionalmente variáveis com escalas pequenas. O slide 19 trata como "um bom hábito". |
| **Gradiente descendente (`SGDRegressor`)** | **Sim** | Atributos em escalas muito diferentes geram passos desiguais; com passo (`eta0`) alto o erro explode e os coeficientes viram números gigantes. |
| **Árvore de Decisão (`DecisionTreeClassifier`)** | **Desnecessário** | A árvore avalia apenas a **ordem relativa** dos dados em cada coluna individualmente (X_j ≤ c). Multiplicar uma coluna por 1.000 não muda a ordem de nenhum valor. |

---

### Erro 3: Mistura de Tarefas (Classificação vs. Regressão)

A prova costuma apresentar trechos onde o desenvolvedor usa o estimador ou a métrica errada para a tarefa:

| Elemento | Para Problemas de Regressão (Y contínuo) | Para Problemas de Classificação (Y categórico) |
| :-- | :-- | :-- |
| **Estimador k-NN** | `KNeighborsRegressor` (prediz média) | `KNeighborsClassifier` (prediz classe majoritária) |
| **Estimador Árvore** | `DecisionTreeRegressor` (média na folha) | `DecisionTreeClassifier` |
| **Estimador Linear** | `LinearRegression`, `Ridge`, `Lasso` | `LogisticRegression` (é classificação!) |
| **Métrica de Avaliação** | `mean_squared_error`, `mean_absolute_error`, `r2_score` | `accuracy_score`, `precision_score`, `recall_score`, `f1_score`, `confusion_matrix` |

> **Pegadinha típica:** usar `accuracy_score(y_test, y_pred)` após rodar um `LinearRegression()`. Como Y é contínuo, a função **lança `ValueError`** ("continuous is not supported"): acurácia é uma métrica de classificação e não aceita alvo contínuo. O mesmo acontece ao dar `fit` de um `KNeighborsClassifier` com alvo contínuo (`Unknown label type: continuous`). O que a prova cobra é reconhecer a **incompatibilidade** entre tarefa, estimador e métrica.

---

## 3. Guia de Leitura por Algoritmo

### A. Regressão Linear, Ridge e Lasso
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso

# OLS comum: sem hiperparâmetros de regularização
modelo_ols = LinearRegression()

# Ridge (L2): alpha controla a força da penalidade quadrática
# alpha=0 equivale a LinearRegression; alpha alto encolhe coeficientes (sem zerar)
modelo_ridge = Ridge(alpha=1.0)

# Lasso (L1): alpha controla a penalidade em módulo
# alpha alto zera coeficientes irrelevantes (seleção de atributos)
modelo_lasso = Lasso(alpha=0.1)
```
* **O que checar no código de Regressão:**
  1. As variáveis foram padronizadas antes de treinar Ridge, Lasso ou gradiente descendente (de preferência dentro de um `Pipeline`)?
  2. O `.score()` de um regressor devolve o **R²** (maior é melhor). Para erros, use `mean_absolute_error` e `mean_squared_error` (menor é melhor). O R² ajustado só é descrito no slide 52; não existe função pronta para ele em `sklearn.metrics`.
  3. Se o MAE é calculado "na mão", há `abs` (ou `np.abs`) antes da média? Sem módulo, erros positivos e negativos se cancelam e o MAE sai quase zero. A ordem da subtração (real menos previsto, ou o contrário) só troca o sinal e não muda o MAE nem o MSE.
  4. Em `SGDRegressor`, o passo (`eta0`) é razoável? Passo grande com atributos sem escala faz o gradiente divergir (R² absurdamente negativo).
  5. Cuidado: o slide 51 diz que o R² "está sempre entre 0 e 1"; na literatura ele pode ser negativo no teste. Na prova, responda conforme o slide.

---

### B. k-NN (k-Nearest Neighbors)
```python
from sklearn.neighbors import KNeighborsClassifier

modelo_knn = KNeighborsClassifier(
    n_neighbors=5,          # Valor de K (ímpar evita empate em classificação binária)
    weights='uniform',      # 'uniform' (voto igual) ou 'distance' (mais peso aos mais próximos)
    metric='minkowski',     # Distância padrão
    p=2                     # p=1: Manhattan; p=2: Euclidiana
)
```
* **O que checar no código de k-NN:**
  1. Houve `scaler.fit_transform` no treino e `scaler.transform` no teste? Se não houve escala, **há erro de lógica grave**.
  2. K foi escolhido olhando o teste? Isso é erro; escolha em validação.
  3. O modelo foi avaliado nos dados de teste? Avaliar `knn.score(X_train, y_train)` com `n_neighbors=1` dá 100% artificialmente. O mesmo ocorre com `weights='distance'` em qualquer K: o ponto consultado está a distância zero de si mesmo e domina o voto.
  4. K par em **classificação** binária causa empate. Em **regressão** (`KNeighborsRegressor`) a média dos K vizinhos não tem empate, e K par é aceitável.
  5. O estimador combina com o alvo? `KNeighborsClassifier` para classes, `KNeighborsRegressor` para números.

---

### C. Árvores de Decisão
```python
from sklearn.tree import DecisionTreeClassifier

modelo_arvore = DecisionTreeClassifier(
    criterion='gini',           # 'gini' ou 'entropy' (em regressão: 'squared_error')
    max_depth=4,                # Pré-poda: limita a profundidade máxima
    min_samples_split=10,       # Nós com < 10 amostras não se dividem
    min_samples_leaf=5,         # Folhas devem ter no mínimo 5 amostras
    random_state=42
)
```
* **O que checar no código de Árvores:**
  1. O modelo possui parâmetros de poda **efetivos** (`max_depth` baixo, `min_samples_leaf` alto)? Valores iguais ao padrão (`min_samples_leaf=1`, `max_depth=None`) ou muito altos não restringem nada. Se não há restrição e o programador comemora 100% de acurácia no treino, **está ocorrendo overfitting**.
  2. O código aplicou `StandardScaler` em uma árvore isolada? Não gera erro de execução, mas é redundante: a árvore só usa a ordem dos valores em cada coluna.
  3. Uma coluna categórica **nominal** foi codificada como 0, 1, 2, 3 (`LabelEncoder`)? Isso cria uma ordem artificial, e a árvore só consegue agrupar categorias vizinhas na numeração. O adequado é *one-hot*. O scikit-learn trata tudo como numérico e faz cortes binários (`<=` e `>`).
  4. Em regressão com árvore (`DecisionTreeRegressor`), a predição é a **média dos exemplos da folha**; por isso a árvore faz previsões em degraus e **não extrapola** além dos valores de y vistos no treino. Já o `.score()` é o R².

---

## 4. Checklist Rápido para Questões de "Ache o Erro"

Quando a questão trouxer um bloco de código de 5 a 15 linhas, passe mentalmente por este checklist:
1. [ ] **Split ocorreu antes de qualquer transformação?** (Se transformou antes, vazamento de dados).
2. [ ] **`fit_transform` foi chamado apenas no treino e `transform` no teste?** (Se usou `fit_transform` no teste, vazamento de dados).
3. [ ] **A ordem dos passos é split, scaler no treino, fit, predict, métrica?** (Treinar antes de padronizar e prever com dados padronizados é erro de ordem.)
4. [ ] **k-NN, Ridge/Lasso ou gradiente descendente receberam dados com escalas heterogêneas sem normalizar?** (Erro de lógica).
5. [ ] **A métrica é compatível com o tipo de alvo?** (R², MAE, MSE para contínuo; acurácia, F1, matriz de confusão para discreto).
6. [ ] **O hiperparâmetro (ex.: K) foi escolhido sem olhar o teste?** E a validação cruzada usa `Pipeline` com o scaler dentro?
7. [ ] **A árvore tem restrição de profundidade efetiva ou está decorando o treino?**
8. [ ] **O modelo é o correto para a tarefa?** (ex.: `LogisticRegression` para classes, `LinearRegression` ou os regressores para números).

> **Complementos (fora dos slides):** `export_text` e `plot_tree` para ler a árvore, e o diagnóstico de resíduos com padrão em curva. Aparecem em questões marcadas "complemento" e não são o foco da prova.
