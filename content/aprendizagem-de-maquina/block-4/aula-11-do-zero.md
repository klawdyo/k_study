# Aula 11 do zero: Máquinas de Vetores de Suporte (SVM)

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e, quando dá, um exemplo numérico pequeno; depois vem o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção). Tudo que **não está nos 31 slides** da Aula 11 vem marcado como **[exemplo nosso]** ou **[complemento]**.

**A pergunta que a aula inteira responde:** *entre infinitas retas que separam duas classes, qual escolher, e o que fazer quando nenhuma reta separa?*

Analogia de software: pense em um **limite de aprovação** num sistema de crédito. Qualquer limite entre "bons" e "maus" pagadores que acerte o histórico serve; o SVM escolhe o que deixa **a maior folga** dos dois lados, para que um cliente ligeiramente diferente do histórico ainda caia do lado certo.

**Como o conteúdo foi conferido:** o texto extraído dos slides tem várias equações e figuras como imagem. Abri todas as imagens do arquivo da aula e descrevo abaixo só o que vi. Onde o slide e o hábito das bibliotecas (scikit-learn) divergem, as duas versões aparecem, com a indicação do que responder.

---

## Cobertura por slide

| Slide | Conteúdo do slide | Onde está nesta leitura |
| :-- | :-- | :-- |
| 1 | Capa (Introdução ao Aprendizado de Máquina, profa. Amanda Gondim) | Sem conteúdo técnico |
| 2 | Título: Máquina de Vetor de Suporte (SVM) | Sem conteúdo técnico |
| 3 | Definição: classificação e regressão; hiperplanos; linearmente separável | Seção 1 |
| 4 | Qual o melhor hiperplano? H1 no ponto médio; simetria; distância d | Seção 1 |
| 5 | Equação do hiperplano: β (vetor normal), x, β0 (figura com w e x) | Seção 2 |
| 6 | Vetores de suporte e margem (figura com d e linhas tracejadas) | Seção 4 |
| 7 | Três abordagens: máxima margem, vetores de suporte, SVM | Seção 5 |
| 8 | Classificador de máxima margem, margens rígidas; f(x)=β·X+β0 em imagem | Seções 2 e 5 |
| 9 | O que é um hiperplano (f(X)=β0+β1X1+...=0; figura com β1=0,8 e β2=0,6) | Seção 2 |
| 10 | Separando as classes: Yi=+1 e Yi=−1, Yi·f(Xi)>0 | Seção 3 |
| 11 | Hiperplano canônico: yi(w·xi+b)−1≥0 e abs(w·xi+b)=1 (só imagens) | Seção 4 |
| 12 | Em meio a tantos hiperplanos, qual escolher? (só figura) | Seção 1 |
| 13 | Máxima margem: maior corredor, otimização com restrições, margem rígida | Seção 5 |
| 14 | Classificador de vetor de suporte: permite pontos entre as margens | Seção 6 |
| 15 | C como parâmetro de tuning; variáveis de folga εi e seus três casos | Seção 6 |
| 16 | Influência do parâmetro C (figura de quatro painéis) | Seções 6 e 8 |
| 17 | Útil quando o limite é linear; limites não lineares aparecem | Seção 7 |
| 18 | SVM não linear: truque do kernel e hiperparâmetros | Seção 7 |
| 19 | Transformação não linear para dimensão maior (figura com kernel) | Seção 7 |
| 20 | Impossível separar perfeitamente: hiperparâmetros, soft e hard margin | Seções 7 e 8 |
| 21 | Parâmetro C: inverso da regularização; minimizar ½‖β‖² + C·Σεi | Seção 8 |
| 22 | Efeito de C alto e baixo; figura C=1, 10, 1000, 10000 | Seção 8 |
| 23 | Parâmetro Gamma: raio de influência; só no SVM não linear | Seção 9 |
| 24 | Efeito de Gamma alto e baixo; figura Gamma=0,01, 1, 100 | Seção 9 |
| 25 | Função lagrangeana, problema dual, produto interno (fórmulas em imagem) | Seção 10 |
| 26 | Problema dual com kernels: linear, polinomial, RBF, K(xi,xj) (imagens) | Seções 7 e 10 |
| 27 | Problemas multiclasse: one-vs.-one ou one-vs.-all | Seção 11 |
| 28 | one-vs.-one: pares, votos da maioria, exemplo (A,A,C) | Seção 11 |
| 29 | one-vs.-all: cada classe contra o resto, exemplo (B+C, A+C, C) | Seção 11 |
| 30 | Vantagens | Seção 12 |
| 31 | Desvantagens | Seção 12 |

**Resultado da cobertura:** 31 de 31 slides tratados (29 com conteúdo técnico; os slides 1 e 2 são capa). Os slides 11, 12, 25 e 26 têm o conteúdo quase todo em imagem; abri essas imagens e descrevo o que está desenhado. Todos os trechos de código das seções 2 a 13 foram executados com scikit-learn (os números impressos aparecem nos comentários).

---

## 1. O problema: qual reta escolher? (slides 3, 4 e 12)

### O que o slide 3 define

A **Máquina de Vetores de Suporte** (SVM, do inglês Support Vector Machine) é um algoritmo de aprendizagem de máquina usado para **classificação e também para regressão** (slide 3). Na prática, a aula trata da classificação.

O SVM procura a **melhor fronteira de separação** entre as classes, num conjunto de dados **linearmente separável**: aquele em que dá para separar completamente as classes com uma reta (2 atributos), um plano (3 atributos) ou, em geral, um **hiperplano**. O slide 3 diz que "as diversas fronteiras de separação possíveis" são chamadas de hiperplanos, e que o SVM busca o **melhor** deles.

Analogia: a lista de clientes "bons" e "maus" está num gráfico com dois atributos (por exemplo, renda e tempo de conta). Se existe uma linha reta com todos os bons de um lado e todos os maus do outro, os dados são linearmente separáveis.

### Qual é o melhor? (slide 4)

A figura do slide 4 mostra duas nuvens (sinais + em cima, sinais − embaixo) e **quatro retas candidatas**, H1 a H4. Vi que todas separam as duas nuvens: H1 (vermelha) passa no meio; H2 (verde) fica colada nos sinais +; H3 (azul) fica colada nos sinais −; H4 é horizontal e fica mais perto de um dos sinais −. Todas têm erro zero **nos dados de treino**; elas diferem na **folga**.

O slide 4 explica por que H1 é a melhor:

1. H1 está no **ponto médio** entre os dois grupos.
2. Há **simetria**: o ponto mais próximo de cada classe está à **mesma distância d** do hiperplano.
3. Isso **minimiza erros de classificação** e problemas de enviesamento do modelo, que o slide chama de overfitting.

O slide 12 repete a pergunta ("em meio a tantos hiperplanos possíveis, qual escolher?"). Vi dois gráficos de pontos azuis e roxos: no da esquerda, **três retas diferentes** separam as classes; no da direita, **uma só reta** foi escolhida e o fundo é pintado de cada cor para mostrar de que lado cai cada região.

**Exemplo nosso:** pense em um teste de regressão que passa com 100 casos. Se a fronteira passa a 0,01 do caso mais próximo, qualquer variação mínima em produção (outra máquina, outro sensor) vira erro. Se passa bem no meio, há margem para variação. É a ideia de **tolerância** (headroom) num limite de alarme: você não coloca o alarme colado no valor normal.

> **Se perguntarem na prova:** das várias retas que separam as classes, o SVM escolhe a que fica no ponto médio, com a mesma distância d até o ponto mais próximo de cada classe.

---

