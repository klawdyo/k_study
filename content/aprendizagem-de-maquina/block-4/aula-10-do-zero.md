# Aula 10 do zero: Redes Neurais (Perceptron e MLP)

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e um exemplo concreto, depois com o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção). Os 52 slides da Aula 10 estão todos mapeados na tabela abaixo; os que só têm figura foram abertos e descritos (seção "Slides que só têm figura").

**A pergunta que a aula inteira responde:** *como um programa pode ajustar sozinho milhares de números (pesos) até que sua saída fique parecida com a resposta certa?*

Analogia de software: pense numa função gigante com milhares de parâmetros (`config`) e uma suíte de testes que diz o quão errada a saída está. Treinar uma rede neural é um laço automático que **mexe nos parâmetros um pouquinho de cada vez, na direção que diminui o erro dos testes**. Todo o resto da aula (neurônio, perceptron, MLP, backpropagation, gradiente, ativação, regularização) é detalhe de como fazer isso bem.

---

## Cobertura por slide

Legenda: **T** = o slide tem texto e está coberto; **F** = o slide só tem figura (arquivo-fonte aberto, figura descrita na seção indicada); **T+F** = texto e figuras.

| Slide | Assunto | Tipo | Seção deste texto |
| :-- | :-- | :-- | :-- |
| 1 | Capa (professora) | T | cabeçalho |
| 2 | Título: Redes Neurais, Perceptron | T | cabeçalho |
| 3 | Neurônios biológicos (bilhões de neurônios, sinapses) | T | 1 |
| 4 | Funcionamento: corpo, axônio, dendritos | T+F | 1 |
| 5 | Plasticidade | T | 1 |
| 6 | Redes neurais artificiais: unidades, camadas, pesos | T+F | 2 |
| 7 | Neurônio MCP (McCulloch e Pitts, 1943) | T+F | 3 |
| 8 | MCP: n entradas, uma saída, pesos | T+F | 3 |
| 9 | MCP: função de ativação, "não aprende" | T+F | 3 |
| 10 | Perceptron de Rosenblatt (1958), linearmente separável | T+F | 4 |
| 11 | Aprendizado = ajustar pesos pelo erro | T | 5 |
| 12 | Correção de erro: e = Yd − Y, regra de atualização | T | 5 |
| 13 | Exemplo: tabela entradas e saídas | F | 6 |
| 14 | Codificar entradas e saída | F | 6 |
| 15 | Inicialização (pesos em [0;1], taxa 0.3) | T | 6 |
| 16 | 1ª iteração | F | 6 |
| 17 | 2ª iteração (erro 0) | F | 6 |
| 18 | Limitação: só problemas lineares; camadas intermediárias | T+F | 7 |
| 19 | MLP: camadas tomando decisões mais abstratas | T+F | 8 |
| 20 | MLP: um perceptron tem uma só saída | T+F | 8 |
| 21 | MLP: o erro só existe na saída (Yd = ?) | T+F | 9 |
| 22 | Backpropagation (1986): responsabilidade pelo erro | T | 9 |
| 23 | Backpropagation: fase Forward | T | 10 |
| 24 | Backpropagation: fase Backward, regra da cadeia, convergência | T | 10 |
| 25 | Função de custo quadrático (MSE), minimizar C(w, b) | T+F | 11 |
| 26 | Gradiente descendente: definição | T+F | 12 |
| 27 | Gradiente: analogia do vale e da bola | T+F | 12 |
| 28 | Gradiente: derivadas dizem a forma do vale | T+F | 12 |
| 29 | Derivada: inclinação da reta tangente | F+T | 13 |
| 30 | Derivada: sinal; vetor gradiente | T+F | 13 |
| 31 | Como funciona (1): valores iniciais e custo | T | 14 |
| 32 | Como funciona (2): derivada e taxa alfa | T | 14 |
| 33 | Como funciona (3): repetir até custo ≈ 0 | T | 14 |
| 34 | Mini-Batch Gradient Descent | T | 15 |
| 35 | Hiperparâmetros da rede | T | 16 |
| 36 | Otimizador do peso: GD, SGD, Adam | T | 16 |
| 37 | Regularização: por quê | T | 17 |
| 38 | Parada antecipada | T | 17 |
| 39 | Regularização L1 e L2 (mecanismo) | T | 17 |
| 40 | L2 (Ridge), L1 (Lasso), Dropout | T | 17 |
| 41 | Taxa de aprendizado: pequena demais, grande demais | T+F | 18 |
| 42 | Ativação: por que (pequena mudança, pequena saída) | T+F | 19 |
| 43 | Ativação: o degrau muda tudo de uma vez | T | 19 |
| 44 | Ativação: decidem se o neurônio ativa | T+F | 19 |
| 45 | Ativação: sem ela, é regressão linear | T | 19 |
| 46 | Degrau (binary step) | T+F | 20 |
| 47 | Linear (a figura é o catálogo de gráficos de ativação) | T+F | 20 |
| 48 | Sigmoide | T+F | 20 |
| 49 | ReLU | T+F | 20 |
| 50 | Softmax | T | 20 |
| 51 | Escolhendo a função de ativação | T | 21 |
| 52 | Tabela função de custo × ativação de saída | T | 22 |

Resumo: **52 de 52 slides cobertos**; 4 slides são só figura (13, 14, 16 e 17) e foram lidos nas imagens; nenhum ficou sem leitura. Os trechos marcados "exemplo nosso" e os de código **não estão nos slides** (são para você entender e para a prova de código).

Outras seções do texto: 23 (código com NumPy e scikit-learn), 24 (afirmações verdadeiras e falsas), 25 (resumo de véspera).

---

## 1. Do neurônio biológico (slides 3, 4 e 5)

**Slide 3.** O slide cita o livro de Ben Coppin (cap. 11): o cérebro tem **bilhões de neurônios**, cada um ligado, em média, a **milhares de outros**; essas ligações são as **sinapses** e o cérebro teria cerca de **60 e tantos trilhões** delas.

**Slide 4.** Um neurônio tem **corpo** (também chamado de **soma**), **axônio** e vários **dendritos**:

- **Dendritos** recebem os impulsos nervosos dos outros neurônios e os levam ao corpo. São os **terminais de entrada**.
- O **corpo** processa os impulsos recebidos e gera um novo impulso. É um processamento simples.
- Se o novo impulso for **suficientemente alto**, ele é repassado a outros neurônios pelo **axônio**, o **terminal de saída**.

Figura do slide 4 (vista no arquivo-fonte): desenho de um neurônio com os rótulos Dendritos, Corpo, Axônio e Terminais sinápticos, com uma seta indicando a direção do impulso, do corpo para os terminais.

Analogia de software: dendritos são os **parâmetros de entrada** de uma função, o corpo é o **corpo da função** (soma e decide) e o axônio é o **return**. Só que a função precisa de um "if" no final: só retorna sinal forte se a soma passar de um limite.

**Slide 5: plasticidade.** O cérebro aprende porque os neurônios podem **modificar a natureza das conexões** com outros neurônios em resposta a eventos novos. Assim, o cérebro **reforça** conexões que levam a soluções corretas e **enfraquece** as que levam a soluções incorretas. Essa propriedade se chama **plasticidade**.

A ponte para o resto da aula: na rede artificial, "reforçar" ou "enfraquecer" uma conexão é **aumentar ou diminuir um número** (o peso). **Aprender = ajustar pesos.**

> **Se perguntarem na prova:** a propriedade biológica que inspira o aprendizado das redes é a **plasticidade**; dendritos = entrada, corpo (soma) = processamento, axônio = saída; sinapses = conexões que viram **pesos** na rede artificial.

---

## 2. Redes neurais artificiais (slide 6)

**Slide 6.** Redes neurais artificiais (RNA) são **programas** formados por **unidades de processamento simples (neurônios)** que calculam **funções matemáticas** para simular o modelo biológico. As unidades ficam em **uma ou mais camadas** e são ligadas por **muitas conexões**. As conexões têm **pesos** que **armazenam o conhecimento adquirido** pela rede e **ponderam a entrada** recebida por cada neurônio.

Figura do slide 6 (vista): rede com **camada de entrada** (2 círculos cinza), duas **camadas intermediárias** (4 círculos vermelhos cada) e **camada de saída** (1 círculo cinza), com linhas rotuladas "conexões" ligando cada neurônio a todos os da camada seguinte.

Pontos que o slide deixa explícitos e que dá para virar pergunta:

| Afirmação do slide | O que significa |
| :-- | :-- |
| Neurônios são unidades simples | Cada um só faz uma soma ponderada e uma função |
| Organizados em camadas | Entrada, intermediárias (ocultas) e saída |
| Os pesos armazenam o conhecimento | O "modelo treinado" é, essencialmente, o conjunto de pesos |

Analogia de software: a rede é um **grafo de funções minúsculas**; o "conhecimento" não está no código (que é igual para todo mundo), está nos **valores das variáveis de configuração** (os pesos).

---

## 3. O neurônio MCP (slides 7, 8 e 9)

**Slide 7.** O primeiro modelo de neurônio artificial foi definido por **McCulloch e Pitts em 1943**; por isso se chama **neurônio MCP**.

**Slide 8.** O modelo tem **n terminais de entrada** (dendritos) x₁, x₂, …, xₙ e **apenas uma saída** y (axônio). Para representar as sinapses, cada entrada tem um **peso** w₁, w₂, …, wₙ, que determina **em que grau aquela informação deve ser considerada**. A **configuração dos pesos é o que armazena o conhecimento** e simula a plasticidade.

