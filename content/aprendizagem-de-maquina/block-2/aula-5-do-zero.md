# Aula 5 do zero: Regressão Linear, otimização, regularização e métricas

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e um exemplo concreto, depois com o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção) e cobre os 55 slides.

**Aviso sobre figuras.** Muitos slides desta aula são só imagem (14, 16, 17, 21, 25, 27, 34, 37, 55) ou têm fórmulas em imagem (29 a 34, 50, 53, 54). Os arquivos de texto extraídos não trazem o conteúdo dessas imagens, então **não afirmo nada sobre o que está desenhado nelas**. Onde eu escrevo uma fórmula que no slide é imagem, ela é a fórmula padrão da literatura e está marcada como tal.

**Convenções.** "Exemplo nosso" = exemplo criado aqui, não está nos slides. "Fora dos slides" = conhecimento da literatura ou do scikit-learn que não consta nos slides. Fórmulas estão em blocos de texto simples (sem LaTeX).

**A pergunta que a aula inteira responde:** *como um computador encontra a melhor reta (ou plano) que liga entradas a um número, e como saber se essa reta é boa?*

Analogia de software: é como ajustar a fórmula de uma estimativa de prazo olhando projetos passados. Em vez de alguém dizer "cada tela custa 3 dias", você deixa os dados dizerem quanto cada fator pesa.

---

## 1. O que é Regressão Linear (slides 1 a 3)

Os slides 1 e 2 são capa e título (Aprendizagem de Máquina, Regressão Linear).

**Slide 3.** Regressão linear é um **algoritmo supervisionado** usado para **estimar um valor contínuo** de algo a partir de dados históricos. Olhando o passado, você "prevê" o futuro. O slide também diz que a regressão é uma ferramenta que **modela relações entre variáveis dependentes e independentes por métodos estatísticos**.

Três palavras para fixar:

- **Supervisionado:** os dados históricos já trazem a resposta certa (o "gabarito"). O algoritmo aprende comparando o que previu com o que de fato aconteceu.
- **Contínuo:** o resultado é um número que pode assumir qualquer valor numa faixa (preço, tempo, peso, latência), e não uma categoria (aprovado/reprovado, spam/não spam). Prever categoria é **classificação**; prever número é **regressão**.
- **Modelar a relação:** descobrir "quando isto muda, aquilo muda assim".

**Exemplo nosso.** Você precisa estimar a latência de uma API em milissegundos. Se soubesse a regra exata, escreveria:

```python
def calcular_imposto(salario):
    return salario * 0.15      # regra conhecida: nao precisa de AM
```

Mas para a latência você não tem a regra; tem um log com milhares de medições (requisições por segundo, memória usada, número de pods) e a latência observada. A regressão linear **descobre os pesos** de uma fórmula do tipo `latencia = base + peso1 × requisições + peso2 × memória`.

> **Se perguntarem na prova:** regressão linear é supervisionada e prevê valor numérico contínuo a partir do histórico.

---

## 2. A equação da reta e seus símbolos (slides 4 a 6)

**Slide 4.** O objetivo é **achar uma função que represente da melhor forma os pontos**:

```
Y = α + β·x
```

Ao variar α e β, obtêm-se **retas diferentes**. Treinar é escolher, entre infinitas retas, a melhor.

**Slide 5** define os símbolos (em notação matricial, útil quando há mais de uma entrada):

| Símbolo | Nome | O que é |
| :-- | :-- | :-- |
| y | vetor de resposta | os valores da variável dependente (o que queremos prever) |
| X | matriz de características | **contém apenas valores numéricos**; cada linha é um exemplo, cada coluna uma variável independente |
| α (alfa) | constante de regressão (intercepto) | valor de Y quando x = 0 |
| β (beta) | vetor de coeficientes | pesos que multiplicam cada característica, combinados com α para fazer a previsão |

Dois pontos de prova no slide 5:

1. **X só aceita números.** Texto ("São Paulo", "sim/não") precisa ser convertido antes (isso é pré-processamento, tema de outras aulas). Num trecho de código, se uma coluna de texto vai direto ao `fit`, está errado.
2. **β é um vetor** (um peso por característica), enquanto α é um número só.

**Nota de notação.** Na geometria da escola a reta é `y = m·x + b`: m é a inclinação (β) e b é o intercepto (α). Os slides 30 a 35 usam m e b.

**Slide 6** define os dois papéis:

- **Variável independente (X):** a grandeza que é **manipulada ou medida** e que **não sofre influência das outras variáveis**. Pode ser uma ou mais.
- **Variável dependente (Y):** valores **associados diretamente a X**; de forma direta ou indireta, X exerce influência sobre Y.

Analogia: X são os **argumentos** da função; Y é o **valor de retorno**. Você escolhe os argumentos e observa o retorno.

**Exemplo nosso (leitura dos símbolos).** Suponha que o modelo aprendeu `latência = 35 + 0,18 × requisições_por_segundo`. Então α = 35 (com zero requisição, a latência-base é 35 ms) e β = 0,18 (cada requisição por segundo a mais acrescenta 0,18 ms). Com 500 req/s: 35 + 0,18 × 500 = 125 ms.

---

## 3. Correlação de Pearson (slide 7)

**Slide 7.** A relação entre variáveis dependente e independente é medida por algum **coeficiente de correlação**. Um dos mais usados é o **coeficiente de Pearson**, que mede a **associação linear** entre duas variáveis. (As imagens do slide mostram exemplos de gráficos; não foram conferidas.)

Faixa de valores do r de Pearson (esta parte é a definição padrão; o slide só dá a ideia geral):

- r = +1: relação linear positiva perfeita (X sobe, Y sobe na mesma proporção).
- r = −1: relação linear negativa perfeita (X sobe, Y desce na mesma proporção).
- r = 0: **nenhuma relação LINEAR**.

