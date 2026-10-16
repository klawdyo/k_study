# Como ler código de redes neurais e SVM

Este guia é para quem **programa bem** e ainda não leu scikit-learn com olho de prova. Na prova você **não escreve código**: lê 5 a 12 linhas e responde "o código tem erro de lógica?", "falta alguma coisa?", "a ordem está certa?". O código **sempre roda**; o erro é **de lógica** (conceito), nunca de sintaxe. Os exemplos numéricos abaixo foram **executados** em dados sintéticos nossos (marcados "exemplo nosso"); não são números da professora.

A ideia que sustenta quase tudo é a mesma do Bloco 1: **o teste é a homologação com dados nunca vistos**. Toda linha que deixa o modelo, o escalonador ou a escolha de hiperparâmetros "enxergarem" o teste deixa a nota otimista.

---

## 1. Mapa das classes que aparecem (mini-glossário)

| Nome | O que faz | Em uma frase de engenheiro |
| :-- | :-- | :-- |
| `train_test_split` | separa treino e teste | cria o ambiente de homologação |
| `StandardScaler` | coloca cada coluna com média 0 e desvio 1 | converte tudo para a mesma unidade |
| `Pipeline` | encadeia passos; o último é o modelo | linha de montagem (middlewares) |
| `MLPClassifier` / `MLPRegressor` | rede neural para classes / para números | o mesmo motor, saídas diferentes |
| `SVC` / `SVR` | SVM para classes / para números | procura a fronteira de maior margem |
| `GridSearchCV` | testa combinações de hiperparâmetros com validação cruzada | busca em grade, dentro do treino |
| `cross_val_score` | valida em várias dobras | roda o experimento várias vezes |
| `.fit(...)` | **aprende** com os dados passados | "estuda" |
| `.transform(...)` | **aplica** o que foi aprendido | "usa a tabela já calibrada" |
| `.predict(...)` | devolve as classes previstas | resposta final |
| `.score(X, y)` | devolve a acurácia | nota |

Regra de leitura: em toda linha com `fit` ou `fit_transform`, pergunte **quais dados ela enxerga**. Só o treino é permitido.

---

## 2. Padronização: quem precisa e quem não precisa

**Precisam de colunas na mesma escala:** SVM (a margem é uma distância), rede neural (as somas ponderadas e o gradiente se desequilibram), k-NN. **Não precisam:** árvores e florestas.

Exemplo nosso (dados sintéticos, a classe depende sobretudo da idade; renda varia de 20 mil a 300 mil):

| Modelo | Sem padronizar | Com `StandardScaler` |
| :-- | :-- | :-- |
| `SVC` (kernel RBF) | 63,3% no teste | 92,5% no teste |
| `MLPClassifier` | 51,7% no teste | 94,2% no teste |

Erro de lógica típico:

```python
modelo = SVC(kernel='rbf', C=1.0)
modelo.fit(X_train, y_train)          # falta padronizar antes
```

Correção (o `Pipeline` já cuida do `fit` só no treino):

```python
pipe = Pipeline([('scaler', StandardScaler()), ('svm', SVC(kernel='rbf', C=1.0))])
pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))
```

---

## 3. Vazamento de dados (data leakage): onde ele se esconde

Cinco formas que a prova pode usar:

1. **`fit_transform` antes da divisão.** O escalonador aprende a média do teste.

```python
X_escalado = StandardScaler().fit_transform(X)           # erro: vê o futuro teste
X_train, X_test, y_train, y_test = train_test_split(X_escalado, y)
```

2. **`fit_transform` no teste.** Recalcula média e desvio com os dados do teste.

```python
X_test_scaled = scaler.fit_transform(X_test)             # erro: o certo é transform
```

Exemplo nosso: num lote de 47 clientes de renda alta, o mesmo SVC acertou 89,4% com `transform` e 78,7% com `fit_transform` no lote.