## 2. O que é um hiperplano e como se escreve (slides 5, 8 e 9)

### Dimensões e nomes

**[Complemento, não está nos slides]** O hiperplano tem uma dimensão a menos que o espaço dos dados: em 1 atributo a fronteira é um ponto; em 2 atributos, uma reta; em 3, um plano; em p atributos, um **hiperplano** (um "plano" em dimensão alta que não dá para desenhar). Para você, engenheiro: o hiperplano é só o conjunto de pontos em que uma **função linear dos atributos vale zero**.

### A equação (slides 5, 8 e 9)

Nos slides a função aparece escrita em imagens como f(x) = β·X + β0, e, no slide 9, expandida:

```
f(X) = β0 + β1·X1 + β2·X2 + ... + βp·Xp = 0      (slide 9, forma geral)
```

Leitura do slide 5, termo a termo:

| Símbolo | O que é (slide 5) | Analogia de software |
| :-- | :-- | :-- |
| β (vetor com β1, β2, ..., βp) | **Vetor normal**: define a orientação do hiperplano; é **perpendicular** a ele | Os pesos de uma soma ponderada dos atributos |
| x ou X (vetor com X1, ..., Xp) | Um ponto qualquer; se pertence ao hiperplano, satisfaz a equação | Uma linha da tabela de dados |
| β0 | Constante que determina o **deslocamento** do hiperplano em relação à origem; o slide diz que determina a regra de decisão | O valor constante (bias, offset) somado ao final |
| β·X | **Produto escalar** (slide 8): β1·X1 + β2·X2 + ... + βp·Xp | Um loop que soma peso × valor |

A figura do slide 5 mostra a reta H1 em vermelho com duas setas partindo da origem: a seta **w** (ou β) encosta na reta formando um **ângulo reto** (o desenho marca o símbolo de 90 graus) e a seta **x** vai da origem até um ponto da reta.

**Notação:** os slides usam β e β0 (livro de estatística) em quase todo lugar; a figura do slide 5 rotula a seta como w, o slide 11 usa w e b (w·x + b = 0) e o slide 13 usa M. Tudo é a mesma coisa: **β = w** (pesos) e **β0 = b** (bias). Em scikit-learn: `coef_` é w e `intercept_` é b.

### O exemplo do slide 9 (figura)

A figura do slide 9 mostra um hiperplano em 2D com β1 = 0,8 e β2 = 0,6 (legenda do gráfico) e três retas paralelas rotuladas **β1X1 + β2X2 − 6 = 0** (a fronteira, ou seja, β0 = −6), **= 1,6** e **= −4**. A seta vermelha β = (β1, β2) sai da origem e é perpendicular às retas; segmentos pontilhados ligam pontos verdes à reta. Duas figuras pequenas do slide 9 trazem o texto: "Se f(X) > 0: β·X + β0 > 0 → estamos de um lado; se f(X) < 0 → estamos do outro".

Leitura nossa: como (0,8)² + (0,6)² = 1, o vetor β tem comprimento 1, então o valor de f(X) coincide com a **distância com sinal** até a reta. Por isso as paralelas aparecem como "1,6" e "−4": a primeira está 1,6 unidade de um lado; a segunda, 4 unidades do outro. **[exemplo nosso]** Esse detalhe do "comprimento 1" é nossa leitura; o slide só mostra os rótulos.

### Exemplo numérico pequeno **[exemplo nosso]**: de que lado cai um ponto

Use dois atributos, w = (1, 1) e b = −4. A função de decisão é f(x) = 1·x1 + 1·x2 − 4. O hiperplano é a reta x1 + x2 = 4. Calcule f para alguns pontos:

| Ponto (x1, x2) | Conta | f(x) | Lado |
| :-- | :-- | :-- | :-- |
| (3, 3) | 3 + 3 − 4 | 2 | positivo (f > 0) |
| (1, 1) | 1 + 1 − 4 | −2 | negativo (f < 0) |
| (4, 1) | 4 + 1 − 4 | 1 | positivo, **exatamente** na linha da margem |
| (2, 2) | 2 + 2 − 4 | 0 | em cima do hiperplano (empate) |
| (0, 0) | 0 + 0 − 4 | −4 | negativo, bem longe |

Distância até o hiperplano = valor absoluto de f dividido pelo comprimento de w. Aqui ‖w‖ = √2 ≈ 1,414 (a raiz da soma dos quadrados: √(1² + 1²)). O ponto (1, 1) está a 2 / 1,414 ≈ 1,41 do hiperplano.

Código executado (python -I) que reproduz a tabela e mostra que `coef_` e `intercept_` são o w e o b:

```python
import numpy as np
from sklearn.svm import SVC

X = np.array([[3,2],[2,3],[5,4],[6,2],[2,1],[1,2],[0,1],[1,0]], float)
y = np.array([1,1,1,1,-1,-1,-1,-1])
m = SVC(kernel="linear", C=1e6).fit(X, y)
w, b = m.coef_[0], m.intercept_[0]
print(w, b)                              # [1. 1.] -4.0
for p in [[3,3],[1,1],[4,1],[2,2],[0,0]]:
    print(p, round(float(w @ np.array(p) + b), 3))   # 2.0 -2.0 1.0 0.0 -4.0
```

Analogia: f(x) é uma **pontuação** (score) que o modelo calcula. O sinal da pontuação é o rótulo que sai; o módulo diz o quão confiante (quão longe da fronteira) ele está.

> **Se perguntarem na prova:** β é o vetor normal (perpendicular ao hiperplano, define a orientação); β0 define o deslocamento em relação à origem; f(x) positivo é um lado, negativo é o outro, zero é a própria fronteira.

---

## 3. A regra de decisão e os rótulos +1 e −1 (slide 10)

No slide 10, as classes são codificadas assim:

- **Yi = +1** para os pontos em **azul**;
- **Yi = −1** para os pontos em **rosa**.

Depois, o slide conclui: **Yi · f(Xi) > 0 para todo i**. A figura do slide 10 mostra o plano dividido por uma reta: acima, "f(Xi) > 0, Yi = +1"; sobre a reta, "f(Xi) = 0"; abaixo, "Yi = −1, f(Xi) < 0".

Por que o produto fica positivo (os dois pequenos quadros do slide 10):

- Pontos azuis: f(Xi) > 0, vezes (+1), dá positivo.
- Pontos rosa: f(Xi) < 0, vezes (−1), dá positivo.

Ou seja, **um único teste serve para os dois lados**: o produto Yi · f(Xi) é positivo exatamente quando o ponto está do lado certo. Analogia: em vez de dois `if`, um para cada classe, o SVM multiplica pelo sinal esperado e testa `> 0`.

**Exemplo nosso:** (3, 2) é da classe +1 e tem f = 1, logo y·f = 1 (certo); (1, 2) é da classe −1 e tem f = −1, logo y·f = (−1)(−1) = 1 (certo).

Observação importante: os rótulos são **+1 e −1**, não 0 e 1. Nas bibliotecas você passa 0 e 1 ou texto, e elas convertem; a conta interna usa ±1.

> **Se perguntarem na prova:** a condição de classificação correta é Yi·f(Xi) > 0 para todo i, com Yi = +1 e Yi = −1.

---

## 4. Vetores de suporte e margem (slides 6 e 11)

### Definições do slide 6

- Os pontos **mais próximos do hiperplano** são os **vetores de suporte** (support vectors).
- É **a partir deles** que o modelo é desenvolvido matematicamente, treinado e otimizado.
- A distância entre os vetores de suporte e o hiperplano é chamada de **margem**.