**Exemplo nosso com números.** Cinco pares: x = 1, 2, 3, 4, 5 e y = 2, 4, 5, 4, 5. Média de x = 3, média de y = 4. O r de Pearson é a covariância dividida pelo produto dos desvios: 6 / √(10 × 6) ≈ 0,77. Correlação positiva forte. (E a reta de mínimos quadrados dá β = 6/10 = 0,6 e α = 4 − 0,6 × 3 = 2,2, isto é, `y ≈ 2,2 + 0,6x`.)

**Armadilha clássica.** r = 0 **não** significa "sem relação", significa "sem relação em linha reta". **Exemplo nosso:** x = −3, −2, −1, 0, 1, 2, 3 e y = x² (uma parábola perfeita). A relação é determinística, mas r = 0, porque os dois lados da parábola se cancelam. (Isso vale para x simétrico em torno de zero, como aqui.) Conclusão: r mede **só linearidade**.

Outra armadilha: **correlação não implica causalidade**. Sorvete e afogamentos sobem juntos no verão; o calor é a causa oculta de ambos.

> **Se perguntarem na prova:** Pearson mede associação **linear**; r próximo de 0 não prova independência.

---

## 4. Onde medir correlação (slides 8 e 9)

**Slide 8.** Devemos avaliar a correlação em **duas situações**:

| Entre quais variáveis | Para quê | O que queremos |
| :-- | :-- | :-- |
| Independente (X) e dependente (Y) | avaliar o **poder preditivo** | correlação **forte** |
| Independentes entre si (X1 e X2) | identificar **multicolinearidade e redundância** | correlação **baixa** |

**Multicolinearidade** é quando duas colunas de entrada dizem quase a mesma coisa (exemplo nosso: peso em kg e peso em libras). Analogia: duas métricas de monitoramento que sempre sobem juntas porque medem a mesma causa; o modelo não consegue decidir quanto crédito dar a cada uma e os coeficientes ficam instáveis. (Fora dos slides: no caso extremo, colinearidade perfeita, a conta do MQO nem fecha; ver seção 9.3.)

O slide 8 ainda diz duas coisas: (1) **nem sempre as correlações são tão explícitas**, sendo necessárias abordagens mais robustas; (2) em ML, modelos de regressão podem ser criados por **várias abordagens, das mais simples** (poucos parâmetros, fácil de interpretar) **às mais complexas**. É o gancho para as seções seguintes.

**Slide 9, exemplo.** Variável independente: índice de felicidade. Variável dependente: expectativa de vida. Países com maior índice de felicidade tendem a ter maior expectativa de vida, com **força de correlação 0,77**. Não prova causa: renda e saneamento podem estar por trás das duas.

---

## 5. O erro e a função custo (slides 10 e 11)

**Slide 10.** Como saber se uma reta é melhor que outra? **A que tiver menor erro.** O erro num ponto i é a **diferença entre o valor previsto pela função e o valor real**.

```
resíduo_i = y_i − ŷ_i        (ŷ lê-se "y chapéu": a previsão)
```

Analogia de software: é a diferença entre o resultado esperado e o obtido num teste. O **resíduo** é o "diff" de cada caso de teste.

**Por que não somar os erros crus?** Um erro de +10 e um de −10 se cancelam, e a soma dá 0, como se o modelo fosse perfeito. Por isso os erros são elevados ao quadrado (ou tomados em módulo) antes de somar.

**Slide 11.** Para calcular o erro de **todos** os pontos há uma **função custo** (cost function). O objetivo da regressão linear é **minimizar a função custo**. Em engenharia de software: é uma função `custo(α, β)` que devolve um número, "quão ruim é esta reta"; treinar é achar os argumentos que a minimizam.

---

## 6. Como achar α e β: três estratégias (slide 12)

**Slide 12.** Como encontrar os valores de α e β que minimizam a função custo? Três estratégias:

1. **Força bruta:** testar vários valores aleatoriamente e comparar.
2. **Pequenas mudanças:** alterar cada variável um pouquinho e avaliar se está caminhando na direção certa.
3. **Passos adaptados ao erro:** se está muito longe do ideal (erro grande), dar **passos maiores**; à medida que chega perto (erro pequeno), dar **passos mais curtos** para o ajuste fino. **Esta é o Gradiente Descendente.**

Analogia: achar a senha de um cofre. (1) é testar combinações ao acaso; (2) é girar um pouco e ouvir se o clique "esquentou"; (3) é girar rápido enquanto o clique está fraco e devagar quando fica forte. O slide 23 repete exatamente esta lista como abertura da seção de gradiente descendente.

---

## 7. Regressão simples e múltipla (slides 13 a 17)

**Slide 13.** Há **dois tipos**: **simples** (somente **uma** variável independente) e **múltipla** (**várias** variáveis independentes).

**Slide 15.** Na múltipla, a fórmula é mais complicada: vários x, **cada um ponderado pelo seu próprio beta**. Não dá mais para usar um plano de coordenadas simples com x e y: o espaço tem **várias dimensões, cada uma uma característica**. O resultado é um **hiperplano**, não mais uma linha.

| | Simples | Múltipla |
| :-- | :-- | :-- |
| Entradas | 1 variável (x) | 2 ou mais (x1, x2, ..., xp) |
| Equação | Y = α + β·x | Y = α + β1·x1 + β2·x2 + ... + βp·xp |
| Geometria | **reta** num plano 2D | **plano** (2 entradas) ou **hiperplano** (3 ou mais) |

**Hiperplano** é só a generalização de "reta" e "plano" para mais dimensões. Você não consegue desenhar com 10 entradas, mas a ideia é a mesma: uma superfície "plana" nesse espaço.

**Exemplo nosso (múltipla).** `latência = 20 + 0,15 × req_por_s + 0,4 × memória_GB − 3 × pods`. Cada coeficiente responde: "mantendo as demais entradas fixas, o que acontece com a latência se esta aumentar 1 unidade?". O sinal negativo em pods diz que mais pods derruba a latência.

Os slides 14, 16 e 17 são **só imagem** (intitulados "Tipos de Regressão Linear" e "Introdução"); o conteúdo desenhado não foi conferido. Não há texto de prova extra neles além do que está nos slides 13 e 15.

---

## 8. Quando aplicar e a influência de β (slides 18 e 19)