**Slide 9.** O neurônio biológico é ativado quando a soma dos impulsos **ultrapassa um limiar**. Para representar isso usa-se uma **função de ativação**, que ativa ou não a saída dependendo do valor. E o ponto que o slide destaca: **o MCP não aprende**. Não há algoritmo de aprendizado; para mudar o comportamento, **um humano** precisa redesenhar os pesos e o limiar **manualmente**.

Figuras (vistas): o slide 8 mostra x₁ … xₙ com pesos w₁ … wₙ entrando em um círculo com Σ, produzindo u; depois uma caixa f(u) com uma curva em S, produzindo y. O slide 9 mostra um neurônio de duas entradas (X₁, X₂, pesos W₁, W₂), o círculo dividido em **u** (somatório) e **f(u)** (ativação), saída **Y**, com a fórmula u = Σ xᵢ·wᵢ.

Em código, o MCP é isto (exemplo nosso):

```
def neuronio(entradas, pesos, limiar):
    u = sum(x * w for x, w in zip(entradas, pesos))   # somatório
    return 1 if u >= limiar else 0                     # função de ativação
```

Os pesos e o limiar são **constantes escritas por você**. Se o resultado estiver errado, quem corrige é o programador. Isso é "não aprende".

> **Se perguntarem na prova:** MCP = entradas × pesos, soma, função de ativação (limiar); **sem algoritmo de aprendizado**; ajuste **manual**. Quem acrescentou aprendizado foi o Perceptron.

---

## 4. O Perceptron simples (slide 10)

**Slide 10.** **Frank Rosenblatt, 1958**, propôs um **algoritmo de aprendizagem por correção do erro** para os neurônios MCP. O modelo é o **Perceptron simples**, porque tem **apenas uma camada de neurônios MCP** (não há camadas intermediárias). Rosenblatt **demonstrou** que um neurônio MCP treinado com o algoritmo do Perceptron **sempre aprende quando o problema é linearmente separável**.

**Linearmente separável** quer dizer: dá para separar as duas classes com **uma reta** (em 2 dimensões; em mais dimensões, um plano ou "hiperplano").

Figura do slide 10 (vista): plano com pontos azuis (embaixo, à esquerda) e vermelhos (em cima, à direita), com uma reta verde inclinada separando os dois grupos sem nenhum erro. É a imagem típica de "problema linearmente separável".

Resumo da relação entre os dois modelos (a diferença entre eles é pergunta clássica):

| | MCP (1943) | Perceptron simples (1958) |
| :-- | :-- | :-- |
| Estrutura | entradas, pesos, soma, ativação | a mesma, em **uma camada** |
| Aprende sozinho | **não** | **sim**, por correção de erro |
| Quem ajusta os pesos | humano | o algoritmo |
| Garantia | nenhuma | aprende **se** o problema é linearmente separável |

> **Se perguntarem na prova:** "Perceptron simples = MCP + algoritmo de aprendizagem por correção de erro, com uma única camada; aprende sempre que as classes são linearmente separáveis."

---

## 5. Como o Perceptron aprende: correção de erro (slides 11 e 12)

**Slide 11.** O conhecimento da rede é adquirido pelo **ajuste da intensidade das conexões**, ou seja, **pelo ajuste dos pesos**. Para saber como ajustar, usa-se **o erro da rede nos dados de treinamento**, modificando os pesos para **diminuir o erro**.

**Slide 12: aprendizado por correção de erro.** Depois que a rede dá uma saída, calcula-se o erro:

```
e = Yd − Y
```

Yd é a saída **desejada (correta)** e Y é a saída **fornecida** pela rede. Depois ajustam-se os pesos:

```
Wi_novo = Wi_atual + n · e · Xi
```

- **n** é a **taxa de aprendizagem**: a proporção de ajuste do peso.
- A taxa deve ser **sempre pequena**: ajustes em passos pequenos, **para evitar aprender ruídos**.
- **e** é o erro; **x** é a entrada **associada ao peso que está sendo ajustado**.

**Por que a fórmula faz sentido** (leia com calma, é a ideia central):

- Se acertou, e = 0, então n·e·Xi = 0 e **o peso não muda**.
- Se a saída devia ser 1 e foi 0, e = +1: o peso **sobe** (se Xi > 0), então a soma da próxima vez será maior, empurrando a saída para 1.
- Se a saída devia ser 0 e foi 1, e = −1: o peso **desce**, empurrando para 0.
- Se Xi = 0, a entrada não participou da soma, então **seu peso não tem culpa e não muda**.

Analogia de software: é como um teste que falha e **só ajusta o parâmetro que contribuiu** para a falha, e ajusta "um tiquinho" (n) para não estragar os outros casos.

**Exemplo numérico nosso** (um perceptron, uma entrada, uma atualização). Entradas x = (2, 1), pesos w = (0.5, −0.4), bias b = 0.1, taxa n = 0.1, saída desejada Yd = 0, ativação degrau (z ≥ 0 dá 1).

```
z = 2·0.5 + 1·(−0.4) + 0.1 = 0.7      -> Y = 1
e = Yd − Y = 0 − 1 = −1               (a rede errou: previu 1, devia ser 0)
w1_novo = 0.5 + 0.1·(−1)·2 = 0.3
w2_novo = −0.4 + 0.1·(−1)·1 = −0.5
b_novo  = 0.1 + 0.1·(−1)   = 0.0
z depois = 2·0.3 + 1·(−0.5) + 0.0 = 0.1   (caiu de 0.7 para 0.1: foi na direção certa)
```

Com uma única correção o z caiu de 0.7 para 0.1, mas ainda é ≥ 0 e a saída ainda seria 1. Isso é normal: a taxa é pequena, e o algoritmo **repete** muitas vezes (por isso se fala em iterações e épocas).

**Sobre o bias.** O slide 12 só mostra a regra para os pesos Wi. A figura do slide 21 (vista na seção 9) mostra também o **bias** b somado à soma ponderada e a regra do bias: `Novo_bias = bias + (taxa de aprendizado · erro)`, que é a mesma regra tratando o bias como um peso cuja entrada é sempre 1. Analogia: o bias é o "valor padrão" da soma, a constante do `ax + b`; ele desloca o ponto em que o neurônio dispara.

> **Se perguntarem na prova:** erro = desejada − obtida; novo peso = peso atual + taxa × erro × entrada; a taxa deve ser **pequena** para não aprender ruído; se não há erro, o peso não muda.

---

## 6. O exemplo trabalhado do slide (slides 13 a 17)

O exemplo ensina o Perceptron a separar **compositores** de **cientistas**. Não precisa decorar os números: o objetivo é você ver o ciclo.

**Slide 13 (figura, vista).** Tabela Entradas × Saídas: **Bach** → Compositor; **Beethoven** → Compositor; **Einstein** → Cientista; **Kepler** → Cientista.

**Slide 14 (figuras, vistas): primeiro passo, codificar.** O computador só entende números. Os nomes viram códigos decimais **0, 1, 2, 3** (Bach, Beethoven, Einstein, Kepler) e depois **binário** em duas colunas, X₁ e X₂: Bach = (0, 0); Beethoven = (0, 1); Einstein = (1, 0); Kepler = (1, 1). A saída vira um número: Compositor = **0**, Cientista = **1** (coluna Y). Resultado: as saídas desejadas são Yd = 0 para (0,0) e (0,1), e Yd = 1 para (1,0) e (1,1).

Analogia de software: é o *encoding* de entrada (como converter enum em inteiro). Observação nossa: esse tipo de codificação é artificial (nada em "Einstein = 10" faz sentido), serve só para ensinar o algoritmo.

**Slide 15: inicialização.** Pesos iniciais **aleatórios**, com o intervalo **[0; 1]** citado como comum. Taxa de aprendizado **pequena**; **0.3** é "um bom exemplo". (No exemplo das próximas tabelas, os pesos começam em 0, o caso mais simples.)

**Slide 16 (figura, vista): 1ª iteração.** A tabela tem colunas X₁, X₂, W₁, W₂, Σ, Y, Yd, e. A saída vale **1 se Σ xᵢwᵢ > 0** e **0 se Σ xᵢwᵢ ≤ 0**. O erro da iteração é **Erro = Σ|e|** (soma dos erros em módulo). Linha a linha, com taxa 0.3:

| X₁ | X₂ | W₁ | W₂ | Σ | Y | Yd | e | o que acontece |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | 1 | 0 | 0 | 0 | 0 | 1 | +1 | errou; pesos viram 0.3 e 0.3 |
| 1 | 0 | 0.3 | 0.3 | 0.3 | 1 | 1 | 0 | acertou; sem mudança |
| 0 | 1 | 0.3 | 0.3 | 0.3 | 1 | 0 | −1 | errou; W₁ fica 0.3 e W₂ cai para 0 |
| 0 | 0 | 0.3 | 0 | 0 | 0 | 0 | 0 | acertou |

No final da 1ª iteração, **Erro = 2** (duas linhas erradas). As contas de atualização aparecem no slide: `0 + 0.3·1·1 = 0.3` (para os dois pesos na primeira linha) e `0.3 + 0.3·(−1)·0 = 0.3` e `0.3 + 0.3·(−1)·1 = 0` (terceira linha). Repare: na linha (0,1), o W₁ **não muda** porque X₁ = 0.

**Slide 17 (figura, vista): 2ª iteração.** Com W₁ = 0.3 e W₂ = 0, as quatro linhas dão e = 0 e **Erro = 0**: **convergiu**. O Perceptron aprendeu (na prática, ele descobriu que a resposta depende só de X₁).

Eu reproduzi essa tabela em código (executado; o resultado bate com o slide: erro 2 na 1ª época, erro 0 na 2ª, pesos finais 0.3 e 0):

