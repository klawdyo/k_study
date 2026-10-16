# Guia de Leitura de Código · Métricas de Avaliação no Scikit-Learn

> **Para o que serve este guia:** preparar você para responder às questões de código da prova. Na prova de Aprendizado de Máquina da professora Amanda Gondim, você **não precisará programar nem digitar código**, mas enfrentará questões que mostram **trechos curtos de código em Python (scikit-learn)** e perguntam:
> - *"Este código possui algum erro de lógica?"*
> - *"A ordem das operações está correta?"*
> - *"A métrica escolhida é adequada para o problema apresentado?"*
> - *"O que a saída deste relatório revela sobre o modelo?"*

---

## 1. O Padrão Universal do Scikit-Learn: `(y_true, y_pred)`

A regra de ouro mais importante para ler código de métricas no scikit-learn:

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

# FORMA CORRETA:
# 1º argumento: O que REALMENTE ACONTECEU (Ground Truth / y_true)
# 2º argumento: O que o MODELO PREVIU (Predições / y_pred)
matriz = confusion_matrix(y_true, y_pred)
precisao = precision_score(y_true, y_pred)
revocacao = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
```

### ⚠️ Erro de Lógica Clássico #1: Inversão de `y_true` e `y_pred`
```python
# CÓDIGO COM ERRO SUTIL DE LÓGICA:
precisao = precision_score(y_pred, y_test)  # INVERTIDO!
```
- **Por que é perigoso?** O Python não gera erro de sintaxe! Como ambos são arrays de números 0 e 1 de mesmo tamanho, o código executa normalmente.
- **O que acontece matematicamente?** A precisão inverte com o recall! O que deveria ser precisão vira recall e vice-versa. Em uma prova, identificar que os parâmetros foram passados na ordem trocada é um erro de lógica grave.

---

## 2. A Armadilha da Matriz de Confusão no Scikit-Learn

A função `confusion_matrix(y_true, y_pred)` devolve um array NumPy bidimensional 2 × 2 (no caso binário).

### A Convenção de Ordenação do Scikit-Learn:
```text
                  Coluna 0              Coluna 1
              (Previsto: 0)         (Previsto: 1)
Linha 0 (Real: 0)   [  VN                  FP   ]
Linha 1 (Real: 1)   [  FN                  VP   ]
```

Repare com atenção:
- A linha superior é a **Classe 0 (Negativa)**.
- A linha inferior é a **Classe 1 (Positiva)**.
- A diagonal principal (`[0,0]` e `[1,1]`) contém os **acertos** (VN e VP).
- A diagonal secundária (`[0,1]` e `[1,0]`) contém os **erros** (FP e FN).

```python
# Desempacotamento canônico no scikit-learn:
vn, fp, fn, vp = confusion_matrix(y_true, y_pred).ravel()
```

Se o código na questão fizer:
```python
# ERRO DE LÓGICA:
vp, fn, fp, vn = confusion_matrix(y_true, y_pred).ravel()  # ORDEM COMPLETAMENTE ERRADA!
```
O `ravel()` lê linha por linha e devolve **VN, FP, FN, VP**. Com a atribuição acima, as **quatro** variáveis ficam trocadas: `vp` recebe o VN, `fn` recebe o FP, `fp` recebe o FN e `vn` recebe o VP (testado no Python). Por isso nem a precisão nem o recall saem certos. O scikit-learn ordena as classes de forma crescente, então a classe 0 (negativa) vem primeiro.

---

## 3. `predict` vs `predict_proba`: O Erro Clássico da Curva ROC e AUC

Os modelos de classificação no scikit-learn (Regressão Logística, Random Forest, SVM com probabilidade ativada, etc.) oferecem dois métodos principais:
1. `model.predict(X_test)`: Retorna rótulos binários discretos (`0` ou `1`), aplicando internamente o limiar rígido padrão de 0,5.
2. `model.predict_proba(X_test)`: Retorna uma matriz com duas colunas de números decimais contínuos:
   - Coluna 0: Probabilidade de pertencer à Classe 0 (ex: 0,15).
   - Coluna 1: Probabilidade de pertencer à Classe 1 (ex: 0,85).

```python
# Exemplo de saída de predict_proba:
# [[0.90, 0.10],   -> Modelo quase convicto de que é Negativo
#  [0.20, 0.80],   -> Modelo convicto de que é Positivo
#  [0.45, 0.55]]   -> Modelo em dúvida, mas levemente inclinado a Positivo
```

### ⚠️ Erro de Lógica Clássico #2: Passar Rótulos Discretos para `roc_auc_score`
```python
# CÓDIGO COM ERRO DE LÓGICA GRAVE:
y_pred = model.predict(X_test)
auc = roc_auc_score(y_test, y_pred)  # ERRO CONCEITUAL!
```
- **Por que está errado?** A AUC mede a capacidade de ordenação contínua de probabilidades ao longo de todos os limiares. Ao passar `y_pred` (apenas 0 e 1), você reduz a curva ROC a poucos pontos: os extremos (0,0) e (1,1) e um único ponto operacional (o do limiar 0,5 embutido no `predict`). A AUC sai grosseira e menor (num teste nosso, 0,82 em vez de 0,92).
- **Forma Correta:**
```python
y_prob = model.predict_proba(X_test)[:, 1]  # Pega a probabilidade da classe 1
auc = roc_auc_score(y_test, y_prob)         # AUC contínua e precisa
```

---

## 4. Customização de Limiar (Threshold Tuning) no Código

Em problemas como detecção de fraudes ou doenças graves, manter o limiar fixo em 0,5 é inadequado porque precisamos priorizar o Recall.

Como ajustar o limiar no scikit-learn:
```python
# 1. Obter probabilidades contínuas da classe positiva
y_prob = model.predict_proba(X_test)[:, 1]