**Slide 18.** A regressão linear se aplica quando há **boa correlação linear (positiva ou negativa)** entre os dados. Se a relação é uma parábola ou tem outra forma, uma reta não representa bem. (O slide 47 reforça: é preciso **alta correlação** para ela funcionar bem.)

**Slide 19.** Cada β é um número que descreve a **intensidade da relação** da característica com a resposta:

- β **próximo de zero**: efeito pequeno.
- β **longe de zero** (positivo ou negativo): efeito significativo, característica importante.
- **Bom hábito: padronizar as características**, para não se enganar com valores altos de β em características de escala pequena e para **poder comparar** diferentes coeficientes.

**Exemplo nosso (por que a escala engana).** Prever o preço de um imóvel com área em metros quadrados (50 a 200) e distância ao metrô em **metros** (100 a 5000). Se um metro de distância custa pouco, o β da distância sai minúsculo (por exemplo, −8 por metro), enquanto o β da área sai grande (por exemplo, +3000 por m²), mesmo que a distância seja tão importante quanto a área. Trocar a distância para quilômetros multiplica esse β por 1000. Os números dos β dependem da unidade; **padronizar** (média 0, desvio padrão 1 em cada coluna) coloca todos na mesma régua.

**Fora dos slides (nuance importante).** O slide 19 justifica a padronização pela **comparação dos β**. Na regressão linear pura (OLS), padronizar **não muda a previsão**, só a leitura dos β. Já em **Ridge e Lasso** (seção 13), padronizar **muda o resultado**, porque a penalidade soma os coeficientes e depende da escala. Também ajuda o gradiente descendente a convergir. Essas duas últimas ideias são nossas, não estão no slide 19.

---

## 9. Como achar os coeficientes: MQO (OLS) × gradiente descendente (slides 20 a 22)

### 9.1 O que o slide 20 diz

Na estatística, "regressão linear" muitas vezes quer dizer **mínimos quadrados ordinários (MQO, ou OLS, Ordinary Least Squares)**: um jeito específico de estimar a solução por **cálculo matricial** (uma fórmula direta). Mas:

- **Nem sempre é possível**: depende da **inversão da matriz** de dados, que nem sempre existe.
- Inverter matrizes é **muito lento** quando a matriz é grande.
- No aprendizado de máquina obtém-se os **mesmos resultados** com **gradiente descendente**, que lida com **volumes maiores de dados de modo mais fácil e rápido**, estimando uma solução a partir de **qualquer** matriz de entrada.

Analogia de software: MQO é uma **função com fórmula fechada** (entra a matriz, sai o resultado, sem laço). Gradiente descendente é um **laço que refina** uma estimativa até estabilizar. Equivalente a calcular uma raiz quadrada pela fórmula versus pelo método de tentativa e refinamento.

A fórmula fechada do MQO (padrão da literatura; no slide 21 é imagem, não conferida):

```
β = (Xᵀ X)⁻¹ Xᵀ y
```

Lê-se: transpõe X, multiplica por X, inverte o resultado, multiplica por Xᵀ e depois por y. O "inverte" é a parte cara e a que pode falhar.

### 9.2 Complexidade: as duas versões (slides 22 e 47)

**Slide 22 diz:** a complexidade computacional ao treinar uma regressão linear por mínimos quadrados é **linear** em relação ao número de instâncias e de características. Portanto, **dobrar as instâncias dobra o tempo**. **Slide 47** liga a complexidade do MQO "diretamente à quantidade de pontos".

**A literatura diz outra coisa** (fora dos slides): a equação normal exige multiplicar XᵀX (custo da ordem de n × d², com n linhas e d colunas) e **inverter uma matriz d × d (custo da ordem de d³)**. Ou seja, o custo cresce **linearmente com o número de linhas n**, mas **cubicamente com o número de colunas d**. O gradiente descendente custa da ordem de n × d **por iteração**.

| Versão | Afirmação |
| :-- | :-- |
| Slide 22 | MQO é linear em instâncias e características; dobrar instâncias dobra o tempo |
| Literatura | MQO ≈ O(n·d² + d³); linear em n, mas cúbico em d |

**Se perguntarem na prova:** se a alternativa repetir o slide 22 (linear no número de instâncias; dobrar as instâncias dobra o tempo), é **isso** que a professora ensinou: marque. Se a questão for conceitual e afirmar "MQO escala mal com muitas características", também está de acordo com o slide 20 (inversão lenta com matriz grande) e com a literatura. A frase do slide 22 sobre instâncias é compatível com a literatura (linear em n); o que a literatura acrescenta é o custo cúbico em d.

### 9.3 Escolha entre os dois (slide 47)

- **Poucas dimensões** (poucas variáveis preditoras): **MQO** é mais recomendado, porque **não é iterativo** (obs.: o slide escreve "interativo"; o sentido é "iterativo").
- **Muitas dimensões**: o **GD** tem melhor desempenho.

O slide 47 conclui também que a regressão linear pode ser aplicada a uma vasta variedade de problemas, mas **precisa de alta correlação** nos dados para funcionar bem.

**Fora dos slides (por que o MQO pode falhar):** se duas colunas são cópias perfeitas uma da outra (colinearidade perfeita), a matriz XᵀX é **singular** (não tem inversa) e a fórmula quebra. É a versão extrema da multicolinearidade da seção 4.

### 9.4 Primeiro trecho de scikit-learn (executado)

O scikit-learn usa solução fechada (por baixo, métodos de álgebra linear) na classe `LinearRegression`. Exemplo nosso, executado e funcionando: latência em função de requisições por segundo, com uma divisão treino/teste.

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

X = np.array([[100], [200], [300], [400], [500], [600], [700], [800]])  # req/s
y = np.array([55, 70, 92, 108, 131, 145, 170, 182])                     # ms
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

modelo = LinearRegression()
modelo.fit(X_train, y_train)          # 1) aprende alfa e beta so com o treino
y_pred = modelo.predict(X_test)       # 2) preve no teste