3. **Esquecer de transformar o teste** ("falta algo?").

```python
scaler = StandardScaler().fit(X_train)
mlp.fit(scaler.transform(X_train), y_train)
mlp.score(X_test, y_test)                                # falta scaler.transform(X_test)
```

Exemplo nosso: 83,3% com o teste bruto e 93,3% depois de `transform`.

4. **Escalonador fora do `Pipeline` na validação cruzada.**

```python
X_scaled = StandardScaler().fit_transform(X)             # viu todas as dobras
cross_val_score(SVC(), X_scaled, y, cv=5)                # erro de procedimento
# certo: cross_val_score(Pipeline([('s', StandardScaler()), ('m', SVC())]), X, y, cv=5)
```

Em padronização simples o efeito numérico costuma ser pequeno (no exemplo nosso as duas formas deram 92,7%); o que a prova cobra é o procedimento.

5. **Alvo dentro de `X`.**

```python
X = df                                                   # inclui a coluna 'classe'
y = df["classe"]
# certo: X = df.drop("classe", axis=1)
```

Exemplo nosso: 100% de acurácia no teste. Acurácia perfeita sem esforço é sinal de alerta.

---

## 4. Avaliação honesta: o que medir e onde

| Treino | Teste | Diagnóstico |
| :-- | :-- | :-- |
| alto | alto | bom ajuste |
| alto | bem menor | overfitting |
| baixo | baixo | underfitting |

Erro clássico: imprimir a nota do treino como "acurácia do modelo".

```python
print("Acurácia:", mlp.score(X_train_scaled, y_train))   # erro: mede memória
```

Exemplo nosso: rede grande (200 e 200 neurônios) com 99,3% no treino e 81,7% no teste.

Outro erro: **escolher hiperparâmetros olhando o teste** (K, `C`, `gamma`, limiar, número de neurônios).

```python
for C in [0.1, 1, 10, 100]:
    nota = SVC(C=C).fit(X_train_scaled, y_train).score(X_test_scaled, y_test)   # erro: escolhe pelo teste
```

O certo é validação cruzada **dentro do treino**, e o teste usado uma única vez:

```python
busca = GridSearchCV(SVC(), {'C': [0.1, 1, 10, 100], 'gamma': [0.1, 1, 10, 100]}, cv=5)
busca.fit(X_train_scaled, y_train)
print(busca.best_params_, busca.score(X_test_scaled, y_test))
```

E escolher pela **nota do treino** também é erro: exemplo nosso, a escolha por nota de treino foi `C=100, gamma=100` (100% no treino, 89,3% no teste), enquanto o `GridSearchCV` escolheu `C=10, gamma=1` (93,3% no teste).

---

## 5. Redes neurais: o que cada hiperparâmetro faz (Aula 10)

```python
MLPClassifier(
    hidden_layer_sizes=(100, 50),  # 2 camadas ocultas: 100 e 50 neurônios
    activation='relu',             # ativação das camadas ocultas
    solver='adam',                 # otimizador: 'adam', 'sgd' ou 'lbfgs'
    alpha=0.0001,                  # regularização L2 (pesos pequenos)
    learning_rate_init=0.001,      # tamanho do passo do gradiente
    max_iter=500,                  # teto de épocas
    early_stopping=True,           # para quando a validação interna não melhora
    random_state=42,
)
```

### 5.1 `hidden_layer_sizes`: cada número é uma camada

- `(64,)` = 1 camada oculta de 64 neurônios (a vírgula é obrigatória com um só elemento).
- `(64, 32)` = 2 camadas ocultas.
- `(64, 64, 64)` = 3 camadas de 64.
- **Erro de leitura:** `(3, 64)` não é "3 camadas de 64"; é 2 camadas (a primeira com 3 neurônios, um gargalo). Executamos: a rede tem 4 camadas contando entrada e saída.

### 5.2 Ativação (slides 42 a 51)