```python
import numpy as np

# Perceptron do slide 15-17: pesos iniciais 0, taxa 0.3, degrau (soma > 0 -> 1)
X = np.array([[1,1],[1,0],[0,1],[0,0]])
Yd = np.array([1,1,0,0])
w = np.array([0.0, 0.0])
eta = 0.3

def prever(x, w):
    return 1 if x @ w > 0 else 0

for epoca in range(1, 4):
    erro_total = 0
    for x, yd in zip(X, Yd):
        soma = x @ w
        y = prever(x, w)
        e = yd - y
        w = w + eta * e * x
        erro_total += abs(e)
        print(f"  x={x} soma={soma:.1f} y={y} yd={yd} e={e:+d} -> w={np.round(w,2)}")
    print(f"época {epoca}: erro = {erro_total}, w = {np.round(w,2)}")
    if erro_total == 0:
        break
```

Saída que obtive: na época 1 os pesos terminam em `[0.3 0.]` com erro 2; na época 2, erro 0.

**Vocabulário que este exemplo ensina** (e não está escrito nos slides, é nosso): uma passada por **todos** os exemplos de treino é uma **época (epoch)**; o algoritmo para quando o erro da época chega a zero (convergência).

> **Se perguntarem na prova:** "O Perceptron para de ajustar quando o erro total de uma passada completa é zero." E: "se o peso está associado a uma entrada 0, ele não é alterado naquela linha."

---

## 7. A limitação do Perceptron (slide 18)

**Slide 18.** As redes de **uma única camada** só resolvem problemas **com características lineares**. Para aprender problemas **não lineares** são necessárias **camadas intermediárias**, porque são elas que dão à rede a capacidade de aprender problemas complexos. E isso vem **associado ao uso de funções de ativação não lineares**.

Figura do slide 18 (vista): o mesmo tipo de gráfico do slide 10, mas agora com pontos vermelhos e azuis misturados de forma que a fronteira verde é uma **curva** (uma espécie de "gancho"), não uma reta. Mensagem: uma reta não separa; é preciso uma fronteira curva.

**Explicação do zero.** Um Perceptron faz, no fundo, `se (w1·x1 + w2·x2 + b) ≥ 0`. Isso desenha **uma reta** no plano. Qualquer problema em que as classes só se separam com curva fica fora do alcance dele.

O exemplo clássico (que **não está nos slides**; é exemplo nosso e muito citado na literatura) é o **XOR** ("ou exclusivo"):

```
x1 x2 | AND  OR  XOR
 0  0 |  0    0    0
 0  1 |  0    1    1
 1  0 |  0    1    1
 1  1 |  1    1    0
```

AND e OR podem ser separados por uma reta. XOR não: os pontos que valem 1 ficam em cantos opostos do quadrado. Eu rodei no scikit-learn (código executado, seção 23): o `Perceptron` acertou 100% em AND e OR e ficou em 50% no XOR.

A frase de Minsky e Papert (1969) sobre o assunto **não aparece nos slides**; se quiser guardar: foi o livro que popularizou essa limitação (informação da literatura, não da aula).

> **Se perguntarem na prova:** "Por que o Perceptron simples não resolve problemas não lineares?" Porque produz **fronteira linear** e só tem **uma camada**. Solução: **camadas intermediárias + ativação não linear** (as duas coisas juntas; só uma não basta).

---

## 8. A rede de Perceptrons de múltiplas camadas: MLP (slides 19 e 20)

**Slide 19.** Na figura, a primeira coluna de perceptrons (primeira camada) toma **três decisões muito simples, pesando a evidência de entrada**. Na segunda camada, cada perceptron decide **ponderando os resultados da primeira camada**, então pode decidir num nível **mais complexo e mais abstrato**. Na terceira camada, decisões **ainda mais complexas**. Assim, uma rede de várias camadas faz **tomada de decisão sofisticada**.

Figura do slide 19 (vista): entradas à esquerda; **1ª camada neural escondida** com n₁ neurônios; **2ª camada neural escondida** com n₂ neurônios; **camada neural de saída** com m neurônios; todos de uma camada ligados a todos da seguinte; rótulos "Entradas do PMC" e "Saídas do PMC". (PMC é a sigla em português de MLP.)

**Slide 20.** Um perceptron tem **apenas uma saída**. As **várias setas** saindo dele são só uma forma de mostrar que **a mesma saída é usada como entrada de vários outros perceptrons**. Figura (vista): rede "inputs → duas camadas → output".

Analogia de software: um **pipeline de transformações**. A 1ª camada extrai sinais simples dos dados brutos (como pegar o comprimento e a quantidade de dígitos de uma string), a 2ª combina esses sinais ("parece um CPF"), a 3ª combina os combinados ("é um documento válido?"). Exemplo nosso.

Vocabulário (nomes, não decorar números):

| Termo | O que é |
| :-- | :-- |
| camada de entrada | recebe os atributos; não calcula nada, só distribui |
| camadas intermediárias (ocultas, escondidas, hidden) | meio da rede; não se vê a saída desejada delas |
| camada de saída | produz a resposta final |
| MLP ou PMC | Perceptron de Múltiplas Camadas (Multilayer Perceptron) |

> **Se perguntarem na prova:** "um neurônio tem uma única saída; as várias setas indicam reaproveitamento da mesma saída em vários neurônios da camada seguinte."

---

## 9. O problema de treinar camadas ocultas e o backpropagation (slides 21 e 22)

**Slide 21.** Em redes de **uma camada**, o erro vem **direto** da diferença entre a saída desejada e a corrente. Em **múltiplas camadas**, esse procedimento só vale para a **camada de saída**, já que **não existe saída desejada** para as camadas intermediárias. O problema passa a ser **como estimar o erro das camadas intermediárias** (no slide aparecem as duas fórmulas, `Wi_novo = Wi_atual + n·e·Xi` e `e = Yd − Y`, e um "Yd = ?" sobre uma rede com 2 camadas ocultas).

Figuras do slide 21 (vistas): (1) uma rede com 4 entradas, **camada oculta #1** (5 neurônios), **camada oculta #2** (5 neurônios) e uma **saída**, com "Pesos" entre as camadas; (2) o diagrama detalhado de um perceptron: entradas X1 e X2 com pesos W1 e W2, um **bias b** entrando no somatório `z = Σ(Xi·Wi) + b`, **função degrau** (1 se z ≥ 0; 0 se z < 0), `erro = esperado − previsão`, e três regras de atualização: `Novo_W1 = W1 + (taxa · erro) · X1`, `Novo_W2 = W2 + (taxa · erro) · X2`, `Novo_bias = bias + (taxa · erro)`.

Analogia: você sabe qual **resultado final** do sistema está errado (o teste de integração falhou), mas **não sabe qual módulo no meio da cadeia** introduziu o erro. Não há um "teste unitário" para a camada intermediária.

**Slide 22: a solução, backpropagation (1986, David Rumelhart).** O princípio: o erro da **camada de saída é calculado e repassado para as camadas intermediárias**, permitindo ajustar os pesos **proporcionalmente aos valores das conexões entre as camadas**.

- **Conexão forte (peso grande):** o neurônio teve **grande responsabilidade** no erro final, então o ajuste no peso dele será **grande**.
- **Conexão fraca (peso pequeno):** quase não influenciou, então o ajuste será **pequeno**.

Analogia: **post-mortem de incidente**. Quem mais contribuiu para o erro (maior peso) leva a maior correção. O erro **volta andando pelos mesmos caminhos** por onde o sinal foi.

> **Se perguntarem na prova (divergência slide × literatura):** o slide explica "ajuste proporcional ao peso da conexão" para dar a intuição. Na literatura, o ajuste vem da **derivada do erro em relação ao peso** (regra da cadeia), que depende do peso da conexão **e também** da derivada da função de ativação e da entrada. Na prova, responda com a versão do slide (responsabilidade proporcional ao peso); a versão da literatura é a explicação completa. O backpropagation **calcula os gradientes**; quem **usa** o gradiente para mudar os pesos é o otimizador (seção 16). O slide 24 mistura os dois quando diz que isso "pode ser feito com qualquer algoritmo de otimização baseado em gradiente".

---

## 10. As duas fases do backpropagation (slides 23 e 24)

**Slide 23: fase Forward ("para frente"), semelhante ao Perceptron.** Serve para **definir a saída da rede** para um dado padrão:

1. A entrada é apresentada à rede.
2. Cada neurônio calcula o **somatório** e aplica a **função de ativação (não linear)**; a saída dele serve de entrada aos neurônios da camada seguinte.
3. As saídas da última camada são **comparadas às desejadas** para calcular o **erro da camada de saída**.

**Slide 24: fase Backward ("para trás").** Usando o **backpropagation** e a **regra da cadeia (chain rule)**, as **derivadas parciais da função de erro** em relação aos vários **pesos e bias** são propagadas de volta pela MLP. Essa diferenciação dá um **gradiente**, ao longo do qual os parâmetros podem ser ajustados, movendo a MLP **um passo mais perto do erro mínimo**. Isso pode ser feito com **qualquer algoritmo de otimização baseado em gradiente**, como a **descida estocástica do gradiente**. O processo continua **até o erro não poder mais ser reduzido**; esse estado é a **convergência**.

| | Forward | Backward |
| :-- | :-- | :-- |
| Direção | entrada → saída | saída → entrada |
| O que calcula | somas, ativações, a **previsão** e o erro da saída | **derivadas** do erro em relação a cada peso e bias |
| Usa | pesos atuais, função de ativação | regra da cadeia |
| Resultado | previsão | gradiente, usado para atualizar os pesos |