print(modelo.intercept_)              # alfa (aprox. 35,39)
print(modelo.coef_)                   # beta (aprox. 0,1841)
print(mean_absolute_error(y_test, y_pred))   # MAE  aprox. 3,56
print(mean_squared_error(y_test, y_pred))    # MSE  aprox. 17,43
print(r2_score(y_test, y_pred))              # R2   aprox. 0,99
```

Pontos que a prova explora em trechos assim: a **ordem** (`fit` antes de `predict`); `fit` só com **treino**; métricas calculadas com `(y_real, y_previsto)` e, em `r2_score`, a ordem dos argumentos é `(y_true, y_pred)`; `intercept_` é o α e `coef_` é o β (vetor).

---

## 10. Gradiente descendente: a ideia (slides 23 a 25)

**Slide 23** repete as três estratégias do slide 12 (seção 6); a terceira é o gradiente descendente.

**Slide 24.** O gradiente descendente é um **algoritmo de otimização** que **minimiza uma função** movendo-se **iterativamente na direção da descida mais íngreme**, dada pelo **negativo do gradiente**. Em ML, serve para **atualizar os parâmetros do modelo**. (Os slides 24 e 25 têm imagens que não foram conferidas.)

**Analogia da montanha com neblina.** Você está numa montanha à noite, com neblina, e quer chegar ao ponto mais baixo (o vale = menor erro). Não vê o vale; só sente a **inclinação do chão sob os pés**. A cada passo você anda na direção em que o chão desce mais e repete até o chão ficar plano. Analogia de software: **busca local** guiada por feedback, sem ver o mapa inteiro.

**O que é "gradiente".** (Fora dos slides, mas necessário.) É o conjunto das derivadas parciais da função custo, uma por parâmetro (uma para α, uma para β). Ele aponta para onde o custo **mais cresce**; por isso o algoritmo anda no **sentido contrário** (o "negativo" do gradiente). O símbolo ∂ nas fórmulas significa "derivada em relação a só este parâmetro, mantendo os outros fixos".

---

## 11. Derivada e a regra de atualização (slides 26 a 35)

### 11.1 Derivada (slides 26 e 27)

**Slide 26.** Geometricamente, a derivada no ponto x = a de y = f(x) é a **inclinação da reta tangente** ao gráfico nesse ponto. (O slide 27 é só imagem.)

Intuição de software: derivada é a "taxa de variação", tipo a taxa de crescimento de uma métrica: quanto a saída muda quando a entrada muda um pouquinho. Tangente = a reta que "encosta" na curva naquele ponto.

### 11.2 Objetivo e função de custo (slides 28 e 29)

**Slide 28.** O objetivo do GD é encontrar o valor de **w** que **minimiza o erro J(w)**. (Fórmulas em imagem.)

**Slide 29.** Com o GD, a regressão linear encontra o melhor conjunto de **coeficientes beta (e a constante de regressão)** que minimiza uma função de custo. Entre as funções de custo mais populares está a **SQR (Soma dos Quadrados dos Resíduos)**, o quadrado da diferença entre previsões e valores reais:

```
SQR = Σ (y_i − ŷ_i)²       (soma sobre todos os pontos i)
```

(A fórmula é imagem no slide; esta é a padrão.) Graficamente, o resultado da otimização são as **distâncias verticais** entre os pontos e a linha de regressão. Por que ao quadrado: elimina o cancelamento de sinais e **pune mais** os erros grandes.

### 11.3 A atualização (slides 30 a 35)

**Slides 30 e 31.** O GD calcula a solução **otimizando os coeficientes lenta e sistematicamente**, e baseia sua fórmula de atualização na **derivada da função de custo**.

**Slides 32 e 33.** Mostram a atualização separada do coeficiente **m** (inclinação) e do coeficiente **b** (intercepto). (As fórmulas são imagem; o slide 34 também. Abaixo está a regra padrão.)

```
m_novo = m − γ1 · (derivada do custo em relação a m)
b_novo = b − γ2 · (derivada do custo em relação a b)
```

Para o custo SQR com a reta ŷ = m·x + b, essas derivadas valem (derivação nossa, padrão da literatura):

```
∂SQR/∂m = −2 · Σ x_i · (y_i − ŷ_i)
∂SQR/∂b = −2 · Σ     (y_i − ŷ_i)
```

**Slide 35.** Como a função representa a **soma de todos os erros**, sua **ordem de grandeza é muito maior** que a de m ou b. Por isso as constantes **γ1 e γ2** (letra grega gama) **normalizam** esses valores para a ordem de grandeza do problema. **Essas constantes são chamadas de taxa de aprendizado.** E: **gradiente negativo aumenta o valor do parâmetro e vice-versa.**

Os sinais, em detalhe (o que a prova cobra):

| Derivada (inclinação do custo) | O que significa | O que o GD faz com o parâmetro |
| :-- | :-- | :-- |
| **Positiva** | o custo cresce para a direita | **diminui** o parâmetro (passo para a esquerda) |
| **Negativa** | o custo cai para a direita | **aumenta** o parâmetro (passo para a direita) |
| Perto de zero | chão plano: está no fundo | quase não muda (convergiu) |

Regra geral resumida (fora dos slides, forma compacta):

```
θ ← θ − η · ∂J/∂θ          (θ = parâmetro; η = taxa de aprendizado)
```

O sinal de menos faz o parâmetro andar contra o gradiente (descida). Nos slides a taxa aparece como γ1 e γ2; é a mesma coisa que η.

### 11.4 Exemplo numérico trabalhado (exemplo nosso)

Dados: x = 1, 2, 3 e y = 2, 4, 6 (a reta certa é y = 2x, sem intercepto). Começamos com m = 0 e taxa 0,1. Usamos o custo "MSE" (dividido por n = 3), cuja derivada é −(2/3) · Σ x·(y − m·x):

| Iteração | Derivada | m novo = m − 0,1 · derivada |
| :-- | :-- | :-- |
| 1 | −18,67 | 0 + 1,87 = 1,87 |
| 2 | −1,24 | 1,87 + 0,12 = 1,99 |
| 3 | −0,08 | 1,99 + 0,01 = 2,00 |

Veja o que acontece, e é isso que a prova pede para você notar: **a derivada é negativa, então m aumenta**; os **passos encolhem sozinhos** porque a derivada encolhe conforme chega perto do fundo; em 3 iterações m já está em ≈ 2,00, o valor certo. Com o custo SQR sem dividir por n a derivada seria 3 vezes maior (e a mesma taxa 0,1 faria o passo enorme e **divergiria**); por isso o slide 35 insiste em "normalizar" com a taxa de aprendizado.

### 11.5 Slide 36: uma iteração na prática

O slide 36 (com imagem) descreve: a **reta vermelha tracejada** é a reta **antes** da atualização, a inicial com **m = 1,0 e b = 0**; a **reta verde contínua** é a reta **depois de uma iteração** do GD, que se ajustou na direção que **reduz o erro quadrático médio (MSE)**. Ou seja: cada iteração leva a reta um passo mais perto dos pontos. O slide 37 é só imagem.

---

## 12. O GD em resumo e a taxa de aprendizado (slides 38 a 44)

### 12.1 Slide 38: o que é e qual é o custo

O GD é uma das técnicas mais usadas para **otimização de modelos de ML**. O slide chama de método "interativo" (leia **iterativo**) que busca os coeficientes α e β **minimizando uma função de custo**, que normalmente é o **erro quadrático médio (MSE)**. Em cada iteração, calcula-se o **somatório do erro** entre todos os valores reais e os calculados; com base nesse erro e numa **taxa de aprendizagem predefinida**, os coeficientes são atualizados para a próxima iteração.

**Atenção: SQR (slide 29) e MSE (slide 38) são o mesmo ponto de partida com escalas diferentes.** O MSE é a SQR **dividida por n**. O mínimo (os melhores α e β) é o mesmo, mas a escala do custo e do gradiente muda, e com ela o valor adequado da taxa de aprendizado. Os slides usam as duas siglas sem avisar; não se assuste.

### 12.2 Slide 39: o que a taxa de aprendizado controla

O parâmetro **taxa de aprendizado** (learning rate) diz **qual distância será percorrida em cada iteração**. Analogia do slide: um jogo de tabuleiro em que seu learning rate é **2 casas**: toda vez que é sua vez, você só anda de 2 em 2. O ponto de partida pode ser aleatório ou não. O slide afirma que o gradiente "sempre apontará para o mínimo local"; quando chega ao menor valor da função de custo, diz-se que **convergiu**. Learning rate **muito pequeno** custa caro computacionalmente por demorar a convergir; **muito grande** pode **falhar em convergir, passando direto do mínimo**.

"Convergir" = o algoritmo parou de melhorar e estabilizou num valor. Analogia de software: um laço `while` cuja condição de parada é "a melhora ficou desprezível".

### 12.3 Slide 40 e a divergência com a literatura

O slide 40 diz: **valor muito alto** para a taxa de aprendizagem pode levar o modelo a **cair em um mínimo local**; **valor muito baixo** faz o modelo demorar mais para chegar ao ajuste ideal, exigindo muito mais tempo e processamento. E: **é normal encontrar learning rate entre estes valores: 0,001, 0,003, 0,01, 0,03, 0,1, 0,3.**

**Divergência.** A função custo da regressão linear com erro quadrático é uma "tigela" suave com **um único fundo** (matematicamente, **convexa**: não existem mínimos locais, só o mínimo global). Num problema assim, uma taxa alta **não leva a mínimo local**: ela faz o algoritmo **pular de um lado ao outro do vale e oscilar, ou até divergir** (o erro cresce em vez de cair). Mínimos locais são problema de funções com muitos vales, como redes neurais. (Observe que o próprio slide 39 já diz "passa direto do mínimo", que é a versão correta.)

**Se perguntarem na prova:**

- Se a alternativa repetir o slide 40 ("taxa muito alta pode levar a um mínimo local"), **é o que a professora ensinou**: marque como correta.
- Se a questão pedir o efeito correto em geral ou na regressão linear, a resposta é: **oscila, passa do mínimo, pode não convergir ou divergir**.
- Se as duas aparecerem como alternativas concorrentes, prefira a que coincide com o slide 39 ("passa do mínimo e falha em convergir") e leia o enunciado para ver se pede "segundo a professora".
- Sobre taxa baixa, não há divergência: **lenta, mais iterações, mais custo**.

### 12.4 Slides 41 a 44: o experimento

**Slide 41.** Os **dois hiperparâmetros principais** do GD são a **taxa de aprendizagem** e o **número de iterações**. (**Hiperparâmetro** = ajuste que você escolhe **antes** de treinar, como uma flag de configuração; os β, ao contrário, são aprendidos.) As imagens seguintes usam o exemplo anterior com GD.

| Slide | Configuração | O que aconteceu |
| :-- | :-- | :-- |
| 42 | 50 iterações, taxa **muito baixa (0,01)** | as iterações **terminam antes de o modelo convergir** |
| 43 | taxa **alta (0,9)** | (imagem; efeito instável, ver 12.3) |
| 44 | taxa **equilibrada** | nas primeiras iterações o gradiente tem **alta perturbação**, que vai **se atenuando ao longo das épocas** |

**Observe o ponto que gera confusão.** No slide 42 a taxa **0,01 é chamada de "muito baixa"**, embora 0,01 esteja na lista "normal" do slide 40. Moral: **"baixo" e "alto" são relativos ao problema** (escala dos dados, custo usado, número de iterações). 0,01 é pequeno **para aquele exemplo**, com **só 50 iterações**. A causa de terminar antes da convergência, no slide 42, é a combinação de taxa baixa com poucas iterações.

**Época (epoch)** = uma passada completa do algoritmo pelos dados de treino. "Ao longo das épocas" = ao longo das iterações.

**Faixas de valores.** Os únicos números que a professora dá são os do slide 40 (0,001 a 0,3) e os exemplos 0,01 (muito baixa, slide 42) e 0,9 (alta, slide 43). Qualquer outra faixa "ideal" seria opinião nossa, e não vale como regra: depende do problema.

### 12.5 Segundo trecho de scikit-learn (executado): o efeito da taxa

`SGDRegressor` faz regressão linear por **gradiente descendente estocástico** (variante: atualiza com amostras individuais ou pequenos lotes). Seus hiperparâmetros incluem `eta0` (taxa inicial) e `max_iter` (número de iterações), os dois do slide 41. Exemplo nosso, com dados padronizados:

```python
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