A figura do slide 6 mostra a reta H1 sólida, **duas retas tracejadas** paralelas a ela, uma de cada lado, e setas marcadas **d** entre H1 e cada tracejada. Um sinal + e um sinal − destacados em verde ficam justamente **sobre as tracejadas**: são os vetores de suporte.

### O hiperplano canônico (slide 11)

O slide 11 é só imagens e uma legenda ("hiperplano canônico"). Vi: uma figura com a reta cheia **w·x + b = 0**, as tracejadas, os rótulos "Classe +1" e "Classe −1" e a seta w; a tracejada de baixo rotulada **H2: w·x + b = −1**; e três quadros de equação:

```
w·xi + b ≥ +1   se yi = +1
w·xi + b ≤ −1   se yi = −1
yi · (w·xi + b) − 1 ≥ 0, para todo (xi, yi)
e os vetores de suporte satisfazem: abs(w·xi + b) = 1
```

Tradução: depois de escolher a **escala** de w e b, as duas tracejadas ficam em f = +1 e f = −1, e **nenhum ponto de treino cai entre elas**. Os vetores de suporte são os pontos com f exatamente +1 ou −1.

**Exemplo nosso (seção 2):** com w = (1, 1) e b = −4, os pontos (3, 2) e (2, 3) têm f = +1 e os pontos (2, 1) e (1, 2) têm f = −1. São os quatro vetores de suporte, e foi o próprio scikit-learn que os apontou (`support_vectors_`). Já (5, 4) tem f = 5 e (6, 2) tem f = 4: estão longe, e não são vetores de suporte.

```python
import numpy as np
from sklearn.svm import SVC

X = np.array([[3,2],[2,3],[5,4],[6,2],[2,1],[1,2],[0,1],[1,0]], float)
y = np.array([1,1,1,1,-1,-1,-1,-1])
m = SVC(kernel="linear", C=1e6).fit(X, y)
print(m.support_vectors_.tolist())        # [[2,1],[1,2],[3,2],[2,3]]
print((y * (X @ m.coef_[0] + m.intercept_[0])).round(2))   # [1 1 5 4 1 1 3 3]

# movendo pontos distantes, nada muda
X2 = X.copy(); X2[2] = [9, 9]; X2[3] = [7, 5]
m2 = SVC(kernel="linear", C=1e6).fit(X2, y)
print(m2.coef_[0], m2.intercept_[0])      # [1. 1.] -4.0  (igual)
```

### Por que só eles importam

Esta é a ideia mais perguntada. Se você **apagar ou mover** qualquer ponto que está longe das tracejadas (como o (5, 4) acima), o hiperplano **não muda**. O código acima mostrou isso: movi (5, 4) para (9, 9) e (6, 2) para (7, 5) e w e b ficaram idênticos. Se mover um vetor de suporte, a reta muda. Analogia: numa ponte apoiada em pilares, só os pilares seguram o peso; remover um ponto qualquer do tabuleiro não muda onde ficam os pilares.

O slide 30 usa essa propriedade para dizer que o SVM é **robusto a outliers**: o algoritmo é otimizado a partir dos vetores de suporte, pontos próximos ao hiperplano, e por isso não é muito influenciado por ruídos distantes. **Cuidado**: um outlier que cai **perto da fronteira** vira vetor de suporte e influencia muito; a robustez é para pontos longe dela (leitura nossa, ligada à seção 6).

### Margem: duas definições, uma só ideia

- No **slide 6**, margem é a **distância entre os vetores de suporte e o hiperplano** (cada um dos dois d).
- No **slide 13**, buscamos "maior distância entre as margens das duas classes", o **corredor** inteiro (largura M).
- No exemplo: cada lado tem distância 1/‖w‖ ≈ 0,707 e o corredor tem 2/‖w‖ ≈ 1,414 (o slide 25 escreve exatamente "2/‖β‖"; ver seção 5).

> **Se perguntarem na prova:** se a questão pedir a definição do slide 6, responda "distância entre os vetores de suporte e o hiperplano"; se falar em largura do corredor, é o dobro disso (2d). Vetores de suporte = pontos mais próximos do hiperplano, que determinam o modelo.

**[Complemento do material Gyl]** O arquivo `Aula SVM .pdf` (outro professor) confirma as retas de margem **w·x + b = +1** (margem positiva) e **w·x + b = −1** (margem negativa), como no slide 11. Esse material é só referência.

---

## 5. Máxima margem e margem rígida (slides 7, 8, 13 e 25)

### As três abordagens (slide 7)

O slide 7 lista a trilha em três passos, do mais simples ao mais completo. Guarde a ordem:

```
1. Classificador de Máxima Margem       (margem rígida, dados separáveis)
2. Classificador de Vetores de Suporte   (margem suave, tolera erros; seção 6)
3. Máquinas de Vetores de Suporte        (kernels, fronteira não linear; seção 7)
```

Analogia: é o caminho de um sistema real. Primeiro a versão ideal (dados limpos), depois a versão que tolera sujeira, por fim a versão que lida com problemas que não são lineares.

### Máxima margem (slides 8 e 13)

- **Slide 8:** "as SVMs lineares com **margens rígidas** definem fronteiras lineares a partir de dados linearmente separáveis".
- **Slide 13:** "Dentre todos os hiperplanos, buscamos aquele que apresenta **maior distância entre as margens** (M) das duas classes. **Maximizar a largura do corredor**." É um **problema de otimização com restrições**. **Margem rígida: todos os pontos fora da margem.**

A figura do slide 13 mostra um **corredor** inclinado entre pontos azuis (de um lado) e roxos (do outro), com setas de cada ponto mais próximo até a reta do meio.

Analogia: otimização com restrição é "ache o melhor valor sob regras que não podem ser violadas". Aqui, melhor = corredor mais largo; regra = nenhum ponto pode estar dentro do corredor nem do lado errado. É como um escalonador que maximiza uma folga respeitando prazos obrigatórios.

### As duas escritas matemáticas (cuidado: o símbolo M muda de papel)

O **slide 13** (em imagem) escreve o problema no estilo do livro de estatística: encontrar β0, β1, ..., βp que maximizem **M**, sujeito a Σβj² = 1 e a yi·(β0 + β1·xi1 + ... + βp·xip) ≥ M para todo i. Com a soma dos quadrados fixada em 1, o valor M **é a própria distância** de cada lado até o hiperplano.

O **slide 25** (em imagem, "Para os classificadores de margem rígida tem-se") escreve:

```
Max M = 2 / ‖β‖ = Min ‖β‖² / 2 = Min βᵀβ / 2        sujeito a: yi · (βᵀXi + β0) ≥ 1
```

Aqui **M é a largura total do corredor** (2/‖β‖) e a restrição usa 1 no lugar de M. As duas escritas descrevem o mesmo problema com normalizações diferentes.

Por que "maximizar a margem" vira "minimizar o tamanho de β": a largura 2/‖β‖ cresce quando ‖β‖ diminui. Minimizar ‖β‖²/2 é só uma versão mais fácil de resolver (derivável, "uma tigela" com um único mínimo).

**Exemplo nosso:** na seção 2, w = (1, 1) tem ‖w‖ = 1,414 e largura 2/1,414 = 1,414. Um w = (2, 2) (com b = −8) teria largura 0,707, metade; o SVM prefere o w **menor** que ainda cumpre yi·f ≥ 1 em todos os pontos.

### Limite da margem rígida

O slide 13 diz "todos os pontos fora da margem". Se os dados **não são** separáveis por uma reta, **não existe** solução; e, se existe só por pouco (um ponto fora do lugar), a margem encolhe muito para acomodar esse ponto. Isso leva à próxima etapa.