**Regra da cadeia, sem cálculo.** Se o erro depende da saída, a saída depende da camada oculta e a camada oculta depende de um peso, então **o efeito do peso no erro é o produto dos efeitos de cada etapa**. Analogia: é o encadeamento de `f(g(h(x)))`: para saber como uma mudança em `x` afeta o resultado final, multiplica-se a "sensibilidade" de cada função da cadeia (é o que um *profiler* faz ao atribuir custo ao longo de uma pilha de chamadas). Os frameworks (TensorFlow, PyTorch) fazem isso automaticamente.

**Exemplo numérico nosso: um MLP pequeno, da entrada à saída.** Rede 2-2-1 (duas entradas, duas ocultas, uma saída). Para você *ver* um MLP funcionando, vou usar **ReLU** nas ocultas e pesos escolhidos à mão para resolver o XOR (não é treino, é só a passagem forward):

```
Entrada (x1, x2) -> oculta h1 = ReLU(x1 + x2)
                    oculta h2 = ReLU(x1 + x2 − 1)
                    saída  y  = h1 − 2·h2

(0,0): h1=0, h2=0       -> y = 0
(0,1): h1=1, h2=0       -> y = 1
(1,0): h1=1, h2=0       -> y = 1
(1,1): h1=2, h2=1       -> y = 2 − 2 = 0
```

Saída: **0, 1, 1, 0 = XOR**. Uma só camada não faz isso; duas camadas com **ReLU** fazem. Agora, **tirando a ReLU** (rede só com somas), as mesmas contas viram `y = −x1 − x2 + 2`, uma função **linear**: dá 2, 1, 1, 0, que **não** é XOR. É a demonstração do slide 45 (seção 19).

Código (executado):

```python
import numpy as np
relu = lambda z: np.maximum(0, z)
W1 = np.array([[1,1],[1,1]]); b1 = np.array([0,-1])
W2 = np.array([1,-2]); b2 = 0
for x in [(0,0),(0,1),(1,0),(1,1)]:
    x = np.array(x); h = relu(W1 @ x + b1); y = W2 @ h + b2
    print(x, "oculta =", h, "saida =", y)
Wlin = W2 @ W1; blin = W2 @ b1 + b2      # a mesma rede sem a ReLU colapsa
print("colapso linear:", Wlin, blin)      # [-1 -1] 2
```

**Um passo completo de treino (forward + backward), exemplo nosso.** Rede 2-2-1 com **sigmoide** em tudo, uma amostra x = (1, 0), saída desejada Yd = 1, custo `½(y − Yd)²`, taxa 0.5. Pesos iniciais: camada oculta `[[0.5, 0.2], [−0.3, 0.8]]` com bias `[0.1, 0.1]`; saída `[0.6, −0.4]` com bias 0.05. Rodei o código (seção 23, bloco "um passo de treino"); resultado:

```
Forward : h = [0.6457, 0.4502]    y = 0.564    custo = 0.0951
Backward: gradiente dos pesos de saída = [−0.0692, −0.0483]
          gradiente de W1[0][0]       = −0.0147
Conferência por diferença finita: −0.0692 e −0.0147 (iguais)
Depois de atualizar os pesos: y = 0.586 e custo = 0.0857 (diminuiu)
```

Leitura: o gradiente é **negativo**, então o peso **sobe** (menos o negativo = mais); a saída foi de 0.564 para 0.586, **mais perto** do desejado 1. Note que o gradiente da camada oculta (−0.0147) é **menor** que o da saída (−0.0692): o erro chega "enfraquecido" em camadas mais antigas (ideia do desaparecimento do gradiente, seção 20). Um treino real repete isso milhares de vezes.

> **Se perguntarem na prova:** Forward = calcular a **previsão** (soma, ativação, até a saída); Backward = calcular os **gradientes** pela regra da cadeia e ajustar pesos e bias; convergência = quando o erro não diminui mais. "Na fase backward calculamos a previsão" é FALSO.

---

## 11. Função de custo (slide 25)

**Slide 25: função de custo quadrático.** Para quantificar o quanto estamos alcançando o objetivo, definimos uma **função de custo**. Em **regressão**, é comum o **erro quadrático médio (MSE, Mean Squared Error)**. O objetivo do algoritmo de treino é **minimizar o custo C(w, b)** em função dos **pesos e bias**, usando a **descida do gradiente (Gradient Descent)**.

Figura do slide 25 (vista): a fórmula `C(w, b) ≡ (1 / 2n) Σ ‖y(x) − a‖²`, soma sobre todos os exemplos x. Leitura em português: para cada exemplo, pegue a diferença entre a saída desejada y(x) e a saída da rede a, **eleve ao quadrado**, some tudo e divida por 2n (n = número de exemplos; o 2 é só uma conveniência para a derivada).

Analogia de software: a função de custo é **a nota do seu teste**: um único número que resume "quão errado está tudo". Treinar é **otimizar essa nota**. Ao quadrado para que erros grandes pesem muito e erros para cima e para baixo não se cancelem. (O motivo do quadrado é explicação nossa.)

O slide 25 só cita o MSE (regressão). As funções de custo para classificação (**entropia cruzada**) só aparecem na tabela do slide 52.

> **Se perguntarem na prova:** custo quadrático/MSE para regressão; o objetivo do treino é **minimizar** C(w, b); o método é a **descida do gradiente**.

---

## 12. Gradiente descendente: a bola no vale (slides 26, 27 e 28)

**Slide 26.** Gradiente descendente é um **algoritmo de otimização** para **minimizar funções**, movendo-se **iterativamente na direção da descida mais íngreme**, definida pelo **negativo do gradiente**. Em machine learning, usa-se para **atualizar os parâmetros do modelo**. Figura (vista): uma paisagem colorida em 3D (vermelho no alto, azul no fundo) com uma seta preta saindo de um ponto alto e descendo até um vale.

**Slide 27.** O objetivo: dada **uma função qualquer, encontrar um mínimo**. Para minimizar C(v), imagine C como função de **duas variáveis** v₁ e v₂, **um vale com uma bola rolando pela encosta**: escolhe-se aleatoriamente um ponto de partida e simula-se a bola rolando até o fundo. Figura (vista): superfície em forma de tigela, eixos v₁ e v₂ de −1 a 1, altura C de 0 a 2.

**Slide 28.** A simulação é feita **computando derivadas** de C: elas dizem tudo sobre a **forma local do vale** e portanto como a bola deve rolar. A descida do gradiente encontra os **valores dos parâmetros (coeficientes, ou w e b, weight e bias)** que **minimizam a função de custo**. Figura (vista): curva em U com o eixo J(w) e w, o rótulo "Initial weight" (peso inicial) no alto da encosta direita, uma reta tangente ("Gradient") e setas descendo até "Global cost minimum".

Analogia de software: é uma **busca às cegas por tentativa**: você não enxerga o vale todo, só a **inclinação do chão sob o pé**; dá um passo para onde o chão desce mais e repete. Parecido com ajustar um timeout sem saber o ótimo: se a latência piora ao aumentar, diminua; se melhora, continue.

> **Se perguntarem na prova:** a descida do gradiente se move na direção do **negativo do gradiente** (descida mais íngreme) para **minimizar** a função de custo, atualizando pesos e bias.

---

## 13. Derivada e gradiente (slides 29 e 30)

**Slide 29.** **Geometricamente**, a derivada no ponto x = a de y = f(x) é a **inclinação da reta tangente** ao gráfico no ponto (a, f(a)). O slide traz três figuras (vistas): (1) uma reta horizontal `y = c` com "inclinação = 0"; (2) uma reta `y = x` com "inclinação = 1"; (3) uma curva `f(x) = x·sin(x²) + 1` com a derivada `f'(x) = sin(x²) + 2x²·cos(x²)`, uma reta verde tangente na origem e alguns pontos marcados (como (1.3552, 2.3076) e (2.8137, 3.8081)).

**Slide 30.** A reta é sempre **tangente** à curva azul; a tangente do ângulo que ela faz com o eixo horizontal é a derivada. A derivada é **positiva** quando a reta está **verde**, **negativa** quando **vermelha** e **zero** quando **preta**. (A figura é uma animação; o quadro que vi mostra uma curva ondulada com uma reta vermelha descendente tangente num ponto.) Depois: o **vetor gradiente** indica **direção e sentido** para o qual se deve deslocar, a partir do ponto, para **o maior incremento** da grandeza medida.

Em palavras simples:

| Derivada no ponto | O que a curva faz ali | Para minimizar, ande |
| :-- | :-- | :-- |
| positiva | sobe (para a direita) | para a esquerda |
| negativa | desce (para a direita) | para a direita |
| zero | plana (topo, fundo ou platô) | você pode ter chegado a um mínimo |

O gradiente aponta para **onde sobe mais rápido**; por isso a descida usa o **negativo** do gradiente. Quando há **muitos parâmetros** (milhares de pesos), o gradiente é o **vetor** de todas as derivadas, uma por peso. Analogia: a derivada é a **taxa de variação** (`delta custo / delta peso`), como "quantos ms a mais a cada 1 KB a mais".

> **Se perguntarem na prova:** derivada = inclinação da tangente; gradiente = vetor que aponta para o maior **aumento**; por isso se anda no **sentido contrário** do gradiente.

---

## 14. Gradiente descendente passo a passo (slides 31, 32 e 33)

**Slide 31.** (1) Começa com **valores iniciais** para os coeficientes: **0.0** ou um **pequeno valor aleatório**. (2) Avalia o **custo** ligando os coeficientes à função: `coeficiente = 0,0; custo = f(coeficiente)`.

**Slide 32.** (3) Calcula a **derivada** da função de custo. (4) Para atualizar os coeficientes, especifica-se a **taxa de aprendizagem (alfa)**, que controla **quanto os coeficientes mudam** a cada atualização:

```
delta = derivada(custo)
coeficiente = coeficiente − (alfa · delta)
```