rng = np.random.default_rng(1)
X = rng.uniform(0, 100, size=(300, 1))
y = 2.0 * X[:, 0] + 10 + rng.normal(0, 5, 300)

for eta in (0.0001, 0.01, 0.1):
    m = make_pipeline(StandardScaler(),
                      SGDRegressor(eta0=eta, learning_rate="constant",
                                   max_iter=50, tol=None, random_state=0))
    m.fit(X, y)
    print(eta, r2_score(y, m.predict(X)))
# resultado executado: 0.0001 -> R2 aprox. 0,77 (nao convergiu em 50 iteracoes)
#                      0.01   -> R2 aprox. 0,993
#                      0.1    -> R2 aprox. 0,992
```

Leitura: com a taxa muito pequena e só 50 iterações, o modelo **não chegou lá** (R² 0,77), exatamente a história do slide 42. Aqui 0,01 já bastou porque a escala dos dados é outra: confirma que "baixo" é relativo.

---

## 13. Overfitting e regularização (slides 45 e 46)

**Slide 45.** **Regularização** é uma técnica fundamental para evitar **overfitting** (sobreajuste). Regularizar = **adicionar uma penalidade** ao modelo se ele tentar ficar complexo demais para explicar cada pequeno ruído. O objetivo da regressão é minimizar a função custo (a soma dos erros).

- **Sem regularização:** o modelo tenta reduzir o erro a quase zero, criando uma reta (ou curva) que passa por **todos os pontos, inclusive erros e outliers**.
- **Com regularização:** "diminua o erro, mas se os seus coeficientes (beta) ficarem muito grandes, eu aumento o seu custo". Isso força o modelo a manter só as características realmente importantes e **encolher** o impacto das que são só ruído.

Analogia de software: **code review com limite de complexidade**. Você pode passar nos testes, mas se a função tiver complexidade ciclomática absurda, o custo sobe. Overfitting = código que tem um `if` para cada caso de teste.

**Exemplo nosso (por que coeficientes enormes são suspeitos).** Se duas colunas quase idênticas recebem pesos +45000 e −44980, o modelo está usando a diferença minúscula entre elas para "encaixar" os pontos de treino. Isso é ilustrativo, não vem do slide. A penalidade proíbe esse truque, porque pesos grandes encarecem o custo.

Forma geral (fora dos slides):

```
custo_regularizado = erro (MSE ou SQR) + λ × penalidade(β)
```

O **λ (lambda)** controla a força: λ = 0 não penaliza nada (volta a regressão comum); λ muito grande esmaga todos os β para perto de zero (modelo simples demais, **underfitting**). Atenção à nomenclatura: **no scikit-learn esse λ se chama `alpha`**, e não tem relação com o α (intercepto) da seção 2.

### Os dois tipos (slide 46)

- **Ridge (L2):** tenta diminuir o valor de **todos** os coeficientes, mas **não os zera**. Ajuda quando há **muitas variáveis correlacionadas**. O slide a compara a um "sossega-leão" em variáveis muito agitadas.
- **Lasso (L1):** mais agressiva; **pode reduzir o coeficiente de uma variável a zero**. Faz uma "limpeza automática", ficando só com as variáveis que importam. **Pode ser usado para seleção de features.**

| Característica | Ridge (L2) | Lasso (L1) |
| :-- | :-- | :-- |
| Penalidade (fórmula padrão, fora dos slides) | λ × soma dos quadrados dos β | λ × soma dos valores absolutos dos β |
| Coeficientes | encolhe todos, **não zera** | encolhe e **pode zerar** |
| Seleção de atributos | **não faz** | **faz** (β = 0 elimina a coluna) |
| Boa para | muitas variáveis correlacionadas | modelo enxuto, descobrir o que importa |

Uma regra de bolso para a prova: **L1 = Lasso = zera** (L de "limpa"); **L2 = Ridge = só encolhe**.

### Terceiro trecho de scikit-learn (executado): padronizar antes de Ridge e Lasso

Exemplo nosso: x1 é a variável útil; x2 é uma **cópia quase igual** de x1 (multicolinearidade); x3 é ruído puro. Ordem correta: dividir, **ajustar o padronizador só no treino**, depois treinar. O `Pipeline` garante isso sozinho.

```python
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso, LinearRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(0)
n = 200
x1 = rng.normal(0, 1, n)
x2 = x1 + rng.normal(0, 0.05, n)    # quase copia de x1
x3 = rng.normal(0, 1, n)            # ruido
X = np.column_stack([x1, x2, x3])
y = 3 * x1 + rng.normal(0, 0.5, n)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