**Exemplo nosso** (código executado): ao adicionar um ponto negativo (3,2; 1,4) ao conjunto da seção 2, a margem rígida (C enorme) sai com w = (1; 3,67) e largura 0,53: o corredor ficou uma lasca para encaixar esse único ponto.

```python
import numpy as np
from sklearn.svm import SVC

X = np.array([[3,2],[2,3],[5,4],[6,2],[2,1],[1,2],[0,1],[1,0],[3.2,1.4]])
y = np.array([1,1,1,1,-1,-1,-1,-1,-1])
for C in [0.01, 0.1, 1, 10, 1e6]:
    m = SVC(kernel="linear", C=C).fit(X, y)
    w = m.coef_[0]
    print(C, round(2/np.linalg.norm(w), 3), int(m.n_support_.sum()), round(m.score(X, y), 3))
# C      largura  n_SV  acerto no treino
# 0.01    18.182    8    0.556
# 0.1      4.192    6    0.778
# 1        1.313    4    1.0
# 10       0.526    3    1.0
# 1e6      0.526    3    1.0
```

> **Se perguntarem na prova:** margem rígida (hard margin) = nenhum ponto pode estar dentro da margem nem do lado errado; só funciona com dados linearmente separáveis; maximizar a largura do corredor equivale a minimizar ‖β‖ (slide 25: Max M = 2/‖β‖ = Min ‖β‖²/2).

---

## 6. Margem suave: variáveis de folga e o parâmetro C (slides 14, 15 e 16)

### A ideia (slide 14)

O **classificador de vetor de suporte** **permite pontos entre as margens** (slide 14). Em vez de exigir perfeição, aceita que alguns pontos violem a margem, e até que alguns fiquem do lado errado, em troca de uma margem melhor para o resto.

Analogia: um linter com **tolerância**. Se qualquer aviso quebra o build (regra rígida), o projeto real nunca passa. Com tolerância (warnings permitidos), o build passa e você controla quantos avisos aceita.

### A formulação do slide 14 (imagem)

```
maximizar M sobre β0, β1, ..., βp, ε1, ..., εn
sujeito a:   Σ βj² = 1
             yi · (β0 + β1·xi1 + ... + βp·xip)  ≥  M · (1 − εi)      ("violação da margem")
             εi ≥ 0   e   Σ εi ≤ C
```

O texto "violação da margem" aparece escrito sob o termo M(1 − εi). Sem a folga (εi = 0), volta a restrição rígida de M.

### As variáveis de folga e seus três casos (slide 15)

O slide 15: **C é o parâmetro de tuning: decide o quanto aceitamos errar. Os εi são as variáveis de folga (slack).**

| Valor de εi | O que o slide 15 diz | Em português claro |
| :-- | :-- | :-- |
| εi = 0 | A i-ésima observação está no lado correto da margem | Ponto perfeito, fora do corredor, lado certo |
| 0 < εi ≤ 1 | Está no lado **errado da margem** | Entrou no corredor, mas ainda do lado certo do hiperplano (o slide distingue este caso do seguinte, que é "lado errado do hiperplano") |
| εi > 1 | Está no lado **errado do hiperplano** | Cruzou a reta e é **classificado errado** |

A figura do slide 15 numera doze pontos (1 a 12), com a reta cheia e duas tracejadas; alguns pontos ficam entre as tracejadas e alguns passam da reta.

**Exemplo nosso (unidades canônicas, restrição yi·f(xi) ≥ 1 − εi):** no conjunto da seção 5, se mantivermos a reta w = (1, 1), b = −4, o ponto negativo (3,2; 1,4) dá f = 3,2 + 1,4 − 4 = 0,6, positivo, ou seja, do lado errado. Como o rótulo é −1, y·f = −0,6, e a folga necessária é εi = 1 − (−0,6) = 1,6, maior que 1: do lado errado do hiperplano. Já um ponto positivo com f = 0,5 teria y·f = 0,5 e εi = 0,5: dentro do corredor, mas do lado certo.

### O que C faz nesta formulação do slide 14/15

No slide 14, a restrição **Σ εi ≤ C** faz do C um **orçamento de violações**: quanto total de folga aceitamos. Já no slide 21 (seção 8), o C é um **peso de penalidade**. Os dois usos têm sentidos **opostos**. Veja a seção 8 e a tabela de divergências (seção 15).

### Figura do slide 16 (influência de C)

O slide 16 reaproveita a figura do slide 14: **quatro painéis** com o mesmo conjunto de pontos azuis e roxos, cada um com uma reta cheia e duas tracejadas. Do primeiro ao quarto painel **as tracejadas ficam cada vez mais próximas** (a margem estreita). O slide não rotula qual valor de C vale em cada painel. **[Complemento, a verificar]** Essa figura parece vir de um livro que usa C como orçamento (forma do slide 14), em que um C maior dá margem **maior**; isso é o contrário da convenção do slide 21. Para a prova, use a seção 8 (convenção do slide 21 e 22).

> **Se perguntarem na prova:** os εi são as variáveis de folga: 0 = lado correto da margem; entre 0 e 1 = lado errado da margem (dentro dela); maior que 1 = lado errado do hiperplano. O C decide o quanto se aceita errar.

---

## 7. Quando uma reta não basta: SVM não linear e o truque do kernel (slides 17, 18, 19, 20 e 26)

### O problema (slide 17)

O slide 17 diz que o classificador de vetor de suporte **é útil quando o limite entre as classes é linear**, mas em problemas reais **frequentemente temos limites não lineares**. A figura: à esquerda, pontos azuis nas duas pontas de uma diagonal e pontos roxos no meio; à direita, o mesmo gráfico com uma reta (e margens tracejadas) atravessando a nuvem: **a reta falha**, pois mistura as classes.

**Exemplo nosso (código executado):** duas circunferências concêntricas (círculo de dentro de uma classe, anel de fora de outra). Com kernel linear, o acerto no teste foi 51% (moeda); com RBF, 99%.

(O código está na seção 9, que usa o mesmo conjunto de dados.)

### O que o slide 18 promete

A teoria do SVM parte de classes linearmente separáveis, mas isso **não limita o uso** a esses problemas. Para casos mais complexos foram desenvolvidas técnicas que formam o **SVM não linear**: o **truque do kernel (kernel trick)** e a introdução de **hiperparâmetros** para flexibilizar o modelo.

### A ideia da transformação (slide 19)

O slide 19: o truque aplica uma **transformação não linear do espaço**, por meio de uma função, **mapeando os dados para um espaço de maior dimensão** onde é possível obter um **hiperplano** que separa as classes. Ao **voltar ao espaço original**, a fronteira aparece **não linear**.

A figura do slide 19: à esquerda, quadrados vermelhos no centro cercados por círculos verdes (impossível separar com uma reta); uma seta rotulada "kernel"; à direita, os mesmos pontos em 3D, com os vermelhos no alto de uma "montanha" e os verdes na base, e um **plano rotulado "Decision surface"** passando entre eles.

Analogia: dados que parecem embolados em uma tabela de 2 colunas podem ficar separáveis se você **criar uma coluna nova**, calculada a partir das antigas. Em engenharia de atributos, isso é criar uma feature derivada. O SVM com kernel faz isso **sem criar a coluna de fato** (próxima subseção).

### Exemplo numérico em 1D: a parábola **[exemplo nosso]**

Pontos numa linha: **classe +** em x = −1, 0, +1; **classe −** em x = −3 e x = +3. Nenhum ponto de corte (um valor de x) separa, porque a classe + está entre as duas negativas.