**Slide 33.** Repete-se **até o custo ser 0 ou próximo o bastante de 0**, indicando que as saídas previstas estão cada vez mais próximas das desejadas.

**Exemplo numérico nosso** (um parâmetro). Seja o custo `C(w) = (w − 3)²`; sua derivada é `2(w − 3)`; o mínimo está em w = 3. Comece com w = 0 e alfa = 0.1:

```
passo 1: derivada = 2(0 − 3) = −6    w = 0 − 0.1·(−6) = 0.6
passo 2: derivada = 2(0.6 − 3) = −4.8 w = 0.6 + 0.48 = 1.08
passo 3: derivada = 2(1.08 − 3) = −3.84 w = 1.08 + 0.384 = 1.464
... os passos vão diminuindo conforme chega perto do mínimo
```

A derivada negativa significa "a curva desce para a direita", então w **aumenta**. Perto do mínimo a derivada fica pequena, e os passos **encolhem sozinhos**. Rodei o laço (executado): depois de 20 passos com alfa = 0.1, w = 2.9654; com alfa = 0.001 (pequeno demais), w = 0.1177 (quase não saiu do lugar); com alfa = 1.1 (grande demais), w = −112.0 (**divergiu**, cada passo passa do mínimo e piora).

**Cuidado com o slide 33.** Dizer "repete até o custo ser zero" é a ideia; na prática o custo raramente chega a zero (os dados têm ruído) e o treino para quando **não melhora mais** (convergência, slide 24) ou por parada antecipada (seção 17).

> **Se perguntarem na prova:** a ordem do algoritmo: iniciar coeficientes, calcular custo, calcular derivada, atualizar com alfa, repetir. A taxa **alfa** controla o tamanho do passo. Atenção à **ordem** de um código: calcular o custo/derivada antes de atualizar; atualizar **subtraindo** (andar contra o gradiente).

---

## 15. Mini-batch (slide 34)

**Slide 34.** Os algoritmos mais atuais trabalham com **mini-lotes (mini-batches)**. Para otimizar a performance, passam-se **várias amostras pela rede** (por exemplo, **128**), calcula-se o **erro médio** delas e **então** faz-se o backpropagation e a atualização dos pesos. Do ponto de vista da atualização dos pesos, **1 amostra = 128 amostras**. É um conceito **mais novo**, necessário sobretudo no treinamento de grandes modelos de deep learning. A descida em mini-lotes é a **forma mais comum** de descida do gradiente em machine learning.

Comparação (as duas primeiras linhas são nossas, para dar contexto; a terceira é o slide 34):

| Variante | Quantas amostras por atualização | Observação |
| :-- | :-- | :-- |
| Batch (descida clássica, slide 36 fala em "todos os exemplos") | todas | passo estável, mas pesado |
| Estocástico (SGD, slide 36) | uma, ou "apenas alguns" (palavras do slide 36) | mais rápido, mais ruidoso |
| Mini-batch (slide 34) | um lote, ex.: 128 | o mais comum |

Com 1000 exemplos, batch faz 1 atualização por época; SGD de 1 amostra faz 1000; mini-batch de 128 faz 8 (exemplo nosso, executado).

Analogia de software: **processamento em lotes** em vez de transação por registro, ou **commit em lote** no banco: menos chamadas e mais eficiente, sem mudar o resultado final.

> **Se perguntarem na prova (divergência slide × literatura):** o slide 36 diz que o SGD calcula o erro "apenas para alguns exemplos"; na literatura, SGD "puro" usa **um** exemplo por atualização, e o que usa um lote é o mini-batch. Na prova, siga o slide: SGD = não usa todos os exemplos, é mais rápido; mini-batch = lote (ex.: 128), média do erro do lote, a forma mais comum.

---

## 16. Hiperparâmetros e otimizador (slides 35 e 36)

**Slide 35.** Ao construir uma rede, devem-se definir **hiperparâmetros**. Os principais, segundo o slide:

1. **Número de camadas**
2. **Número de neurônios em cada camada**
3. **Otimizador do peso** (a função que ajusta os pesos)
4. **Taxa de aprendizado**
5. **Função de ativação dos neurônios**

Hiperparâmetro é o que **você escolhe antes** de treinar (como `config`); **parâmetros** (pesos e bias) são o que **o treino descobre**. (Tamanho do lote e número de épocas são hiperparâmetros muito usados, mas **não estão nesta lista do slide**.)

**Slide 36: otimizador do peso.**

- **Gradiente Descendente:** a estratégia **mais antiga**; busca alterar os pesos para o menor erro, como no algoritmo backpropagation.
- **Gradiente Descendente Estocástico (SGD):** uma **evolução**, pois **não calcula o erro para todos os exemplos, mas apenas para alguns**, o que torna o ajuste **mais rápido**. O SGD mantém **uma única taxa de aprendizado para todas as atualizações de peso**, e ela **não muda durante o treinamento**.
- **Adam:** outro otimizador muito usado, **evolução do SGD**, onde **uma taxa de aprendizado é mantida para cada peso** e **adaptada separadamente** conforme o aprendizado evolui.

| Otimizador | Taxa de aprendizado |
| :-- | :-- |
| SGD | **uma só**, igual para todos os pesos e **fixa** |
| Adam | **uma por peso**, **adaptativa** |

Analogia: SGD é um **timeout global fixo**; Adam é um **timeout adaptativo por serviço**, que se ajusta ao comportamento de cada um.

> **Se perguntarem na prova:** "O SGD usa taxa de aprendizado individual para cada peso" é FALSO (isso é o **Adam**). "Os principais hiperparâmetros são número de camadas, neurônios por camada, otimizador, taxa de aprendizado e função de ativação."

---

## 17. Regularização (slides 37 a 40)

**Slide 37.** Redes com **muitas camadas (profundas)** têm **milhares e até milhões de parâmetros**, o que pode levar a **sobreajuste (overfitting)** nos dados de treino. Para evitar, usam-se técnicas de **regularização**, como a **parada antecipada** (com conjunto de validação) ou as **regularizações L1 e L2**.

Analogia: um sistema com milhões de "botões" consegue **decorar** os casos de teste (código com um `if` para cada teste). Regularizar é **limitar a liberdade** do modelo para ele aprender o padrão geral.

**Slide 38: parada antecipada (early stopping).** Uma parte do conjunto de treino é usada para **validar** o modelo, indicando **quando a rede começa a errar nesse conjunto enquanto acerta no de treino**. Interpretação: acompanha-se o erro de validação; quando ele **para de cair (ou sobe)** enquanto o erro de treino continua caindo, **pare o treino**. (A rede está começando a decorar.)

**Slide 39: L1 e L2 (mecanismo).** Buscam **restringir os pesos das conexões**, evitando valores muito altos; isso se faz **acrescentando um fator** à função de ajuste do peso, que **diminui o peso** (para variações cada vez mais altas). O fator é **diferente** em cada um:

- **L1:** os pesos diminuem em uma **quantidade constante**, tendendo a **0**.
- **L2:** os pesos diminuem em um valor **proporcional a w**.

**Slide 40: resumo.**

| Técnica | O que faz (slide 40) | Efeito |
| :-- | :-- | :-- |
| **L2 (Ridge)** | penaliza pesos grandes; penalidade **proporcional ao quadrado** dos pesos | **mantém todos os pesos, pequenos**; "não deixe nenhum parâmetro exagerado" |
| **L1 (Lasso)** | **faz alguns pesos virarem exatamente zero**; penalidade proporcional ao **valor absoluto** | ajuda a **selecionar features**; "se a variável não é importante, elimine" |
| **Dropout** | **desliga neurônios aleatoriamente** durante o treino | evita que a rede **dependa demais de conexões específicas** |

Para ver a diferença entre L1 e L2 (exemplo nosso, executado, peso w = 2.0, taxa 0.1, força 0.5, sem erro de dados): um passo com L2 dá `2.0 − 0.1·0.5·2.0 = 1.9` (encolhe **proporcional a w**: peso grande encolhe mais, e peso pequeno encolhe pouco, então nunca chega a zero); um passo com L1 dá `2.0 − 0.1·0.5·1 = 1.95` (encolhe **uma quantidade constante**, e por isso um peso pequeno chega a zero em poucos passos).

Dropout, o que **não está no slide** (explicação nossa): ao desligar neurônios aleatórios a cada passo, a rede não pode contar com um neurônio específico, e acaba aprendendo representações redundantes. Na hora de usar a rede treinada, os neurônios ficam todos ligados. A porcentagem de neurônios desligados (por exemplo, 20% ou 50%) é um hiperparâmetro; **o slide não cita números**.

**Sobre o L2 no scikit-learn** (nosso): o parâmetro `alpha` do `MLPClassifier` é a força da **penalidade L2**. Atenção ao nome: não é a taxa de aprendizado (que é `learning_rate_init`).

> **Se perguntarem na prova:** L2 mantém todos os pesos pequenos (não zera); **L1 zera pesos** e seleciona atributos; **Dropout** desliga neurônios aleatoriamente no treino; **early stopping** usa um conjunto de validação e para quando o erro de validação sobe. A afirmação invertida ("L1 mantém pesos pequenos e L2 zera pesos") é FALSA.

---

## 18. Taxa de aprendizado (slide 41)

**Slide 41.** O **learning rate** diz **qual a distância percorrida em cada iteração**. Se for **muito pequeno**, é **custoso computacionalmente** (demora a convergir); se for **muito grande**, pode **falhar em convergir no mínimo por passar dele**. Valores comuns: **0.001, 0.003, 0.01, 0.03, 0.1, 0.3**.