for nome, reg in [("OLS", LinearRegression()),
                  ("Ridge", Ridge(alpha=10.0)),
                  ("Lasso", Lasso(alpha=0.1))]:
    pipe = make_pipeline(StandardScaler(), reg)   # scaler aprende so no treino
    pipe.fit(X_train, y_train)
    print(nome, pipe[-1].coef_, pipe.score(X_test, y_test))
# resultado executado (aprox.):
# OLS   [ 2.21  0.76 -0.00]
# Ridge [ 1.45  1.42  0.00]   -> divide o peso entre x1 e x2, nenhum zerado
# Lasso [ 2.24  0.63  0.00]   -> x3 foi a exatamente 0
```

Leitura: a coluna de ruído (x3) é zerada pelo Lasso; Ridge reparte o peso entre as duas colunas quase iguais, sem zerar nada. Observação honesta: com colunas tão parecidas, até o Lasso pode manter as duas (ele zerou o ruído, não a cópia); o que se garante é que **pode** zerar, não que zere sempre.

Erro clássico que cai em prova de código (**vazamento de dados**, data leakage): chamar `scaler.fit(X)` antes de dividir treino e teste. A média e o desvio calculados usam informação do teste. Correto: `scaler.fit_transform(X_train)` e `scaler.transform(X_test)` (só `transform` no teste).

---

## 14. Conclusão do slide 47 e 48

**Slide 47** (já visto na seção 9.3): poucas dimensões -> MQO; muitas dimensões -> GD; alta correlação necessária.

**Slide 48.** A regressão continua sendo um algoritmo **simples, compreensível e eficaz** para prever valores. É **rápido de treinar, fácil de explicar para leigos e simples de implementar em qualquer linguagem**. É a **primeira escolha da maioria dos praticantes** para construir modelos de **comparação** com soluções mais sofisticadas.

Analogia: a regressão linear é o **teste de fumaça** (smoke test) dos modelos: se um modelo sofisticado não ganha dele, não vale a complexidade. Em ML isso se chama **baseline** (modelo de referência), e na prática é o primeiro a ser treinado.

> **Se perguntarem na prova:** regressão linear = simples, rápida, interpretável, boa como baseline; exige boa correlação linear; MQO para poucas variáveis, GD para muitas.

---

## 15. Métricas de validação para regressão (slides 49 a 55)

**Slide 49** é só o título. Em regressão a saída é um número contínuo, então não faz sentido falar em "acertou ou errou" ou em matriz de confusão (prever 100,001 quando o real é 100,000 seria "erro" numa checagem de igualdade). Avaliamos **o tamanho dos resíduos**.

**Exemplo nosso para todas as métricas.** Cinco imóveis, preços em mil reais:

```
real  y:  10   20   30   40   100
prev ŷ:   12   18   33   38    80
erro e:   −2   +2   −3   +2   +20        (e = y − ŷ)
```

### 15.1 SQR (slide 50)

**Mostra a variação de Y que não é explicada pelo modelo.** (A fórmula é imagem.)

```
SQR = Σ e_i² = 4 + 4 + 9 + 4 + 400 = 421
```

Desvantagem: **cresce com o número de linhas**. Uma base de 1 milhão de linhas dá SQR enorme mesmo com ótimas previsões; não serve para comparar bases de tamanhos diferentes.

### 15.2 R² (slide 51)

**O R² é uma medida estatística de quão próximos os dados estão da linha de regressão ajustada; também chamado de coeficiente de determinação.** O slide afirma: **"o R² está sempre entre 0 e 1"**, em que **0** indica que o modelo **não explica nada** da variabilidade ao redor da média e **1** que **explica toda** a variabilidade.

Fórmula padrão (o slide não a escreve):

```
R² = 1 − SQR / SQT
SQT = Σ (y_i − ȳ)²          (variação dos dados reais em torno da própria média ȳ)
```

No nosso exemplo: ȳ = 40; SQT = 900 + 400 + 100 + 0 + 3600 = 5000; R² = 1 − 421/5000 ≈ 0,92. Lê-se: o modelo explica cerca de 92% da variação dos preços.

Interpretação: SQT é o erro de um "modelo bobo" que sempre responde a média. R² compara o seu modelo com esse chute.

**Divergência: slide × literatura.**

- **Slide 51:** R² está sempre entre 0 e 1.
- **Literatura e scikit-learn (`r2_score`):** R² pode ser **negativo**. Acontece quando as previsões são **piores que simplesmente chutar a média** (por exemplo, modelo sobreajustado avaliado no **teste**, ou regressão sem intercepto). Valor máximo 1; mínimo, menos infinito. Só no treino com OLS e intercepto ele fica entre 0 e 1.

**Se perguntarem na prova:** se a questão pede o que a professora ensinou ou apresenta "sempre entre 0 e 1", marque a versão do slide. Se a questão pergunta se R² pode ser negativo, ou cita avaliação no conjunto de teste, a resposta correta é que **sim, pode ser negativo, e isso indica um modelo pior que a média**.

### 15.3 R² ajustado (slide 52)

O R² simples **nunca diminui** (pelo menos no treino) quando você acrescenta variáveis, mesmo inúteis. O **R² ajustado penaliza** a inclusão de variáveis independentes que não ajudam a explicar Y. O slide diz: variável **útil -> R² ajustado sobe**; **irrelevante -> cai**. E: é a **métrica correta para comparar se um modelo com 5 variáveis é realmente melhor que um com 3** (seleção de modelos).

Fórmula padrão (fora dos slides): com n linhas e p variáveis,

```
R²ajustado = 1 − (1 − R²) × (n − 1) / (n − p − 1)
```

Exemplo nosso: R² = 0,90 com n = 20 e p = 3 dá 1 − 0,10 × 19/16 ≈ 0,88. O ajustado sai sempre um pouco menor que o R² e a diferença cresce com p.

**Divergência fina.** O "sobe se útil, cai se inútil" do slide é a **tendência**, não uma lei: o ajustado só sobe se a melhora do ajuste superar a penalidade; e uma variável inútil pode, por puro acaso, subir um pouco. Para a prova, responda como o slide.

Atenção ao texto da seção de resumo: o R² ajustado serve para comparar modelos com **números diferentes de variáveis** (não "tamanhos" diferentes de dados).

### 15.4 MAE (slide 53)

**Erro médio absoluto**: a métrica de erro de regressão **mais simples de entender**; calcula o valor (absoluto) dos resíduos de cada ponto e tira a **média**.

```
MAE = (1/n) · Σ valor_absoluto(y_i − ŷ_i)
```

No exemplo: (2 + 2 + 3 + 2 + 20) / 5 = 5,8 (mil reais). Interpretação: "em média o modelo erra 5,8 mil reais, para mais ou para menos". Fica na **mesma unidade de Y**.

Fora dos slides: o MAE trata todos os erros de forma **linear**, então é **menos sensível a outliers** do que o MSE.

### 15.5 MSE (slide 54)

**Média dos erros ao quadrado**: é o mesmo cálculo, mas elevando o resíduo ao quadrado.

```
MSE = (1/n) · Σ (y_i − ŷ_i)²
```

No exemplo: 421 / 5 = 84,2 (unidade: mil reais ao quadrado). Observe como o único erro grande (20) responde por 400 dos 421: o MSE **pune fortemente erros grandes**.

**O que o slide 54 diz:** como o resíduo é elevado ao quadrado, **não podemos comparar o MSE com o MAE, porque ele sempre será maior**. Por isso faz mais sentido **comparar o MSE com o MSE de outro modelo**.

**Divergência.** "Sempre será maior" não é uma regra matemática: o quadrado de um erro **menor que 1** é **menor** que o próprio erro (erro 0,5: MAE 0,5; MSE 0,25). E as **unidades são diferentes** (reais contra reais ao quadrado), que é o motivo real para não compará-los.

**Se perguntarem na prova:** se a alternativa disser "o MSE não deve ser comparado diretamente ao MAE" ou "compara-se MSE com MSE de outro modelo", marque (estão de acordo com o slide e com a literatura). Se disser "o MSE é sempre maior que o MAE", é o texto do slide: marque se a questão perguntar "segundo a professora"; sabendo que, na realidade, depende da escala.

### 15.6 RMSE e a ordem entre as métricas (fora dos slides)

Os slides 49 a 54 **não** apresentam o RMSE (o slide 55 é só imagem, não conferido, e pode trazer algo que eu não vi). O RMSE é a raiz do MSE e traz o erro de volta à unidade de Y:

```
RMSE = √MSE        no exemplo: √84,2 ≈ 9,18 mil reais
```

Vale RMSE ≥ MAE, com igualdade só se todos os erros forem do mesmo tamanho. No exemplo, MAE = 5,8 e RMSE = 9,18: a distância grande entre eles denuncia a presença de um erro extremo (o 20).

### 15.7 Quarto trecho de scikit-learn (executado): métricas

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

y_real = np.array([10, 20, 30, 40, 100])
y_prev = np.array([12, 18, 33, 38, 80])

print(mean_absolute_error(y_real, y_prev))        # 5.8
print(mean_squared_error(y_real, y_prev))         # 84.2
print(mean_squared_error(y_real, y_prev) ** 0.5)  # RMSE aprox. 9.18 (conta manual)
print(r2_score(y_real, y_prev))                   # aprox. 0.9158
```