Crie uma segunda coluna x² (transformação φ(x) = (x, x²)):

| x | x² (nova coluna) | classe |
| :-- | :-- | :-- |
| −1 | 1 | + |
| 0 | 0 | + |
| 1 | 1 | + |
| −3 | 9 | − |
| 3 | 9 | − |

Agora uma reta **horizontal x² = 5** separa tudo: os + ficam em x² ≤ 1 e os − em x² = 9. Voltando ao eixo original, x² = 5 corresponde a dois cortes (x = ±2,24): uma fronteira **não linear** (dois pontos) vinda de uma separação **linear** no espaço novo. O mesmo efeito do slide 19, em miniatura. O scikit-learn confirma: com φ explícito, o SVM linear acerta 100%; sem φ, só 60%; com kernel RBF direto nos dados originais, 100%.

```python
import numpy as np
from sklearn.svm import SVC

x = np.array([-1, 0, 1, -3, 3]); y = np.array([1, 1, 1, -1, -1])
Z = np.c_[x, x**2]
print(SVC(kernel="linear", C=1e6).fit(Z, y).score(Z, y))                    # 1.0
print(SVC(kernel="linear", C=1e6).fit(x.reshape(-1,1), y).score(x.reshape(-1,1), y))   # 0.6
print(SVC(kernel="rbf", gamma=1, C=1e6).fit(x.reshape(-1,1), y).score(x.reshape(-1,1), y))  # 1.0
```

### O truque em si: o que o kernel calcula (slides 18, 19 e 26)

O slide 18 cita o "truque do kernel"; o slide 26 mostra o **problema dual** em que ele aparece (a última equação do slide troca o termo xiᵀxj por **K(xi, xj)**, em vermelho). A explicação a seguir é o que isso quer dizer.

- Sem o truque: transformar cada ponto para um espaço de muitas dimensões e depois calcular produtos internos. Se o espaço novo tem milhões de dimensões (ou infinitas, como no RBF), o custo explode.
- Com o truque: uma **função K(xi, xj)**, o **kernel**, devolve **diretamente** o produto interno no espaço novo, usando só as coordenadas originais.

Analogia de software: uma **função que retorna o resultado sem executar o processo caro**, como calcular um hash ou uma soma fechada em vez de iterar. O espaço de alta dimensão existe só "em teoria".

**[Complemento do material Gyl, e verificado por nós em código]** O PDF Gyl (`Aula SVM .pdf`, página 24) traz um exemplo parecido: pontos 2D xi = (2, 3) e xj = (4, 5), kernel polinomial (xi·xj + 1)². Produto escalar 2·4 + 3·5 = 23; mais 1 dá 24; ao quadrado dá **576**. O mesmo valor sai se transformarmos explicitamente cada ponto em 6 coordenadas, φ(v) = (1, √2·v1, √2·v2, v1², √2·v1·v2, v2²), e fizermos o produto escalar: 576. Ou seja, o kernel obteve em 3 contas o que exigiria 6 coordenadas por ponto.

```python
import numpy as np
a, b = np.array([2, 3]), np.array([4, 5])
K = (a @ b + 1) ** 2
phi = lambda v: np.array([1, np.sqrt(2)*v[0], np.sqrt(2)*v[1], v[0]**2, np.sqrt(2)*v[0]*v[1], v[1]**2])
print(K, round(float(phi(a) @ phi(b)), 6))     # 576 576.0
```

### Os kernels que aparecem nos slides (slide 26, imagens)

O slide 26 mostra o problema dual com três kernels, cada um em uma caixa azul:

| Kernel | Fórmula escrita no slide 26 | Em palavras |
| :-- | :-- | :-- |
| Linear | xiᵀ xj | Produto escalar puro: fronteira reta |
| Polinomial | (xiᵀ xj + 1) elevado a d | Combinações polinomiais de grau d |
| Função de base radial (RBF) | e elevado a (−γ ‖xi − xj‖²) | Similaridade que cai com a distância; é a que tem γ |

O slide 23 cita ainda o kernel **sigmoide** ao dizer onde o Gamma é introduzido ("RBF, polinomial e sigmoide"), mas **a fórmula do sigmoide não está nos slides**. **[Complemento]** Em scikit-learn, as opções de `kernel` são `linear`, `poly`, `rbf` e `sigmoid`; o `poly` do scikit-learn também usa γ e um termo r, enquanto o slide escreve (xiᵀxj + 1)ᵈ sem γ. Na prova, use o que o slide escreve.

Cálculo para fixar a ideia do RBF **[exemplo nosso]**: com a = (2, 3) e b = (4, 5), a distância ao quadrado é 8. Com γ = 1, K = e⁻⁸ ≈ 0,0003 (quase zero: "pontos distantes não se influenciam"). Com γ = 0,1, K = e⁻⁰·⁸ ≈ 0,45 (ainda há influência). O kernel de um ponto com ele mesmo vale 1. Isso antecipa o papel do γ na seção 9.

### Quando nem o kernel resolve (slide 20)

O slide 20 admite: "em algumas situações é impossível" achar uma reta que separe perfeitamente, e às vezes **o problema persiste mesmo após o kernel**. Nesses casos **os hiperparâmetros** (C e Gamma) é que dão versatilidade: ou o modelo **tolera que algumas amostras sejam classificadas erradas (soft margin)** ou **tenta a separação perfeita (hard margin)**.

As figuras do slide 20 mostram os mesmos pontos (círculos pretos e quadrados azuis) em dois painéis: no de cima, uma **reta** inclinada em vermelho; no de baixo, uma **linha verde quebrada** (poligonal) contornando os pontos, ou seja, uma fronteira bem mais complexa para tentar acertar tudo.

> **Se perguntarem na prova:** o SVM não linear usa o truque do kernel: mapeia os dados para uma dimensão maior onde um hiperplano separa; de volta ao espaço original, a fronteira é não linear. O kernel calcula o produto interno sem transformar explicitamente os pontos. Quando nem isso basta, C e Gamma flexibilizam o modelo (soft margin) ou forçam a separação (hard margin).

---

## 8. O hiperparâmetro C (slides 21 e 22)

### O que o slide 21 afirma

O **parâmetro C**:

- está presente **tanto no SVM linear quanto no não linear**;
- controla **o quão tolerante a erros de classificação** será o modelo;
- na maioria das bibliotecas de ML (o slide cita o SVM e a Regressão Logística), C é um parâmetro de **regularização**, e **por convenção C é sempre o inverso da força de regularização**;
- **C pequeno: a penalidade por errar é pequena; C grande: a penalidade por errar é altíssima**.

A imagem do slide 21 traz a função objetivo: **Minimizar ½‖β‖² + C · Σ εi**. Ela tem duas partes em disputa: ½‖β‖² (quer margem larga) e C·Σεi (penaliza as violações). C é o **peso** da segunda parte.

Analogia: C é a **multa por falha**. Multa grande (C grande): o sistema evita qualquer falha, mesmo à custa de uma configuração complicada. Multa pequena: aceita algumas falhas para manter tudo simples.

### O que o slide 22 afirma

- **C alto:** o algoritmo busca a separação completa das classes, mesmo em problemas complexos; pode causar **overfitting** e **demandar muito tempo de treinamento**, porque gera **fronteiras de decisão muito complexas**.
- **C baixo:** flexibiliza o treinamento e permite fronteiras **com erros (soft margin)**; pode levar a **underfitting**.