Figura do slide 41 (vista), com títulos em inglês: à esquerda "alpha is too small" (a trajetória desce a curva em U com **muitos passinhos minúsculos**); à direita "alpha is too large" (a trajetória dá **saltos** de um lado ao outro da curva, passando do fundo).

*(Figura não incluída neste projeto: Taxa de aprendizado pequena demais e grande demais, do slide 41. Veja-a nos slides da disciplina.)*

Eu confirmei isso no exemplo da seção 14: alfa = 0.001 mal se mexeu, alfa = 1.1 divergiu.

Analogia de software: é o **tamanho do passo** de um *hill climbing*; passo minúsculo = busca eterna; passo gigante = vai e volta sem achar o ponto.

> **Se perguntarem na prova:** taxa **pequena** = convergência lenta (custosa); taxa **grande** = pode **não convergir**, ultrapassando o mínimo. Valores usuais entre 0.001 e 0.3.

---

## 19. Por que precisamos de função de ativação (slides 42, 43, 44 e 45)

**Slide 42.** O objetivo é que a rede aprenda pesos e bias para **classificar corretamente**. Para a aprendizagem funcionar, o desejável é que uma **pequena mudança** em um peso (ou bias) cause **apenas uma pequena mudança correspondente na saída**. "Esta propriedade tornará possível a aprendizagem." Figura (vista): rede de 3 entradas, 4 ocultas, 1 saída, com o texto "Pequena mudança no peso (ou bias) causa uma pequena mudança no output" (w + Δw leva a output + Δoutput).

**Slide 43.** O problema: uma pequena alteração nos pesos de **um único perceptron** pode **mudar a saída por completo, digamos, de 0 para 1**, e isso pode fazer o **resto da rede mudar de modo muito complicado**. A solução é a **função de ativação**: ela permite que **pequenas mudanças** em pesos e bias causem **apenas uma pequena alteração** na saída.

Analogia de software: pense num `if` duro (`if soma >= 0 return 1`): mexer 0.0001 no parâmetro pode inverter o resultado inteiro (comportamento "tudo ou nada"). Um comportamento **suave** (que muda aos poucos) é o que permite ajustar com derivadas, porque dá para saber para que lado "melhorar". (A explicação do "para que lado melhorar" é nossa.)

**Slide 44.** "As funções de ativação basicamente **decidem se um neurônio deve ser ativado ou não**." A figura (vista) é o diagrama de um neurônio: entradas X₀ = +1, x₁, x₂, …, xₘ; pesos w_k0 (rotulado **W_k0 = b_k (bias)**), w_k1, …, w_km; um círculo com Σ que produz v_k; uma caixa "Activation function φ(.)" e a saída y_k. Ela mostra que o **bias é um peso cuja entrada é sempre +1**.

**Slide 45: a função de ativação é a transformação não linear.** É a **transformação não linear** aplicada ao sinal de entrada; essa saída transformada é enviada como entrada à próxima camada. **Sem função de ativação**, pesos e bias fazem **apenas uma transformação linear**; "uma rede neural sem função de ativação é essencialmente apenas um modelo de **regressão linear**".

**Por que empilhar camadas lineares não adianta.** Uma camada linear é `y = a·x + b`. Duas camadas seguidas são `y = a2·(a1·x + b1) + b2`, que **simplifica** para `(a2·a1)·x + (a2·b1 + b2)`: **outra** função linear. Isso vale para 50 camadas: **continua sendo uma reta**. Demonstrado na seção 10: a rede do XOR sem a ReLU colapsa em `−x1 − x2 + 2`.

```
Analogia: compor funções "multiplica por 2" e "soma 3" muitas vezes
          sempre resulta em "multiplica por K e soma M". Nenhum `if`, nenhuma curva.
          É um refatoramento: 50 camadas lineares podem ser substituídas por UMA.
```

> **Se perguntarem na prova:** "uma rede sem função de ativação (ou só com ativação linear) equivale a um **modelo de regressão linear**, não importa o número de camadas" (VERDADEIRO). "Função de ativação decide se o neurônio é ativado" (VERDADEIRO, slide 44). A ativação serve também para que **pequenas mudanças nos pesos causem pequenas mudanças na saída** (slide 43).

---

## 20. As principais funções de ativação (slides 46, 47, 48, 49 e 50)

**Catálogo visual (figura do slide 47, vista).** Cinco gráficos de F contra NET (a soma ponderada), cada um com duas versões (centrada em 0 e deslocada pelo bias b): **pseudo linear** (rampa entre 0 e 1), **degrau** (salto de 0 para 1), **sigmoide** `F = 1 / (1 + e^(−NET))` (curva em S entre 0 e 1), **tansigmoide** `F = (e^NET − e^(−NET)) / (e^NET + e^(−NET))` (curva em S entre −1 e 1) e **linear** (reta). Os textos dos slides 46 a 50 detalham degrau, linear, sigmoide, ReLU e softmax; pseudo linear e tansigmoide (tanh) só aparecem nesse desenho, sem texto.

*(Figura não incluída neste projeto: Gráficos de funções de ativação do slide 47: pseudo linear, degrau, sigmoide, tansigmoide e linear. Veja-a nos slides da disciplina.)*

### 20.1 Degrau (Binary Step Function, slide 46)

Se Y está **acima de um limite**, ativa o neurônio; senão, desativa: `f(x) = 1 se x ≥ 0` e `f(x) = 0 se x < 0`. O slide diz que é **só para fins didáticos, não é usada na prática**: o **gradiente da função degrau é zero**, o que a torna inútil no backpropagation, onde os gradientes das ativações são enviados para os cálculos de erro. Figura (vista): gráfico "Unit step (threshold)" com salto de 0 para 1 em x = 0.

**Atenção: divergência dentro dos próprios slides.** O slide 46 (e a figura do slide 21) escrevem o degrau com `x ≥ 0` dando 1. O slide 16 (exemplo numérico) escreve a saída como **1 se a soma > 0** e **0 se a soma ≤ 0**. Só muda o caso da soma exatamente igual a zero. Isso explica por que, no exemplo do slide 16, uma soma 0 dá saída 0.

> **Se perguntarem na prova:** se o enunciado trouxer uma tabela de perceptron com soma exatamente 0, **siga a regra dada no enunciado**; se ele não disser, assuma a convenção do slide do exemplo (soma > 0 → 1). A prova é sem cálculo, então isso é improvável; fique ciente.

### 20.2 Linear (slide 47)

`f(x) = a·x`. A derivada é **constante**, independente de x. O slide diz: isso significa que a cada backpropagation o gradiente seria o mesmo, e "este é um grande problema, não estamos realmente melhorando o erro". Usar a ativação linear é **não modificar a soma ponderada** (f(x) = x). **Onde se usa: na camada de saída de modelos de regressão.** Figura (vista): é o catálogo de gráficos descrito acima (o último painel, "Linear", mostra uma reta, uma centrada em zero e outra deslocada pelo bias b).

Leitura: ela **não adiciona não linearidade** (por isso nas camadas **ocultas** não ajuda, ver seção 19); no **fim**, para prever um número real qualquer (preço, temperatura), é exatamente o que se quer.

### 20.3 Sigmoide (slide 48)

Função **amplamente usada**, **suave** e **continuamente diferenciável**. A figura (vista) mostra a fórmula `φ(x) = 1 / (1 + e^(−x))` e o gráfico em S, saindo de 0 (para valores negativos grandes), passando por 0.5 em z = 0, e indo a 1. O slide diz que a função "tenta **empurrar os valores de Y para os extremos**", qualidade desejável para classificar numa classe. **Quando usar: camada de saída de classificação binária.**

Valores que calculei (executado): sigmoide(−6) = 0.0025, sigmoide(−2) = 0.1192, sigmoide(0) = 0.5, sigmoide(2) = 0.8808, sigmoide(6) = 0.9975. A saída fica **sempre entre 0 e 1**, e pode ser lida como uma **probabilidade** (leitura nossa).

Fora do slide (literatura, para entender): nas pontas, a curva é quase horizontal, então a **derivada fica quase zero** (0.0025 em ±6, contra 0.25 no centro). Isso causa o **desaparecimento do gradiente** (vanishing gradient) em redes profundas. O slide 48 não fala disso.

### 20.4 ReLU (slide 49)

**ReLU** = unidade linear retificada: `f(x) = max(0, x)`. É a função de ativação **mais usada** hoje no projeto de redes. O slide justifica: a ReLU é **não linear**, o que permite **propagar os erros para trás** com facilidade e ter **várias camadas** ativadas por ReLU. **Quando usar: padrão absoluto para as camadas ocultas** de quase todas as redes modernas; **se você não sabe qual usar, comece pela ReLU.**

Figuras do slide 49 (vistas): (1) ReLU `R(z) = max(0, z)`: zero à esquerda do 0 e reta crescente à direita; (2) ReLU junto com sua **derivada**: a derivada vale **0** para x < 0 e **1** para x > 0 (um degrau); (3) **Leaky ReLU** com sua derivada: à esquerda, uma reta de pouca inclinação (não zero) e à direita, a reta normal. O texto do slide **não cita Leaky ReLU**; a figura mostra a variação que "vaza" um pouquinho para valores negativos, evitando neurônio "morto" (explicação nossa).

*(Figura não incluída neste projeto: ReLU e sua derivada, do slide 49. Veja-a nos slides da disciplina.)*

Valores (executado): ReLU de [−6, −2, 0, 2, 6] = [0, 0, 0, 2, 6]; derivada = [0, 0, 0, 1, 1]. A derivada ser **1** para positivos significa que o gradiente passa sem enfraquecer (leitura nossa, coerente com a figura).