Atenção: a ordem dos argumentos é sempre `(y_real, y_previsto)`. Em `r2_score`, trocar a ordem altera o resultado.

### 15.8 Slide 55

O slide 55 contém **quatro imagens** e nenhum texto extraído, então seu conteúdo não foi conferido por este texto. Se, na aula, ele resume as fórmulas das métricas acima, elas já estão cobertas nas seções 15.1 a 15.5.

### Tabela-resumo das métricas

| Métrica | Mede | Unidade | Sensível a outlier | Observações |
| :-- | :-- | :-- | :-- | :-- |
| SQR | erro total ao quadrado | Y ao quadrado | muito | cresce com n |
| MAE | erro médio em módulo | **a de Y** | pouco | mais fácil de interpretar |
| MSE | erro médio ao quadrado | Y ao quadrado | muito | compare só com MSE de outro modelo |
| RMSE (fora dos slides) | raiz do MSE | a de Y | muito | RMSE ≥ MAE |
| R² | % da variação explicada | sem unidade | depende | slide: 0 a 1; literatura: pode ser negativo |
| R² ajustado | R² penalizado por nº de variáveis | sem unidade | depende | compara modelos com número diferente de variáveis |

(MAE e MSE dividem por n, por isso permitem comparar bases de tamanhos diferentes; a SQR não.)