A figura do slide 22: quatro gráficos de pontos vermelhos (classe −1) e azuis (classe +1) com a fronteira colorida, rotulados **C = 1, C = 10, C = 1000 e C = 10000**. Com C = 1 a fronteira é uma curva suave e há muitos pontos do lado errado; com C = 10000 as regiões viram blocos quase retangulares que tentam acertar quase todo ponto.

### Tabela de C (resume os slides 21 e 22, mais nossas leituras marcadas)

| Característica | C pequeno | C grande |
| :-- | :-- | :-- |
| Penalidade por errar (slide 21) | Pequena | Altíssima |
| Fronteira (slide 22) | Permite erros, soft margin | Busca separação completa, fronteira complexa |
| Risco (slide 22) | Underfitting | Overfitting e treino demorado |
| Largura da margem (nossa leitura da função objetivo) | Larga | Estreita |
| Nº de vetores de suporte (exemplo nosso, seção 5) | Muitos | Poucos |
| Relação com a regularização (slide 21) | Muita regularização | Pouca regularização |

**Números do nosso exemplo (seção 5):** C = 0,01 → margem 18,2 e 8 vetores de suporte (todos); C = 10 → margem 0,53 e 3 vetores de suporte. A margem **encolhe** quando C cresce, e o número de vetores de suporte também cai.

**Exemplo com kernel RBF em dados ruidosos (luas, código executado):** C = 0,001 usa os 210 pontos de treino como vetores de suporte e acerta 80% no teste; C = 1 acerta 89%; C = 1000 também 89% (aqui o excesso de C pouco prejudicou, porque o γ estava moderado). O estrago aparece quando C e γ crescem juntos: C = 1000 e γ = 100 dá 100% no treino e **83% no teste** (overfitting); C = 0,001 e γ = 0,01 dá 80% no treino e 76% no teste (underfitting).

```python
from sklearn.svm import SVC
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

X, y = make_moons(n_samples=300, noise=0.35, random_state=1)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for C, g in [(0.001, 1), (1, 1), (1000, 1), (1000, 100), (0.001, 0.01)]:
    m = SVC(kernel="rbf", gamma=g, C=C).fit(Xtr, ytr)
    print(C, g, round(m.score(Xtr, ytr), 3), round(m.score(Xte, yte), 3), int(m.n_support_.sum()))
# 0.001 1    0.848 0.8   210
# 1     1    0.857 0.889 84
# 1000  1    0.886 0.889 73
# 1000  100  1.0   0.833 181
# 0.001 0.01 0.805 0.756 210
```

> **Se perguntarem na prova:** C grande → penaliza muito os erros → margem estreita, fronteira complexa, risco de overfitting e treino lento; C pequeno → tolera erros (soft margin) → risco de underfitting. C é o inverso da força de regularização. **Cuidado com a divergência:** a restrição Σεi ≤ C dos slides 14 e 15 trata C como orçamento de erros (efeito oposto); para as questões sobre efeito de C, valem os slides 21 e 22.

---

## 9. O hiperparâmetro Gamma (slides 23 e 24)

### Slide 23

- O **Gamma é introduzido somente no SVM não linear**, por meio das funções de kernel (o slide cita **RBF, polinomial e sigmoide**). O SVM linear não tem Gamma.
- "Enquanto o C controla a folga da margem, o Gamma controla **o raio de influência de cada ponto individual** no treinamento."
- Pode ser visto como uma forma de flexibilizar o treinamento, ao influenciar a **distância até onde as amostras são consideradas** para o cálculo da fronteira.
- São **pesos aplicados à distância entre amostras**, dando maior ou menor importância a amostras distantes ou próximas da fronteira.

Esse é exatamente o γ da fórmula do RBF do slide 26: e^(−γ‖xi − xj‖²). Quanto maior o γ, mais rápido o kernel cai com a distância (ver o cálculo da seção 7).

Analogia: γ é o **raio de busca** de um algoritmo de vizinhança (por exemplo, "considere só clientes a até X km"). Raio pequeno: cada ponto só vale para o vizinho imediato. Raio grande: cada ponto influencia todo mundo.

### Slide 24

- **Aumentar Gamma:** pontos mais distantes da região de separação passam a ser **desconsiderados**; fronteiras **mais restritas e complexas (overfitting)**.
- **Gamma menor:** aumenta a influência dos pontos distantes e **flexibiliza** a região de separação, permitindo alguns erros; pode levar a **underfitting**.

Figura do slide 24: três painéis com pontos vermelhos (−1) e azuis (+1), rotulados **Gamma = 0,01, Gamma = 1 e Gamma = 100**. Vi: com 0,01 a fronteira é quase uma reta, suave; com 1 é uma curva em duas "bolhas"; com 100 a região vermelha vira **ilhas pequenas** em volta de cada aglomerado de pontos vermelhos, e o resto é azul.

### Tabela de Gamma

| Característica | Gamma pequeno | Gamma grande |
| :-- | :-- | :-- |
| Raio de influência de cada ponto (slide 23) | Grande (alcança pontos distantes) | Pequeno (só vizinhos próximos) |
| Pontos distantes (slide 24) | Influenciam | São desconsiderados |
| Fronteira (slide 24) | Mais flexível e suave | Mais restrita e complexa |
| Risco (slide 24) | Underfitting | Overfitting |

**Números do nosso exemplo (círculos, código executado, RBF com C = 1):**

| Gamma | Acerto no treino | Acerto no teste | Pontos de suporte (de 210) |
| :-- | :-- | :-- | :-- |
| 0,01 | 0,667 | 0,578 | 210 |
| 1 | 1,000 | 0,989 | 45 |
| 100 | 1,000 | 0,956 | 172 |
| 1000 | 1,000 | 0,778 | 208 |

Leitura: com γ muito pequeno o modelo não aprende a forma (underfitting: treino e teste ruins); com γ muito grande acerta 100% no treino, mas o teste despenca (overfitting); γ = 1 está no meio. Quando γ cresce, **quase todo ponto vira vetor de suporte** (cada um vale só para si).

```python
from sklearn.svm import SVC
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split

X, y = make_circles(n_samples=300, noise=0.12, factor=0.4, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for k in ["linear", "rbf"]:                      # seção 7: linear 0.59 0.511 / rbf 1.0 0.989
    m = SVC(kernel=k).fit(Xtr, ytr)
    print(k, round(m.score(Xtr, ytr), 3), round(m.score(Xte, yte), 3))
for g in [0.01, 1, 100, 1000]:                   # tabela desta seção
    m = SVC(kernel="rbf", gamma=g, C=1).fit(Xtr, ytr)
    print(g, round(m.score(Xtr, ytr), 3), round(m.score(Xte, yte), 3), int(m.n_support_.sum()))
```

### C e Gamma juntos (leitura nossa a partir dos slides 22 e 24)

- C alto e γ alto: os dois empurram para fronteira complexa, risco máximo de **overfitting**.
- C baixo e γ baixo: os dois empurram para fronteira simples, risco de **underfitting**.
- O slide 31 avisa: "escolhas indevidas dos valores de C e Gamma podem levar facilmente a overfitting"; por isso se testam várias combinações (seção 13: busca em grade com validação cruzada, **[complemento]**).

> **Se perguntarem na prova:** Gamma só existe no SVM não linear (kernels); controla o raio de influência de cada ponto. Gamma alto: fronteira complexa, overfitting. Gamma baixo: fronteira flexível/suave, underfitting. Não confundir com C: C controla a folga da margem; Gamma controla o alcance de cada ponto.

---

## 10. Função lagrangeana, problema dual e produto interno (slides 25 e 26)