**Sobre "não linear".** A ReLU é feita de **dois pedaços de reta**, mas o conjunto (um "cotovelo" em 0) **não é uma reta**, então é não linear. Na seção 10, as camadas com ReLU resolveram o XOR; sem ela, não.

### 20.5 Softmax (slide 50)

"Também é um tipo de função sigmoide, mas é útil em **classificação multiclasse**. A sigmoide, como vimos, lida com **apenas duas classes**." A softmax **transforma as saídas de cada classe em valores entre 0 e 1** e também **divide pela soma das saídas**, o que dá a **probabilidade** de a entrada estar em cada classe.

Exemplo numérico nosso (executado): escores de saída [2.0, 1.0, 0.1] viram, com softmax, **[0.659, 0.242, 0.099]**; a soma é **1.0**. Ou seja: cada saída vira "fração do total" e o maior escore fica com maior probabilidade. Já com **sigmoides independentes** sobre escores [3.0, −1.0, 0.5], saem [0.953, 0.269, 0.623] com **soma 1.84**: cada saída é uma probabilidade **separada** (é isso que se usa em multirrótulo, seção 22).

Fórmula (fora do slide, aqui para você reconhecer): `softmax(xi) = e^xi / Σ e^xj`.

> **Se perguntarem na prova (divergência slide × literatura):** o slide 50 diz que a softmax é "um tipo de função sigmoide". Na literatura, ela é a **generalização** da sigmoide para várias classes (com 2 classes, as duas coincidem). Responda como o slide: softmax = multiclasse, saídas entre 0 e 1 que somam 1 (probabilidades); sigmoide = duas classes.

Tabela-resumo das cinco (slides 46 a 50):

| Função | Fórmula (slide) | Intervalo | Uso segundo os slides | Observação do slide |
| :-- | :-- | :-- | :-- | :-- |
| Degrau | 1 se x ≥ 0, senão 0 | 0 ou 1 | só didática | gradiente zero: inútil no backpropagation |
| Linear | a·x | todos os reais | **saída de regressão** | derivada constante |
| Sigmoide | 1 / (1 + e^(−x)) | (0, 1) | **saída de classificação binária** | suave, diferenciável |
| ReLU | max(0, x) | [0, +∞) | **camadas ocultas** (padrão) | não linear; comece por ela |
| Softmax | e^xi / Σ e^xj | (0, 1), soma 1 | **saída multiclasse** | probabilidades |

---

## 21. Escolhendo a função de ativação (slide 51)

**Slide 51.** **Não há regra de ouro**; depende do problema. As funções **sigmoide e suas combinações** geralmente funcionam melhor em **classificadores**. A **ReLU** é uma ativação **geral**, usada **na maioria dos casos** hoje. "Tenha sempre em mente que a ReLU deve ser usada **apenas nas camadas ocultas**." Como regra geral, **comece pela ReLU** e passe para outras se ela não der resultados ótimos.

Resumo para decisão (junta slides 47 a 51):

```
camadas ocultas       -> ReLU (comece por ela)
saída, regressão      -> linear (ou nenhuma)
saída, binária        -> sigmoide
saída, multiclasse    -> softmax
saída, multirrótulo   -> sigmoide em cada neurônio de saída (slide 52)
```

> **Se perguntarem na prova:** "ReLU na camada de saída de um classificador" é FALSO (o slide 51 manda usar ReLU só nas ocultas). "Não há uma regra de ouro; começar pela ReLU é a regra geral" é VERDADEIRO.

---

## 22. A tabela custo × ativação de saída (slide 52)

**Slide 52.** O slide traz esta tabela (a última linha do texto extraído, "Múltiplas classes possíveis", é uma anotação do slide ao lado da linha de Multilabel; eu a interpretei assim):

| Tipo de problema | Função de custo (loss) | Ativação recomendada na saída | Como ler (nossa explicação) |
| :-- | :-- | :-- | :-- |
| Classificação binária | Entropia cruzada binária | Sigmoide | 1 neurônio; probabilidade da classe positiva |
| Classificação multiclasse | Entropia cruzada categorizada | Softmax | 1 neurônio por classe; probabilidades somam 1; **uma** classe certa |
| Classificação multilabel | Entropia cruzada binária | Sigmoide (em cada neurônio de saída) | cada rótulo decidido de forma independente; **várias** classes possíveis ao mesmo tempo |
| Regressão | Erro quadrático médio | Linear (ou nenhuma) | número real qualquer |
| Regressão com outliers | Erro absoluto médio | Linear (ou nenhuma) | o erro absoluto pesa menos os valores extremos |

**Entropia cruzada (cross-entropy), sem cálculo.** Mede a distância entre as probabilidades que a rede deu e a resposta certa; pune forte quando a rede tem **muita confiança na resposta errada**. Se a classe certa é a primeira e a rede deu 0.659 a ela, o custo é `−log(0.659) = 0.417` (executado, exemplo nosso); se tivesse dado 0.99, o custo seria quase 0. O slide não explica a fórmula, só indica qual usar.

**MSE × MAE com outlier (exemplo nosso, executado).** Valores reais [100, 110, 105, 500] e previsões [102, 108, 107, 200]. O último ponto é um outlier muito mal previsto (erro de 300). **MSE = 22.503**, **MAE = 76,5**. O MSE explode por causa do quadrado do erro 300 (90.000 dividido por 4); o MAE cresce de forma linear. Por isso o slide recomenda o **erro absoluto médio** quando há outliers. (A explicação "o MAE é mais robusto" é a leitura padrão da literatura, e coerente com o slide.)

**Multiclasse × multilabel (a confusão preferida da prova).**

| | Multiclasse | Multilabel |
| :-- | :-- | :-- |
| Pergunta | "qual **uma** classe?" | "quais classes **estão presentes**?" |
| Exemplo nosso | foto: gato OU cão OU pássaro | artigo: tags "redes", "saúde", "otimização" (pode ter várias) |
| Saída | softmax (soma 1) | uma sigmoide por rótulo (soma livre) |
| Custo | entropia cruzada categorizada | entropia cruzada binária |

> **Se perguntarem na prova:** cada linha da tabela deve ser memorizada. "Para multilabel, use softmax" é FALSO (sigmoide em **cada** neurônio). "Classificação binária: entropia cruzada binária + sigmoide." "Regressão: MSE + linear; com outliers, erro absoluto médio."

---

## 23. Código: NumPy e scikit-learn (todos executados)

Esta seção não é dos slides (a prova pode trazer **trechos curtos de código scikit-learn**, ver spec 09). O que está nos slides são os conceitos; abaixo vão os trechos que eu rodei para conferir os números citados nas seções anteriores. Versões usadas: scikit-learn 1.5.1, NumPy 1.26.4.

### 23.1 Um passo de treino completo (forward + backward) em NumPy

```python
import numpy as np
sig = lambda z: 1/(1+np.exp(-z))
x = np.array([1.0, 0.0]); yd = 1.0
W1 = np.array([[0.5,0.2],[-0.3,0.8]]); b1 = np.array([0.1,0.1])
W2 = np.array([0.6,-0.4]); b2 = 0.05; eta = 0.5

def fwd(W1,b1,W2,b2):
    z1 = W1@x+b1; h = sig(z1); z2 = W2@h+b2; y = sig(z2)
    return z1,h,z2,y

z1,h,z2,y = fwd(W1,b1,W2,b2)           # FORWARD
C = 0.5*(y-yd)**2
d2 = (y-yd)*y*(1-y)                     # BACKWARD: camada de saída
gW2 = d2*h; gb2 = d2
d1 = d2*W2*h*(1-h)                      # BACKWARD: volta para a camada oculta
gW1 = np.outer(d1,x); gb1 = d1
W1n=W1-eta*gW1; b1n=b1-eta*gb1; W2n=W2-eta*gW2; b2n=b2-eta*gb2   # ATUALIZAÇÃO
```

Resultado: custo 0.0951 antes e 0.0857 depois do passo (os mesmos números da seção 10). A conta do gradiente confere com diferença finita.

### 23.2 Perceptron do scikit-learn contra AND, OR e XOR

```python
import numpy as np
from sklearn.linear_model import Perceptron
X = np.array([[0,0],[0,1],[1,0],[1,1]])
for nome, y in [("AND",[0,0,0,1]),("OR",[0,1,1,1]),("XOR",[0,1,1,0])]:
    p = Perceptron(max_iter=1000, eta0=0.1, random_state=0).fit(X, y)
    print(nome, "acurácia =", p.score(X, y))
```

Saída obtida: AND = 1.0, OR = 1.0, **XOR = 0.5**.

### 23.3 MLPClassifier resolvendo o XOR

```python
from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier(hidden_layer_sizes=(4,), activation="relu", solver="lbfgs",
                    max_iter=2000, random_state=1).fit(X, [0,1,1,0])
print(mlp.score(X, [0,1,1,0]), mlp.predict(X))     # 1.0 [0 1 1 0]
print([c.shape for c in mlp.coefs_], mlp.out_activation_)   # [(2, 4), (4, 1)] logistic
```

Pontos para ler em qualquer código do scikit-learn: `hidden_layer_sizes=(4,)` = **uma** camada oculta com 4 neurônios (`(16, 16)` = duas camadas de 16); `coefs_` = as matrizes de pesos (2 entradas × 4 ocultas, depois 4 × 1 saída); `out_activation_` = **logistic** (sigmoide) para classificação binária (coerente com o slide 52). Este exemplo usa `lbfgs` porque a base é minúscula; na prática o padrão é `adam` (slide 36).