---

## 16. Armadilhas de prova e revisão final

1. **Pearson e r = 0:** só diz "sem relação linear". Correlação não é causalidade.
2. **Onde buscar correlação (slide 8):** forte entre X e Y; baixa entre os X (multicolinearidade).
3. **X só tem números (slide 5); β é vetor; α é a constante.**
4. **Padronização (slide 19):** serve para comparar β; em Ridge e Lasso afeta o resultado; no teste, só `transform`.
5. **MQO × GD:** MQO não é iterativo (fórmula direta), bom para poucas variáveis; GD é iterativo, melhor com muitas dimensões. **Complexidade:** slide 22 = linear (dobrar instâncias dobra o tempo); literatura = cúbico no nº de colunas.
6. **Gradiente descendente:** passo = taxa × derivada; derivada positiva -> diminui o parâmetro; derivada negativa -> aumenta. Hiperparâmetros: taxa e nº de iterações.
7. **Taxa:** muito baixa = lenta (pode terminar antes de convergir); muito alta = passa do mínimo, oscila, diverge. Slide 40 diz "mínimo local" (resposta da professora); a literatura diz oscilar ou divergir. Valores usuais do slide 40: 0,001 a 0,3. "Baixa" é relativo.
8. **Regularização:** Ridge (L2) encolhe e não zera; Lasso (L1) zera e seleciona features; ambas combatem overfitting. `alpha` do scikit-learn = λ.
9. **Métricas:** MAE na unidade de Y; MSE na unidade ao quadrado e penaliza erros grandes; não comparar MSE com MAE (slide: "sempre maior"; realidade: depende da escala e das unidades); RMSE ≥ MAE.
10. **R²:** slide 0 a 1; literatura pode ser negativo (pior que a média). **R² ajustado** compara modelos com números diferentes de variáveis.
11. **Regressão linear é o baseline** (slide 48): simples, rápida, explicável.

### Cobertura por slide

Slides 1 e 2 (título), 3 (seção 1), 4 a 6 (seção 2), 7 (3), 8 e 9 (4), 10 e 11 (5), 12 (6), 13 a 17 (7), 18 e 19 (8), 20 a 22 (9), 23 a 25 (10), 26 a 35 (11), 36 (11.5), 38 a 44 (12), 45 e 46 (13), 47 e 48 (9.3 e 14), 49 a 55 (15). Só imagem, não conferidos: 14, 16, 17, 21, 25, 27, 37, 55 e as figuras dos demais.