| Função | Onde usar |
| :-- | :-- |
| ReLU | camadas **ocultas** (padrão) |
| sigmoide | saída de classificação **binária** |
| softmax | saída de classificação **multiclasse** |
| linear | saída de **regressão** |

`activation='identity'` é linear: empilhar camadas lineares dá um único modelo linear. Em XOR, exemplo nosso: `identity` ficou em 50% e `relu` ou `tanh` chegaram a 100% com a mesma rede.

### 5.3 Convergência e `max_iter`

`ConvergenceWarning: Maximum iterations (5) reached` significa que o laço foi cortado antes de o erro estabilizar. A conduta é **aumentar `max_iter`** (ou revisar escala e taxa), não ignorar. Exemplo nosso: `max_iter=5` deu 53,6% no treino e 48,7% no teste; `max_iter=500` deu 94,2% e 94,0%.

### 5.4 Taxa de aprendizado (slide 41)

Valores usuais: 0.001, 0.003, 0.01, 0.03, 0.1, 0.3. Com `learning_rate_init=100.0` e `solver='sgd'`, exemplo nosso: perda final de cerca de 2e99 e acurácia de 51,7% (chute). Com `0.01`: perda 0,21 e acurácia 94,2%.

### 5.5 `early_stopping=True` (slides 37 e 38)

- Reserva **10% do treino** (padrão) como validação interna e treina com os 90% restantes.
- Para quando a nota de validação não melhora por `n_iter_no_change` épocas (padrão 10).
- O **teste continua intocado** e deve ser usado com `mlp.score(X_test, y_test)`.
- Erro de lógica: apresentar `best_validation_score_` como acurácia final.

### 5.6 `MLPClassifier` versus `MLPRegressor`

Alvo categórico: `MLPClassifier`. Alvo numérico contínuo (temperatura, preço): `MLPRegressor`. Usar o classificador com alvo contínuo lança `ValueError` ("Unknown label type").

---

## 6. SVM: o que cada hiperparâmetro faz (Aula 11)

```python
SVC(
    C=1.0,            # tolerância a erros (inverso da regularização)
    kernel='rbf',     # formato da fronteira: 'linear', 'rbf', 'poly', 'sigmoid'
    gamma='scale',    # raio de influência de cada ponto (kernels não lineares)
    probability=False # True liga a calibração para predict_proba (mais lento)
)
```

### 6.1 `C` e `gamma`: a tabela que decide a prova

| Hiperparâmetro | Valor alto | Valor baixo |
| :-- | :-- | :-- |
| `C` | penaliza muito os erros, margem rígida, fronteira complexa, **overfitting** | tolera erros, margem mole, fronteira simples, **underfitting** |
| `gamma` | influência pequena de cada ponto, fronteira recortada, **overfitting** | influência grande, fronteira suave, **underfitting** |

Combater **overfitting**: reduzir `C` e/ou reduzir `gamma`. Combater **underfitting**: aumentar `C` e/ou aumentar `gamma`.

Exemplos nossos: `gamma=500` deu 100% no treino e 73,3% no teste; `gamma=5000` piorou (100% e 50,0%); `gamma=1` deu 95,1% e 92,7%. Num modelo já simples demais, `C=0.0001` derrubou o treino de 85,8% para 50,9%.

### 6.2 Kernel inadequado

Fronteira reta (`'linear'`) em dados curvos (círculos concêntricos): exemplo nosso, 47,2% no teste, contra 100% do `'rbf'`. Padronizar, aumentar `C` ou trocar para `LinearSVC` **não** resolvem, porque todos continuam traçando retas.

### 6.3 Probabilidades e AUC

O SVM não produz probabilidade por natureza; produz a **distância assinada** ao hiperplano.

```python
svm = SVC(kernel='linear')
svm.fit(X_train_scaled, y_train)
svm.predict_proba(X_test_scaled)        # AttributeError: falta probability=True
```