**Aviso de proporção:** os slides 25 e 26 só citam esses nomes e mostram as fórmulas em imagem; **a professora não detalha as contas**. Para a prova, entenda o **papel** de cada peça. Descrevo só as fórmulas que vi.

### O que está no slide 25

O texto do slide lista: **Função Lagrangeana**, **Problema Dual**, **Produto interno**. Nas imagens:

```
Margem rígida:  Max M = 2/‖β‖ = Min ‖β‖²/2 = Min βᵀβ/2
                sujeito a:  yi · (βᵀXi + β0) ≥ 1

Lagrangeana:    L(β, β0) = βᵀβ/2  −  Σ αi · [ yi·(βᵀXi + β0) − 1 ]      (soma de i = 1 até n)

Dual:           Max  Σ αi  −  ½ · Σ Σ αi·αj·yi·yj · (xiᵀ xj)
                sujeito a:  Σ αi·yi = 0
```

### O que muda no slide 26

O slide 26 repete o **problema dual** três vezes, mudando só o **termo de produto entre os pontos**:

```
Linear:        ... yi·yj · (xiᵀ xj)
Polinomial:    ... yi·yj · (xiᵀ xj + 1)^d
RBF:           ... yi·yj · exp(−γ ‖xi − xj‖²)
Geral:         Max Σ αi − ½ Σ Σ αi·αj·yi·yj · K(xi, xj)      sujeito a  Σ αi·yi = 0
```

A versão final troca xiᵀxj por **K(xi, xj)**, destacado em vermelho: a mensagem do slide é "para trocar o kernel, só mude K".

### Em português simples

1. **Primal** (o problema original, seção 5): achar β e β0 que dão a maior margem. Variáveis: uma por atributo.
2. **Lagrangeana**: ferramenta matemática que **incorpora as restrições** (todos os pontos do lado certo) à função a minimizar, atribuindo a cada ponto de treino um número αi (multiplicador de Lagrange).
3. **Dual**: o mesmo problema reescrito com os αi como variáveis. Variáveis: uma por **ponto de treino**.
4. **Produto interno**: no dual, os atributos aparecem **só** na forma xiᵀxj (produto entre dois pontos). Por isso dá para **substituir** esse produto por K(xi, xj): é aí que o truque do kernel entra, **sem mexer no resto do algoritmo**.

Analogia: o dual é uma **refatoração**: o algoritmo deixa de depender dos dados brutos e passa a depender só de "quão parecidos são os pares de pontos"; a função de similaridade (o kernel) vira uma interface que se pode trocar.

**[Complemento, não está nos slides]** Dois fatos de livro que explicam por que a aula fala em vetores de suporte: (1) quase todos os αi saem **zero**; só os pontos que tocam a margem (ou a violam) têm αi positivo, e eles são os vetores de suporte; (2) na margem suave o dual ganha o limite 0 ≤ αi ≤ C. Os slides não escrevem nenhuma das duas coisas; se a questão da prova só pedir "o que é o produto interno no dual", a resposta é: o que permite trocar xiᵀxj por K(xi, xj).

> **Se perguntarem na prova:** o problema dual usa apenas produtos internos entre pares de amostras; por isso se pode substituir o produto interno por uma função de kernel K(xi, xj) (truque do kernel). A função lagrangeana incorpora as restrições com multiplicadores αi.

---

## 11. Problemas multiclasse (slides 27, 28 e 29)

### Slide 27

O SVM resolve em essência problemas **binários**. Para mais de duas classes, existem técnicas que dividem o problema em várias classificações binárias, e valem para **diferentes algoritmos** (não só SVM). As duas mais comuns: **one-vs.-one** (um contra um) e **one-vs.-all** (um contra todos).

### Um contra um (slide 28)

- Separa o problema em classificações binárias **de pares de classes diferentes** e decide por **votos da maioria**.
- Com três classes A, B e C: classificadores **(A, B), (A, C) e (B, C)**; a classe mais votada vence.
- Exemplo do slide: o SVM escolheu A em (A, B), A em (A, C) e C em (B, C). Resultado **(A, A, C)** → a classe escolhida é **A**.

### Um contra todos (slide 29)

- **Compara cada classe com todo o resto.**
- Com três classes: **(A, B+C), (B, A+C) e (C, A+B)**; a classe que "ganhar do resto" é a escolhida.
- Exemplo do slide: o SVM escolheu B+C em (A, B+C), A+C em (B, A+C) e C em (C, A+B). Resultado **(B+C, A+C, C)** → a classe escolhida é **C**. Entenda: nos dois primeiros, a classe isolada **perdeu** (o vencedor foi o bloco "resto"); só no terceiro a classe isolada (C) venceu.

### Contagem de classificadores **[complemento, matemática simples]**

| Nº de classes K | Um contra um: K·(K−1)/2 | Um contra todos: K |
| :-- | :-- | :-- |
| 3 | 3 | 3 |
| 4 | 6 | 4 |
| 10 | 45 | 10 |

Com 3 classes os dois dão 3, e isso engana na prova: com 10 classes a diferença aparece (45 contra 10). Executado com o conjunto de dígitos (10 classes):

```python
from sklearn.datasets import load_digits
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
from sklearn.svm import SVC

X, y = load_digits(return_X_y=True)
ovo = OneVsOneClassifier(SVC(kernel="linear")).fit(X, y)
ovr = OneVsRestClassifier(SVC(kernel="linear")).fit(X, y)
print(len(ovo.estimators_), len(ovr.estimators_))     # 45 10
```

**[Complemento]** A classe `SVC` do scikit-learn **internamente usa um contra um**; o parâmetro `decision_function_shape` só muda o **formato** das pontuações devolvidas, não a estratégia de treino. Para forçar um contra todos, use `OneVsRestClassifier`. Também, "um contra todos" cria, em cada classificador, um problema **desbalanceado** (uma classe contra a soma das outras), o que é uma desvantagem prática conhecida; o slide não diz isso.

> **Se perguntarem na prova:** um contra um = um classificador por par de classes, votação por maioria; um contra todos = um classificador por classe contra o resto, escolhe-se a classe que ganha. Siga o exemplo dos slides: (A, A, C) dá A; (B+C, A+C, C) dá C.

---

## 12. Vantagens e desvantagens (slides 30 e 31)

### Vantagens (slide 30)

1. **Robusto a outliers:** o algoritmo é otimizado a partir dos vetores de suporte (pontos próximos ao hiperplano), então ruídos distantes pouco influenciam (seção 4).
2. **Lida muito bem com dados esparsos** (muitos zeros).
3. **Resolve problemas de classificação não lineares** com o uso dos kernels (seção 7).
4. **Efetivo com alta dimensionalidade** (bancos com muitos atributos).

**Exemplo nosso:** dados esparsos com muitas colunas são típicos de texto (uma coluna por palavra, quase todas zero). Aplicações como filtro de spam são citadas no material Gyl **[complemento]**.

### Desvantagens (slide 31)

1. **Caixa preta:** a interpretação e a visualização são muito complexas, principalmente em dimensão alta.
2. **Lento** em comparação com outros classificadores; a velocidade de treino varia com os hiperparâmetros. **Evitar em datasets gigantes.**
3. **Ajuste de hiperparâmetros** exige vários testes para achar o melhor custo-benefício; escolhas indevidas de C e Gamma podem levar **facilmente a overfitting**.

**[Complemento, não está nos slides]** O tempo de treino do SVM com kernel cresce rápido com o número de amostras (de forma grosseira, entre o quadrado e o cubo); por isso, para milhões de linhas, costuma-se usar variações lineares. E, **muito importante na prática**, os slides **não mencionam** a escala dos atributos, mas o SVM usa distâncias e produtos internos, então atributos em escalas muito diferentes distorcem o resultado. A solução é **padronizar** (seção 13). O material Gyl pede explicitamente normalização no exercício do vinho.