### 23.4 MLP com os hiperparâmetros da aula

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
X, y = make_moons(n_samples=400, noise=0.25, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
mlp = make_pipeline(
    StandardScaler(),
    MLPClassifier(hidden_layer_sizes=(16, 16), activation="relu", solver="adam",
                  learning_rate_init=0.01, alpha=0.001, batch_size=32,
                  early_stopping=True, validation_fraction=0.1,
                  n_iter_no_change=10, max_iter=500, random_state=0))
mlp.fit(Xtr, ytr)
```

Saída na minha execução: acurácia de teste do MLP 0.93, o treino **parou na 22ª época** (parada antecipada), e o `Perceptron` simples, na mesma base, teve 0.9. (É uma base de teste pequena: não generalize a diferença; o ponto é que a base "duas luas" tem fronteira curva.)

Mapa de cada argumento para a aula:

| Argumento | Conceito dos slides |
| :-- | :-- |
| `hidden_layer_sizes` | número de camadas e neurônios (slide 35) |
| `activation="relu"` | ReLU nas ocultas (slides 49 e 51) |
| `solver="adam"` | otimizador Adam (slide 36); `"sgd"` é o SGD |
| `learning_rate_init` | taxa de aprendizado (slide 41) |
| `alpha` | penalidade L2 (slide 40) |
| `batch_size` | mini-batch (slide 34) |
| `early_stopping`, `validation_fraction`, `n_iter_no_change` | parada antecipada (slide 38) |
| `max_iter` | máximo de épocas (hiperparâmetro; não está no slide 35) |

A saída da rede para classificação já vem com a ativação certa (sigmoide para binária, softmax para multiclasse), escolhida pelo scikit-learn automaticamente.

### 23.5 Código com erros de lógica para treinar o olho (exemplo nosso)

Trecho 1 (cada linha tem um defeito de lógica, não de sintaxe):

```python
mlp = MLPClassifier(hidden_layer_sizes=(16,), activation="relu")
mlp.fit(X_teste, y_teste)                 # (a) treinando no conjunto de teste
print(mlp.score(X_treino, y_treino))      # (b) medindo no treino
```

Defeitos: (a) deveria treinar com `X_treino`; (b) a nota honesta vem do **teste**, não do treino (aula 4).

Trecho 2 (ordem das ações):

```python
mlp = MLPClassifier(...)
y_pred = mlp.predict(X_teste)    # (a) predizendo antes de treinar
mlp.fit(X_treino, y_treino)
```

Defeito: **prever antes de ajustar**. O scikit-learn lança erro (modelo não treinado); a ordem certa é `fit` e depois `predict`.

Trecho 3 (atualização do gradiente descendente em NumPy):

```python
w = w + alfa * derivada     # (a) deveria ser menos
```

Defeito: o passo é **contra** o gradiente (slide 32: `coeficiente − alfa·delta`). Com `+` o custo **sobe**.

Trecho 4 (escala dos atributos, fora do slide, mas importa em redes): usar `MLPClassifier` direto em atributos com escalas muito diferentes (idade 0 a 100 e salário 0 a 20000) piora o treino; por isso o pipeline do 23.4 tem `StandardScaler` antes (conceito da aula de pré-processamento).

---

## 24. Afirmações verdadeiras e falsas típicas de prova

| # | Afirmação | V ou F | Porquê (slide) |
| :-- | :-- | :-- | :-- |
| 1 | O neurônio MCP aprende sozinho ajustando os pesos | F | MCP não tem algoritmo de aprendizado (slide 9) |
| 2 | O Perceptron simples tem uma camada e aprende por correção de erro | V | slide 10 |
| 3 | O Perceptron sempre aprende se o problema for linearmente separável | V | slide 10 |
| 4 | Um Perceptron simples resolve qualquer problema se treinado por tempo suficiente | F | só lineares (slide 18) |
| 5 | O erro é e = Yd − Y | V | slide 12 |
| 6 | A taxa de aprendizagem deve ser grande para aprender rápido e sem ruído | F | deve ser pequena, para não aprender ruído (slide 12) |
| 7 | Se a rede acertou (e = 0), os pesos não mudam | V | n·e·Xi = 0 (slide 12) |
| 8 | Camadas intermediárias bastam para aprender problemas não lineares, mesmo com ativação linear | F | precisa de ativação não linear (slides 18 e 45) |
| 9 | Um neurônio tem várias saídas, uma para cada seta do desenho | F | tem uma saída; as setas só reaproveitam (slide 20) |
| 10 | Em MLP, o erro das camadas intermediárias é calculado direto por Yd − Y | F | não existe Yd para elas (slide 21) |
| 11 | O backpropagation foi descrito em 1986 e repassa o erro da saída para as camadas anteriores | V | slide 22 |
| 12 | Na fase Forward calculam-se os gradientes | F | isso é a Backward; a Forward calcula a saída (slides 23 e 24) |
| 13 | Na fase Backward usa-se a regra da cadeia | V | slide 24 |
| 14 | A convergência é o estado em que o erro não pode mais ser reduzido | V | slide 24 |
| 15 | O MSE é usado em problemas de regressão | V | slide 25 |
| 16 | O gradiente descendente se move na direção do gradiente (subindo) | F | negativo do gradiente (slide 26) |
| 17 | A derivada é a inclinação da reta tangente | V | slide 29 |
| 18 | O custo tem de chegar a exatamente zero para o treino terminar | F | zero ou próximo de zero (slide 33); na prática, convergência |
| 19 | No mini-batch, calcula-se o erro médio de várias amostras antes de atualizar os pesos | V | slide 34 |
| 20 | O SGD mantém uma taxa de aprendizado para cada peso | F | isso é o Adam; o SGD tem uma única taxa fixa (slide 36) |
| 21 | O Adam adapta separadamente a taxa de cada peso | V | slide 36 |
| 22 | Número de camadas, neurônios, otimizador, taxa e ativação são hiperparâmetros | V | slide 35 |
| 23 | A parada antecipada usa uma parte do treino como validação | V | slide 38 |
| 24 | L1 deixa todos os pesos pequenos sem zerar nenhum, e L2 zera pesos | F | invertido: L1 zera, L2 só diminui (slides 39 e 40) |
| 25 | O Dropout desliga neurônios aleatoriamente durante o treino | V | slide 40 |
| 26 | Taxa de aprendizado muito grande pode fazer a rede ultrapassar o mínimo | V | slide 41 |
| 27 | A função de ativação serve para que pequenas mudanças nos pesos causem pequenas mudanças na saída | V | slide 43 |
| 28 | Uma rede neural sem função de ativação equivale a uma regressão linear | V | slide 45 |
| 29 | A função degrau é a mais indicada para o backpropagation | F | seu gradiente é zero (slide 46) |
| 30 | A ativação linear é usada na saída de modelos de regressão | V | slide 47 |
| 31 | A sigmoide é usada na saída de classificação binária | V | slide 48 |
| 32 | A ReLU é o padrão para camadas ocultas e deve ser usada só nelas | V | slides 49 e 51 |
| 33 | A softmax é usada na saída multiclasse e transforma as saídas em probabilidades | V | slide 50 |
| 34 | Para multilabel, usa-se softmax e entropia cruzada categorizada | F | sigmoide em cada neurônio e entropia cruzada binária (slide 52) |
| 35 | Para regressão com outliers, recomenda-se o erro absoluto médio | V | slide 52 |

---

## 25. Resumo de véspera

1. **Neurônio biológico** → artificial: dendritos = entradas, corpo = soma, axônio = saída; **plasticidade** = ajuste das conexões = **ajuste dos pesos** (slides 3 a 6).
2. **MCP (1943)**: soma ponderada + ativação; **não aprende**, ajuste manual (slides 7 a 9). **Perceptron (1958)**: o MCP com **aprendizagem por correção de erro**, uma camada, aprende se **linearmente separável** (slide 10).
3. **Regra**: `e = Yd − Y`; `Wi_novo = Wi_atual + n·e·Xi`; taxa **pequena** (slides 11 e 12). Exemplo dos compositores e cientistas: erro 2, depois erro 0 (slides 13 a 17).
4. **Limite**: só fronteira linear. Saída: **camadas intermediárias + ativação não linear** (slide 18). MLP = camadas de perceptrons; cada neurônio tem **uma saída** (slides 19 e 20).
5. **Backpropagation** (1986): o erro da saída volta às ocultas; peso grande = grande responsabilidade (slides 21 e 22). **Forward** = previsão; **Backward** = gradientes pela **regra da cadeia**; fim = **convergência** (slides 23 e 24).
6. **Custo** C(w, b); MSE na regressão; minimizar com **gradiente descendente**: andar no **negativo do gradiente**; `coef = coef − alfa·derivada` (slides 25 a 33). **Mini-batch** (ex.: 128) é o mais comum (slide 34).
7. **Hiperparâmetros** (slide 35): camadas, neurônios, otimizador, taxa, ativação. **SGD** = uma taxa fixa; **Adam** = uma taxa por peso (slide 36).
8. **Regularização**: parada antecipada (validação), **L2** (pesos pequenos, nunca zera), **L1** (zera, seleciona atributos), **Dropout** (desliga neurônios) (slides 37 a 40). Taxa: pequena = lenta; grande = passa do mínimo (slide 41).
9. **Ativação**: faz pequenas mudanças nos pesos causarem pequenas mudanças na saída (slides 42 e 43); sem ela, rede = **regressão linear** (slide 45). **Degrau** (gradiente zero, só didático), **linear** (saída de regressão), **sigmoide** (saída binária), **ReLU** (ocultas), **softmax** (saída multiclasse) (slides 46 a 50). Comece pela ReLU, só nas ocultas (slide 51).
10. **Tabela do slide 52**: binária = entropia cruzada binária + sigmoide; multiclasse = categorizada + softmax; multilabel = binária + sigmoide em cada neurônio; regressão = MSE + linear; com outliers = erro absoluto + linear.