Duas correções válidas: `SVC(probability=True)` ou usar `svm.decision_function(X_test_scaled)`. Para ROC e AUC, o `decision_function` serve; **não** use `predict` (rótulos 0/1): exemplo nosso, AUC 0,926 com `predict` contra 0,974 com `decision_function`.

### 6.4 `SVC` versus `SVR`

Classes: `SVC`. Número contínuo (preço): `SVR`. `OneClassSVM` é para anomalias.

---

## 7. `Pipeline`: ordem dos passos

```python
Pipeline([('padronizador', StandardScaler()), ('classificador', SVC())])   # certo
Pipeline([('classificador', SVC()), ('padronizador', StandardScaler())])   # erro: TypeError
```

Todos os passos são **transformadores**, exceto o **último**, que é o estimador. Dentro do `GridSearchCV` ou do `cross_val_score`, o `Pipeline` refaz o `fit` do escalonador em cada dobra, sem vazamento.

---

## 8. A ordem correta das ações

**Receita geral para SVM ou rede neural:**

1. Limpeza estrutural que **não aprende nada** (remover duplicatas, trocar -999 por `NaN`, padronizar texto).
2. **Dividir** em treino e teste (`train_test_split`).
3. **Imputar** ausentes com a estatística do **treino**.
4. **Padronizar** (`fit` só no treino; `transform` em treino e teste).
5. **Treinar** (`fit` do modelo) com o treino.
6. **Prever** no teste (`predict`).
7. **Avaliar** comparando `y_test` com as previsões.

**Receita para escolher hiperparâmetros:**

1. Dividir em treino e teste.
2. Montar o `Pipeline` e a grade de `C` e `gamma`.
3. Rodar `GridSearchCV` com validação cruzada **só no treino**.
4. Escolher a combinação pela nota média da validação.
5. Avaliar no teste, **uma única vez**.

Os pares de erro de ordem mais usados na prova:

| Ordem errada | Por que está errada |
| :-- | :-- |
| dividir antes de remover duplicatas | cópias iguais caem em treino e teste |
| imputar ou padronizar antes de dividir | o teste entra nas estatísticas |
| prever antes de treinar | modelo sem `fit` lança `NotFittedError` |
| avaliar antes de prever | não existe `y_pred` |
| padronizar depois de treinar | o modelo aprendeu em escala bruta |
| `GridSearchCV` antes da divisão | a busca viu o teste |
| avaliar candidatos no teste e depois escolher | o teste decidiu o vencedor |

---

## 9. Checklist de leitura (uma passada por trecho de prova)

1. **Qual é o alvo?** Categoria (classificador) ou número (regressor)? Está fora de `X`?
2. **Há `fit` ou `fit_transform`?** Quais dados ele vê? Só o treino?
3. **O teste é transformado com `transform`?** E existe a linha que o transforma?
4. **A divisão acontece antes de qualquer imputação, escala ou seleção?**
5. **As colunas têm escalas diferentes e o modelo é SVM, rede ou k-NN?** Há padronização?
6. **A nota é medida no teste?** (nunca no treino, e o teste só no fim)
7. **Algum hiperparâmetro foi escolhido olhando o teste ou o treino?**
8. **Os hiperparâmetros combinam com o sintoma?** Overfitting pede menos `C`, menos `gamma`, mais regularização; underfitting pede o contrário.
9. **A ativação é não linear nas camadas ocultas?** (`identity` é linear)
10. **Aparece `ConvergenceWarning` ou perda explosiva?** Pense em `max_iter`, taxa de aprendizado e escala.
11. **A métrica é compatível?** AUC pede escore contínuo (`decision_function` ou `predict_proba`), não rótulo.
12. **Se há `Pipeline`, o estimador está por último?**

Se todas as respostas estão certas e o trecho parece correto, a alternativa "não há erro" pode ser a certa.