> **Se perguntarem na prova:** SVM é robusto a outliers, bom para dados esparsos e alta dimensionalidade, resolve problemas não lineares com kernels; é caixa preta, lento em bases gigantes e sensível à escolha de C e Gamma.

---

## 13. Código scikit-learn: o que costuma cair em "o código está certo?" **[complemento]**

Os slides da Aula 11 **não trazem código**. O material de exercícios Gyl usa SVC, Pipeline e GridSearchCV; por isso a prova pode trazer trechos assim. Todos os trechos desta seção foram executados.

### Padronizar dentro do Pipeline

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_wine(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

sem_escala = SVC(kernel="rbf").fit(Xtr, ytr)
print(round(sem_escala.score(Xte, yte), 3))          # 0.694

modelo = Pipeline([("scaler", StandardScaler()), ("svm", SVC(kernel="rbf", C=1, gamma="scale"))])
modelo.fit(Xtr, ytr)
print(round(modelo.score(Xte, yte), 3))              # 0.972
```

O vinho tem 13 atributos em escalas muito diferentes; sem padronização o acerto no teste foi 69%, com padronização 97%. Analogia: somar "idade em anos" e "salário em reais" num cálculo de distância é como comparar metros e milímetros sem converter: a coluna de maior magnitude manda em tudo.

**Erros de lógica que a prova pode colocar neste código:**

| Erro | Por que está errado |
| :-- | :-- |
| `StandardScaler().fit(X)` antes de separar treino e teste | O teste vaza para o treino (a média e o desvio usaram os dados de teste) |
| `scaler.fit(Xte)` ou `fit_transform` no teste | O teste deve só usar `transform` com o que foi aprendido no treino |
| Treinar `SVC` sem padronizar (atributos em escalas diferentes) | A margem fica dominada pelo atributo de maior magnitude |
| Usar `gamma` com `kernel="linear"` | O Gamma só existe nos kernels não lineares (slide 23); no linear é ignorado |
| Padronizar **depois** de `fit` do SVC | A ordem certa é escalar antes de treinar; no Pipeline isso é automático |

### Escolher C e gamma com busca em grade e validação cruzada

```python
from sklearn.model_selection import GridSearchCV

# (continua do bloco anterior: Pipeline, StandardScaler, SVC, Xtr, ytr, Xte, yte)
pipe = Pipeline([("scaler", StandardScaler()), ("svm", SVC(kernel="rbf"))])
grade = {"svm__C": [0.1, 1, 10], "svm__gamma": [0.001, 0.01, 0.1]}
gs = GridSearchCV(pipe, grade, cv=5).fit(Xtr, ytr)
print(gs.best_params_, round(gs.best_score_, 3), round(gs.score(Xte, yte), 3))
# {'svm__C': 1, 'svm__gamma': 0.01} 0.993 1.0
```

O `GridSearchCV` testa todas as combinações (9 aqui), cada uma com validação cruzada em 5 partes. Colocar o scaler no Pipeline garante que a padronização seja refeita dentro de cada partição (sem vazamento).

---

## 14. Divergências e pontos delicados: o que responder na prova

| Tópico | O que os slides dizem | O que as bibliotecas ou a literatura fazem | O que responder |
| :-- | :-- | :-- | :-- |
| Sentido de C | Slide 21: C é inverso da regularização; C grande = penalidade alta por errar | Slides 14 e 15 (fórmula Σεi ≤ C) tratam C como orçamento de erros: C maior = mais tolerância | Para efeito de C, siga os slides 21 e 22: C grande = rígido, overfitting |
| Quatro painéis do slide 16 | Sem rótulo de C | Figura vinda da fórmula de orçamento | Não responda o valor de C por painel; só que a margem estreita |
| Definição de margem | Slide 6: distância dos vetores de suporte ao hiperplano | Slides 13 e 25: largura do corredor (2/‖β‖) | Escolha conforme o enunciado; corredor = 2 × distância |
| Símbolo M | Slide 13: distância até o hiperplano com Σβ² = 1 | Slide 25: M = 2/‖β‖ (largura total) | Anote qual escrita a questão usa |
| Kernels | Slide 26: linear, polinomial (com +1), RBF; slide 23 cita sigmoide | scikit-learn: polinomial com γ e r; sigmoide existe | Use as fórmulas do slide |
| Gamma | Slide 23: só SVM não linear | Em scikit-learn, kernel linear ignora gamma | Concorda |
| Margem suave: origem | Slides não citam autores | Material Gyl cita Cortes e Vapnik (1995) e o truque do kernel (1992) | Só cite se a questão perguntar história (complemento) |
| Padronização | Não aparece nos slides | Prática obrigatória em SVM | Em questão de código, aponte falta de padronização como erro |
| Estratégia multiclasse do SVC | Slides só descrevem as duas | `SVC` usa um contra um por dentro | Siga o slide para descrever; saiba o fato do scikit-learn |

---

## 15. Afirmações típicas de prova: verdadeiro ou falso

| Afirmação | Veredito | Por quê |
| :-- | :-- | :-- |
| O SVM serve só para classificação | Falso | Slide 3: classificação **e regressão** |
| Vários hiperplanos podem separar as classes; o SVM escolhe o de maior margem | Verdadeiro | Slides 4 e 13 |
| Vetores de suporte são todos os pontos de treino | Falso | Só os mais próximos do hiperplano (slide 6) |
| Apagar um ponto distante da fronteira muda o hiperplano | Falso | O modelo depende dos vetores de suporte (slides 6 e 30) |
| Yi·f(Xi) > 0 indica classificação correta | Verdadeiro | Slide 10 |
| O vetor β é paralelo ao hiperplano | Falso | É perpendicular (vetor normal), slide 5 |
| β0 define a orientação do hiperplano | Falso | β0 define o deslocamento; a orientação é de β (slide 5) |
| Margem rígida aceita pontos dentro da margem | Falso | Slide 13: todos os pontos fora da margem |
| εi > 1 significa que o ponto está do lado errado do hiperplano | Verdadeiro | Slide 15 |
| Aumentar C faz o modelo tolerar mais erros | Falso | Slide 21: C grande = penalidade altíssima por errar |
| C grande pode causar overfitting e treino lento | Verdadeiro | Slide 22 |
| Gamma existe no SVM linear | Falso | Slide 23: só no não linear (kernels) |
| Gamma alto aumenta a influência de pontos distantes | Falso | Slide 24: pontos distantes são desconsiderados |
| Gamma alto leva a fronteiras complexas e overfitting | Verdadeiro | Slide 24 |
| O truque do kernel mapeia os dados para uma dimensão menor | Falso | Slide 19: para uma dimensão **maior** |
| O problema dual depende só de produtos internos entre pares de pontos | Verdadeiro | Slides 25 e 26 |
| No um contra um, com 3 classes, os classificadores são (A, B), (A, C) e (B, C) | Verdadeiro | Slide 28 |
| Para 10 classes, um contra um treina 10 modelos | Falso | Treina 45 (complemento); quem treina 10 é um contra todos |
| SVM é interpretável em qualquer caso | Falso | Slide 31: caixa preta, sobretudo em dimensão alta |
| SVM é recomendado para datasets gigantes | Falso | Slide 31: evitar em bases gigantes |
| SVM é robusto a outliers | Verdadeiro | Slide 30 (para pontos longe da fronteira) |

---