# 2. Aplicar limiar agressivo para capturar mais positivos (ex: 0.25 em vez de 0.50)
y_pred_sensivel = (y_prob >= 0.25).astype(int)

# Agora sim: calcular métricas com o novo y_pred customizado
rec = recall_score(y_test, y_pred_sensivel)
```

### ⚠️ Erro de Lógica Clássico #3: Esquecer de fatiar a coluna da classe positiva
```python
# ERRO DE CÓDIGO:
y_prob = model.predict_proba(X_test)  # Matriz com 2 colunas!
y_pred = (y_prob >= 0.25).astype(int) # Erro! Gera array com shape (N, 2), quebrando métricas
```

---

## 5. O `classification_report` e suas Médias: `macro`, `weighted`, `micro`

Quando lidamos com classes desbalanceadas:

```python
from sklearn.metrics import classification_report

print(classification_report(y_test, y_pred))
```

Ao interpretar o relatório no código:
1. **`accuracy`**: Não use se as classes forem desbalanceadas.
2. **`macro avg`**: Média simples não-ponderada. Se o modelo tiver F1 = 0,90 na classe majoritária e F1 = 0,10 na minoritária, o `macro avg` será (0,90 + 0,10) ÷ 2 = 0,50. Ele grita que o modelo falhou na classe rara!
3. **`weighted avg`**: Ponderada pelo suporte (tamanho da classe). Se a majoritária tiver 9.900 amostras e a minoritária 100, o `weighted avg` será dominado pela majoritária e continuará próximo de 0,90, mascarando o fracasso.

Em código com funções individuais:
```python
# CORRETO para dados desbalanceados multiclasse:
f1 = f1_score(y_test, y_pred, average='macro')

# CUIDADO com o default em multiclasse:
# Se omitir o average em problemas multiclasse, o scikit-learn lança exceção ValueError!
```

### ⚠️ Erro de Lógica Clássico #4: Aplicar o limiar sobre `predict`
```python
y_pred = model.predict(X_test)           # já é 0 ou 1
y_sens = (y_pred >= 0.20).astype(int)    # mesmos rótulos: o limiar não faz nada
```
O limiar só tem efeito sobre `predict_proba(X_test)[:, 1]`. E o limiar deve ser escolhido em dados de **validação**; escolher o melhor no teste e reportar essa nota é usar o teste para decidir (nota otimista).

---

## 5.1 `average=` em problemas com mais de duas classes

- Sem `average=`, `f1_score`, `precision_score` e `recall_score` com 3 classes levantam `ValueError` (padrão `'binary'`).
- `'micro'`: soma os acertos e erros de todas as classes; em multiclasse equivale à acurácia e **esconde** a classe rara.
- `'weighted'`: pondera pelo tamanho das classes; também é dominada pela maior.
- `'macro'`: média simples, mesmo peso para cada classe; revela a classe rara. `average=None` dá um valor por classe.

---

## 5.2 Ordem das ações e escolha da métrica

Ordem de uma avaliação confiável: **1) `train_test_split`, 2) `fit` só no treino, 3) `predict` no teste, 4) métricas com `y_test` e `y_pred`**. Ajustar o modelo (ou scaler) antes do split vaza o teste; medir no treino infla a nota; prever antes do `fit` dá `NotFittedError`.

A métrica vem do **custo do erro**: falso negativo caro (fraude, doença) pede **recall**; falso positivo caro pede **precisão**; base desbalanceada não aceita só acurácia (`cross_val_score` usa acurácia por padrão; troque com `scoring=`). Se o modelo só empata com o baseline que sempre chuta a classe majoritária (`DummyClassifier`, complemento fora dos slides), a acurácia não prova aprendizado.

---

## 6. Checklist de 5 Segundos para Questões de Código da Aula 7

Quando bater o olho em uma questão de código na prova:
1. **Verifique os argumentos e a leitura da matriz:** As métricas chamam `(y_true, y_pred)`? O `ravel()` vira `vn, fp, fn, vp`? Os eixos da ROC são X = fpr e Y = tpr?
2. **Verifique os dados:** As métricas foram calculadas com os dados de **TESTE** (`y_test`, `X_test`) ou usaram por engano os dados de treino (`y_train`)?
3. **Verifique a função da ROC-AUC:** Chamaram `predict_proba(X_test)[:, 1]` ou passaram `predict(X_test)` binário?
4. **Verifique o tipo de problema:** É classificação ou regressão? Usar `r2_score` ou `mean_squared_error` em problema de classificação com classes 0 e 1 é erro grosseiro de incompatibilidade!
5. **Verifique o equilíbrio de classes:** Se o enunciado diz que a base é 99% classe A e 1% classe B, aprovar o modelo usando apenas `accuracy_score` é erro conceitual gravíssimo.
6. **Verifique a ordem e o limiar:** o `fit` vem depois do split? O limiar foi aplicado sobre `predict_proba` e escolhido fora do teste? Em multiclasse, o `average=` esconde a classe rara?
