# Aula 4 do zero: como saber se o modelo realmente aprendeu (amostragem e validação)

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software e um exemplo concreto, depois com o termo técnico que a professora usa nos slides. Palavras em **negrito** podem aparecer na prova. O texto segue a **ordem dos slides** (o número do slide aparece em cada seção).

Esta é a aula mais cobrada em formato "este gráfico está certo?", "esta tabela indica o quê?" e "a ordem do código está certa?". Leia devagar, e **responda as questões antes de ler as explicações**.

**A pergunta que a aula inteira responde:** *como eu sei, com honestidade, se meu modelo vai funcionar em dados que ele nunca viu?*

Analogia de software: é a diferença entre "passou nos testes que eu mesmo escrevi olhando o código" e "vai funcionar em produção com usuários reais". A aula 4 é o manual para não se enganar nessa diferença.

---

## 1. Os sete desafios do AM (slide 3)

O slide 3 lista os problemas que fazem um projeto de AM dar errado. Eles são a "lista de bugs típicos" de um sistema que aprende com dados:

| # | Desafio | Em uma frase | Analogia de software |
| :-- | :-- | :-- | :-- |
| 1 | Quantidade insuficiente de dados | Poucos exemplos para aprender | Testar o sistema com 3 casos de teste |
| 2 | Dados não representativos | Os exemplos não se parecem com o mundo real | Testar só em ambiente de desenvolvimento, com dados "bonitos" |
| 3 | Dados de baixa qualidade | Erros, ruído, outliers | Entrada suja (lixo entra, lixo sai) |
| 4 | Atributos irrelevantes | Colunas que não ajudam (ou atrapalham) | Parâmetros inúteis que só confundem a função |
| 5 | Sobreajuste (overfitting) | Decorou o treino | Código que passa nos testes porque tem `if` para cada caso de teste |
| 6 | Subajuste (underfitting) | Simples demais, não aprendeu | Função que devolve sempre a média |
| 7 | Testar e validar | Medir de forma honesta | Ter um conjunto de testes que realmente prova algo |

As próximas seções vão um por um, na ordem dos slides.

> **Se perguntarem na prova:** saiba listar os sete desafios e dizer em uma frase o que cada um significa.

---

## 2. Quantidade insuficiente de dados (slide 4)

**Ideia.** Aprender por exemplos é como aprender a reconhecer fraudes: se você viu 5 fraudes na vida, a "regra" que tira delas é frágil. A maioria dos algoritmos precisa de **muitos dados** para funcionar bem.

- Isso é **mais verdade** em problemas complexos, como **reconhecimento de imagens ou da fala** (slide 4).
- **Mas bases pequenas continuam comuns**. Por isso existem **estratégias de amostragem** (o assunto das seções 8 a 10): maneiras de aproveitar bem uma base pequena para treinar e para avaliar.

**Exemplo.** Uma clínica tem 120 pacientes com exames e quer prever uma doença rara. Com 120 linhas, a divisão em treino e teste deixa o teste com poucas dezenas de casos; qualquer resultado oscila muito. Em vez de aceitar um único número, usa-se uma estratégia de amostragem (validação cruzada, seção 10).

**Dois estragos diferentes de ter poucos dados** (não confundir):

1. **Treinar mal:** com 120 linhas é fácil o modelo decorar todas (overfitting, seção 5.2). Analogia: escrever uma regra de validação de formulário olhando só 5 entradas reais; ela acerta essas 5 e quebra na sexta.
2. **Avaliar mal:** se o teste tem 24 casos, cada erro vale ≈ 4 pontos percentuais (1/24). Errar 2 casos a mais ou a menos muda a acurácia de 88% para 79%. A nota é um "retrato tremido". Esse é o problema que as seções 8 a 10 atacam: reaproveitar os mesmos dados em várias divisões para ter uma nota mais estável.

O vídeo "9.5 Resampling and Repeated Holdout (L09 Model Eval 2)" mostra (em inglês) como a nota oscila quando o teste é pequeno. [Complemento: o slide 4 só afirma que mais dados ajudam, sobretudo em imagens e fala; os dois estragos acima são a leitura prática dessa frase.]

> **Se perguntarem na prova:** poucos dados dificultam o aprendizado, principalmente em problemas complexos; como bases pequenas são comuns, usam-se estratégias de amostragem.

---

## 3. Dados não representativos e viés de amostragem (slides 5 e 6)

**Ideia.** Para o modelo generalizar, ele precisa ser treinado com dados que **representam bem o problema** em que será usado. Pense em testar um sistema de entrega de pedidos só com endereços do centro da cidade e depois colocá-lo no interior: ele nunca viu estradas de terra.

O **viés de amostragem (sampling bias)** é quando a forma de coletar ou selecionar os dados faz a amostra **não representar com precisão** o problema real (slide 5). Detalhe importante: **base grande não garante representatividade**. Um milhão de linhas coletadas do jeito errado continua sendo uma amostra torta.

**Exemplo do slide 6.** Um estudo sobre desnutrição em áreas rurais: os entrevistadores **evitam moradias isoladas** e examinam só crianças que moram **perto das estradas principais**. As crianças das casas isoladas (provavelmente as mais afetadas, com menos acesso a serviços) ficam de fora. O modelo conclui que a desnutrição é menor do que de fato é.

**Exemplos novos (para você reconhecer o padrão):**

| Situação | Quem ficou de fora | Efeito |
| :-- | :-- | :-- |
| Pesquisa de satisfação enviada **por e-mail**, respondida só por quem quer responder | Quem não abre e-mail ou está insatisfeito demais para perder tempo | Notas infladas |
| Modelo de crédito treinado só com clientes **que tiveram o crédito aprovado** | Os negados (não sabemos se pagariam) | O modelo nunca aprende o perfil dos recusados |
| Detector de falhas treinado só com dados de **máquinas novas** | Máquinas velhas, que falham de outro jeito | Falha em produção com equipamento antigo |
| Reconhecimento de voz treinado só com vozes **adultas e sem sotaque** | Crianças, idosos, sotaques regionais | Erra muito para esses grupos |
| App de trânsito calibrado só com dados de **usuários de smartphone caro** | Quem usa aparelho simples | Conclusões válidas só para um recorte |

**Por que o tamanho não salva.** Pense em testar um app de compras com 1 milhão de pedidos, todos feitos por clientes de São Paulo. O volume é enorme, mas o modelo aprende hábitos paulistanos (CEP, frete, horário) e erra em Manaus. Mais linhas do mesmo recorte só deixam o modelo *mais confiante no recorte errado*. O que importa é se a amostra foi **sorteada de forma a refletir a população**; a analogia clássica (vídeo "Princípios de separação de dados em treino, validação, teste e reamostragens") é provar uma colher de sopa **depois de mexer a panela**: se você não mexer, a colher pega só o sal que ficou no fundo e a amostra engana.

**Como reconhecer na prova:** o enunciado descreve *como* os dados foram coletados e algo é deixado de fora de forma sistemática. A palavra-chave do slide é "**não representam com precisão o problema no qual o modelo operará**".

⚠ **Armadilha:** viés de amostragem **não** é o mesmo que o "viés" (bias) da seção 12. O primeiro é um problema de **coleta de dados**; o segundo é uma propriedade do **modelo** (erro sistemático). O português usa a mesma palavra, mas são ideias diferentes.

> **Se perguntarem na prova:** viés de amostragem = os dados de treino não representam o problema real; pode ocorrer mesmo em base grande; consequência: o modelo não generaliza.

---

## 4. Qualidade dos dados e atributos irrelevantes (slide 7)

**Qualidade dos dados.** Se a base está cheia de **erros, outliers (valores muito fora do padrão) ou ruído**, o modelo tem mais dificuldade de enxergar os padrões reais. É o velho "lixo entra, lixo sai". Por isso o **pré-processamento** é tão importante antes de entregar os dados ao algoritmo.

**Atributos irrelevantes.** O modelo só aprende se os dados tiverem **atributos relevantes suficientes e poucos irrelevantes**. Analogia: para prever o preço de um imóvel, área, bairro e número de quartos ajudam; a cor da porta, o nome do vendedor e a matrícula do corretor só adicionam barulho (e, com poucos dados, o modelo pode "achar" uma relação falsa com eles).

Por isso existe a fase de **seleção ou agregação de atributos** (slide 7):

- **Seleção**: escolher quais colunas ficam e descartar as inúteis.
- **Agregação**: combinar colunas em outras mais informativas (por exemplo, juntar "data de nascimento" e "data da compra" em "idade na compra").

**Atributo irrelevante, com um exemplo numérico.** Imagine prever se um cliente cancela a assinatura com 200 clientes e 40 colunas, das quais 3 são úteis (tempo de contrato, reclamações, uso mensal) e 37 são ruído (id, cor preferida do tema, dia da semana do cadastro...). Com tão poucos clientes, por puro acaso algumas das 37 colunas coincidirão com quem cancelou, e o modelo vai "descobrir" regras como "quem se cadastrou numa quarta cancela". Isso é overfitting causado por atributos irrelevantes: no treino parece padrão, no teste desaparece. Analogia: um linter que, por acaso, viu 3 bugs em arquivos com nome começando por "u" e passa a acusar todo arquivo "u*". Daí a seleção de atributos (descartar colunas) e a agregação (criar uma coluna melhor a partir de várias).

**Qualidade dos dados, com um exemplo.** Em uma coluna "idade" com a maioria entre 18 e 70 e um registro "250", a média sobe e qualquer modelo que use distância fica distorcido por esse registro. Os cuidados de limpeza (outliers, valores ausentes, padronização) são o assunto da Aula 3; veja nela os vídeos "Pré-processamento: valores extremos e valores ausentes" e "Detecção e remoção de outliers: univariado e multivariado". [Os slides da Aula 4 só citam o problema; a técnica está na Aula 3.]

| Problema | Exemplo | Remédio |
| :-- | :-- | :-- |
| Ruído / erro | idade = 250; peso = -3 | limpeza, correção, remoção |
| Outlier | salário de R$ 5 milhões entre salários de R$ 3 mil | tratar ou remover (com critério) |
| Atributo irrelevante | coluna "id_do_registro" | selecionar atributos |
| Atributos insuficientes | prever preço sem saber o bairro | obter/criar atributos melhores |

> **Se perguntarem na prova:** dados ruins dificultam o aprendizado, então se faz pré-processamento; o modelo precisa de atributos relevantes, então se faz seleção/agregação.

---

## 5. Overfitting × Underfitting (slides 8 a 12)

### 5.1 A ideia geral e a nomenclatura do slide (slides 8 e 9)

A **capacidade de generalização** (funcionar bem em dados novos) depende da **estrutura do modelo** e também da **quantidade de iterações de treinamento** (slide 8). Daí vêm os dois termos.

⚠ **Nomenclatura estranha do slide.** Os slides 8 e 9 chamam overfitting de "**super-amostrado**" e underfitting de "**sub-amostrado**", e dizem que o underfitting acontece por "**quantidade reduzida de iterações**". Na literatura, o ajuste (fit) não tem a ver com "amostragem": overfitting é **ajustar demais** o modelo ao treino; underfitting é **ajustar de menos**. **Na prova, use o vocabulário do slide se a questão usar; se a questão for conceitual, "ajuste demais × ajuste de menos" é a versão correta.** Pouco treinamento é **uma** das causas do subajuste (a lista de causas do slide 11 inclui "tempo de treinamento insuficiente"), mas não a única.

### 5.2 Sobreajuste (overfitting), slide 10

**Analogia.** É o aluno que **decora as respostas do simulado** em vez de aprender a matéria. Tira 10 no simulado e 4 na prova real, que tem questões diferentes. Em software: um código com um `if` para cada caso de teste. Passa em todos os testes e falha em tudo que é novo.

**Definição do slide 10:** o modelo **decora os exemplos de treinamento**; parece ter aprendido com os dados usados para construí-lo, mas, apresentado a **dados novos**, não consegue generalizar.

**Como reconhecer, em números:**

| Treino | Teste | Diagnóstico |
| :-- | :-- | :-- |
| 99% de acurácia | 71% | **Overfitting** (grande distância entre os dois) |

**Causas (slide 10):**

| Causa | Em português claro |
| :-- | :-- |
| Modelo excessivamente complexo | Tem mais "flexibilidade" do que o problema exige (árvore muito profunda, polinômio de grau 20) |
| Base de dados muito pequena | Poucos exemplos: é fácil decorar todos |
| Ruído nos dados de treinamento | O modelo aprende os erros como se fossem padrão |
| Treinamento excessivo (over-training) | Iterações demais: continua ajustando até decorar |
| Vazamento de dados (data leakage) | Informação do teste foi parar no treino (seção 11); ele "parece" ótimo, mas por trapaça |

**Soluções (da literatura; o slide só lista as causas):** simplificar o modelo, obter mais dados, limpar ruído, remover atributos irrelevantes, **regularização** (penalizar a complexidade), **parada antecipada (early stopping)**, e corrigir qualquer vazamento. [Complemento: o slide 10 não lista soluções.]

**Cada solução ligada à sua causa, com exemplo:**

| Causa (slide 10) | Solução | Exemplo concreto |
| :-- | :-- | :-- |
| Modelo complexo demais | Simplificar | Árvore de decisão com profundidade 25 → limitar a profundidade a 4; polinômio de grau 20 → grau 3 |
| Base pequena | Mais dados (ou validação cruzada para avaliar melhor) | Coletar mais 5 mil exemplos em vez de 300 |
| Ruído nos dados | Limpar / remover outliers e rótulos errados | Corrigir o cliente com idade 250 |
| Treinamento excessivo | Parada antecipada | Parar na época em que a perda de validação começa a subir (seção 13) |
| Vazamento | Corrigir o pipeline | Dividir antes de normalizar (seção 11) |
| (qualquer causa de complexidade) | Regularização | Cobrar uma "multa" por parâmetros grandes; analogia: limite de linhas por função que obriga o código a ser enxuto |

Repare que o remédio do overfitting (**reduzir** a capacidade ou **acrescentar** dados) é o oposto do remédio do underfitting (**aumentar** a capacidade).

### 5.3 Subajuste (underfitting), slide 11

**Analogia.** É o aluno que **não estudou o suficiente** ou usa um método fraco demais: erra tanto o simulado quanto a prova. Em software: um sistema de recomendação que sugere sempre o produto mais vendido. Simples demais para a realidade.

**Definição do slide 11:** é o oposto do sobreajuste. O modelo é **muito simples** para aprender a estrutura presente nos dados; a realidade é mais complexa que o modelo, e as previsões são imprecisas **mesmo nos exemplos de treinamento**.

**Como reconhecer, em números:**

| Treino | Teste | Diagnóstico |
| :-- | :-- | :-- |
| 62% | 60% | **Underfitting** (os dois baixos e próximos) |

**Causas (slide 11):** modelo muito simples (baixa complexidade); atributos insuficientes (*missing features*); pré-processamento inadequado; tempo de treinamento insuficiente.

**Soluções (slide 11):**

1. Selecionar um **modelo mais poderoso**, com mais parâmetros.
2. Alimentar o algoritmo com **melhores atributos**.
3. **Ajustar melhor os hiperparâmetros** (parâmetros definidos por nós).

**Cada causa do slide 11 com exemplo:**

| Causa | Exemplo | Como aparece |
| :-- | :-- | :-- |
| Modelo muito simples | Regressão linear (uma reta) para dados que formam uma curva | Reta cortando a nuvem de pontos sem acompanhá-la |
| Atributos insuficientes (*missing features*) | Prever o preço do imóvel só pela cor da fachada, sem área nem bairro | Erro alto mesmo no treino, qualquer que seja o modelo |
| Pré-processamento inadequado | Atributos com escalas muito diferentes (salário em milhares, idade em dezenas) sem padronizar, num modelo baseado em distância | O modelo "só enxerga" a coluna de maior escala |
| Tempo de treinamento insuficiente | Rede neural interrompida na época 2 de 100 | Perda ainda alta e em queda; basta treinar mais |

Os remédios do slide 11 casam um a um: modelo mais simples **→** modelo mais poderoso; atributos faltando **→** melhores atributos; pré-processamento ou treino mal ajustado **→** ajustar hiperparâmetros (por exemplo, número de épocas, taxa de aprendizado, profundidade). Analogia de software: o sistema de recomendação que sugere sempre o mais vendido melhora quando você (1) troca a regra por um modelo mais expressivo, (2) passa a usar o histórico do usuário (novos atributos) e (3) ajusta as configurações.

⚠ **A armadilha mais comum:** "para consertar underfitting, coloque **mais dados**". Em geral **não funciona**. Um modelo simples demais continua simples demais com 10 vezes mais dados (veja a curva de aprendizado na seção 5.5). O remédio é **mais capacidade** (modelo mais complexo, melhores atributos).

### 5.4 O quadro comparativo que resolve metade das questões

| | **Overfitting (sobreajuste)** | **Underfitting (subajuste)** |
| :-- | :-- | :-- |
| O que o modelo fez | Decorou o treino, inclusive o ruído | Não aprendeu nem o treino |
| Erro no **treino** | **Baixo** | **Alto** |
| Erro no **teste** | **Alto**, bem maior que o do treino | **Alto**, parecido com o do treino |
| Diferença treino × teste | **Grande** | Pequena |
| Viés / variância (seção 12) | baixo viés, **alta variância** | **alto viés**, baixa variância |
| Complexidade | Complexo demais | Simples demais |
| Remédio | Simplificar, regularizar, mais dados, parar antes | Mais poderoso, melhores atributos, hiperparâmetros |

**Truque de leitura em duas perguntas:**

1. **O erro de treino é baixo?** Se for alto, é underfitting (o modelo nem aprendeu o que viu).
2. Se for baixo, **o de teste é muito pior?** Se for, é overfitting. Se os dois são baixos e próximos, é um bom ajuste.

### 5.5 Como reconhecer em gráficos

O slide 12 traz figuras de ajuste de curvas; o slide 29 traz o gráfico de complexidade × erro. Há três gráficos que você precisa saber ler.

**(a) Curvas ajustadas aos mesmos pontos** (modelos X, Y e Z de uma regressão polinomial):

| Aparência da curva | Diagnóstico |
| :-- | :-- |
| Uma **reta** que não acompanha a curvatura dos pontos | Underfitting (simples demais) |
| Curva **suave** que segue a tendência sem tentar passar por todo ponto | Bom ajuste |
| Curva que **passa por todos os pontos**, cheia de ondas e picos | Overfitting (decorou o ruído) |

Pegadinha: "a curva que passa por todos os pontos tem o menor erro **no treino**, então é a melhor." **Falso.** Erro baixo no treino não prova nada; olhe o desempenho em dados novos.

**(b) Gráfico de erro × complexidade do modelo (slide 29).** Duas curvas, treino e teste:

- O **erro de treino** só **cai** conforme a complexidade aumenta.
- O **erro de teste** cai no começo (o modelo está aprendendo o padrão) e **depois sobe** (está decorando ruído). Forma de **"U"**.
- O **melhor modelo** é o **fundo do U**.
- À **esquerda** do fundo: underfitting. À **direita**: overfitting.
- O erro de teste normalmente fica **acima** do de treino. Se aparece **abaixo**, de forma consistente e crescente, o gráfico é **incoerente** com a teoria.

**(c) Curva de aprendizado** (acurácia × número de exemplos de treino), complemento útil:

- **Treino alto, validação bem abaixo, a distância diminuindo com mais dados**: overfitting. Mais dados **ajudam**.
- **Treino e validação baixos e já juntos**: underfitting. Mais dados **não ajudam**; precisa de modelo mais capaz ou atributos melhores.

**(d) Perda × épocas de uma rede neural (slides 33 e 34).** A perda de treino cai sempre. A perda de validação cai e, a partir de certo ponto, **sobe**: ali começa o overfitting, e ali se deve **parar o treino** (parada antecipada, seção 13).

> **Se perguntarem na prova:** overfitting = treino bom, teste ruim; underfitting = os dois ruins. No gráfico de complexidade, o melhor modelo está no fundo do "U" da curva de teste. Para underfitting a solução é modelo mais poderoso/melhores atributos/hiperparâmetros; para overfitting, simplificar/regularizar/mais dados.

---

## 6. Generalização: o objetivo final

**Generalização** é a capacidade de o modelo funcionar bem em dados **que ele nunca viu**. É o objetivo de todo o processo. Um modelo não é bom por acertar o treino; é bom se acerta casos novos do mesmo problema (slide 5: "consiga classificar, prever, agrupar ou associar adequadamente novos dados do mesmo problema").

Analogia: um sistema de tradução que só traduz as frases do manual de treinamento não é um tradutor, é um dicionário de frases. A diferença entre os dois é a generalização.

Tudo o que vem a seguir (hold-out, validação cruzada, vazamento) existe para **medir a generalização sem trapacear**.

---

## 7. Por que testar nos mesmos dados do treino é erro metodológico (slides 13 e 14)

**Ideia.** Imagine corrigir a prova de um aluno com **as mesmas questões** que ele estudou. Ele pode tirar 10 apenas porque decorou o gabarito. A nota não mede aprendizado.

O slide 13 diz literalmente: treinar um modelo de AM e testá-lo nos mesmos dados é **um erro metodológico**. Esse modelo apenas "decoraria" os rótulos dos exemplos que acabou de ver: desempenho **perfeito no treino**, mas **nada útil** sobre exemplos novos.

**Exemplo concreto (um modelo de vizinhos mais próximos com k = 1).** Se você pergunta a ele a classe de uma amostra que **já está no treino**, o vizinho mais próximo é ela mesma, e ele acerta 100%. Isso não diz nada sobre dados novos.

**A solução (slides 13 e 14):** **reter parte dos dados como conjunto de teste**, que o modelo **nunca vê durante o treinamento**. A única maneira de saber quão bem o modelo generalizará em novos casos é testá-lo em novos casos, e isso se faz **antes** de colocar em produção, para evitar falhas e queixas dos usuários. É preciso dividir a base em **pelo menos dois conjuntos**: um para treinar, outro para testar.

> **Se perguntarem na prova:** avaliar o modelo nos dados de treino é erro metodológico, porque ele pode apenas ter decorado; a avaliação deve ser em dados não vistos (conjunto de teste).

---

## 8. Hold-out: treino e teste (slides 15 a 17)

### 8.1 Como funciona (slide 16)

A primeira opção de divisão é separar **uma vez** a base em dois conjuntos: **treino** e **teste**. Essa técnica se chama **hold-out** ("reter").

Proporções comuns: **⅔ treino e ⅓ teste**, ou **80% treino e 20% teste**.

Exemplo: base com 1.000 amostras, 80/20 → 800 para treinar e 200 para testar. ⅔–⅓ → cerca de 667 e 333.

⚠ **Slide × vídeos.** O slide 16 cita só ⅔–⅓ e 80–20. Os vídeos "AM 03.6 Experimentação, Holdout, Cross Validation, Validação Cruzada, Estratificado" e "9.5 Resampling and Repeated Holdout" usam 60/40, 50/50, 70/30 e 90/10 e dizem que a escolha é uma convenção, não uma regra. Não há contradição: **o "certo" não é uma proporção fixa**, e sim um compromisso.

- Teste **grande** demais → sobra pouco para treinar, e o modelo fica pior do que poderia (nota pessimista).
- Teste **pequeno** demais → a nota oscila muito de uma divisão para outra (seção 8.3).
- Com **milhões** de linhas, 90/10 ou até 98/2 já dão um teste enorme; com **centenas**, 80/20 deixa um teste instável, e é aí que entra a validação cruzada.

**Na prova:** se a questão pedir "proporções comuns", responda **⅔–⅓ ou 80–20** (slide). Se disser que 70/30 ou 90/10 "está errado", desconfie: são proporções usadas na prática. Se afirmar que existe uma proporção universalmente correta, é falso.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model.fit(X_train, y_train)          # treina só com o treino
acc = model.score(X_test, y_test)    # mede só no teste
```

Em palavras: o modelo ajusta seus parâmetros usando **só** o treino; depois verificamos a capacidade de generalização no **teste**.

### 8.2 A regra de diagnóstico (slide 16)

> **Erro de treino baixo + erro de teste alto = o modelo está se sobreajustando (overfitting).**

É a frase mais cobrada da aula. Ela é a versão em palavras da tabela da seção 5.4.

### 8.3 A crítica à divisão única (slide 17)

O problema: com **uma só divisão**, não dá para saber **o quanto o desempenho varia** se o conjunto de teste for outro. Principalmente com conjuntos de teste pequenos. A frase do slide: "pode ser que a amostra de teste possuísse amostras consideradas mais fáceis".

Analogia: avaliar um aluno com **uma única prova de 10 questões**. Se caíram as 10 que ele sabia, ele parece ótimo; se caíram as 10 que ele não sabia, parece péssimo. Uma prova só é um retrato pouco confiável.

Por isso o slide propõe, para tornar o resultado **menos dependente da partição**, **amostragem aleatória** ou **validação cruzada** (próximas seções).

[Complemento, não é do slide, mas é conhecimento consolidado] Quando as classes são desbalanceadas, usa-se **divisão estratificada** (`stratify=y`), que mantém a proporção das classes em treino e teste.

> **Se perguntarem na prova:** hold-out = uma divisão treino/teste (⅔–⅓ ou 80–20). Treino baixo e teste alto = overfitting. Crítica: um único teste pode ser "fácil" ou "difícil" e não mede a variação.

---

## 9. Amostragem aleatória repetida (slides 18 e 19)

**Ideia.** Em vez de fazer **uma** divisão, faça **várias divisões aleatórias** (por exemplo, 10), treine e teste em cada uma e **tire a média**. É como aplicar 10 provas diferentes ao aluno e olhar o conjunto das notas.

```python
accs = []
for seed in range(10):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
    model.fit(X_tr, y_tr)
    accs.append(model.score(X_te, y_te))
# reportar: média e desvio padrão de accs
```

O desempenho é reportado pela **média** **e** pelo **desvio padrão** (slide 18). Exemplo de resultado: "acurácia 0,86 ± 0,02".

**Como ler o desvio padrão (slide 18):**

| Resultado | O que indica |
| :-- | :-- |
| Média 0,86, desvio **0,01** | Modelo **estável**: o desempenho quase não muda conforme a amostra |
| Média 0,86, desvio **0,12** | Desvio **alto** = alta variabilidade = **instabilidade** do modelo diante de mudanças nas amostras |

Atenção: um desvio padrão alto **não** quer dizer que o modelo é ruim em média; quer dizer que o resultado **depende muito de qual amostra caiu**, e portanto que não podemos confiar em um número só.

**O que é o desvio padrão, do zero.** É "o quanto, em média, cada resultado se afasta da média". Pense em tempos de resposta de uma API: média de 100 ms. Se as chamadas ficam entre 98 e 102 ms, o desvio é pequeno e você confia no serviço; se ficam entre 20 e 400 ms, o desvio é grande, mesmo com a mesma média, e o serviço é imprevisível. Aqui a "chamada" é cada divisão treino/teste e o "tempo" é a acurácia.

Exemplo com as acurácias de 5 divisões:

| Modelo | Acurácias | Média | Desvio (aprox.) | Leitura |
| :-- | :-- | :-- | :-- | :-- |
| A | 0,85; 0,86; 0,86; 0,87; 0,86 | 0,86 | 0,007 | Estável |
| B | 0,98; 0,70; 0,92; 0,75; 0,95 | 0,86 | 0,12 | Instável: a nota depende de qual teste caiu |

As médias são iguais; o que diferencia os modelos é o desvio. [Não é para calcular na prova; é para interpretar.] No código da seção 10.3, `scores.std()` faz esse papel. O vídeo "9.5 Resampling and Repeated Holdout (L09 Model Eval 2)" mostra a mesma ideia com mínimo e máximo (acurácias entre 80% e 100% em 50 repetições com teste pequeno), sem usar o termo "desvio padrão"; nenhum vídeo da lista o define, por isso o texto acima é a referência.

**A crítica (slide 19):** como as divisões são sorteadas, **não há garantia de que os conjuntos de teste sejam diferentes** entre si: podem se repetir ou se sobrepor bastante. Uma amostra pode aparecer em vários testes e outra nunca. A alternativa proposta é a **validação cruzada**.

Exemplo concreto: base de 10 amostras (numeradas 1 a 10), 3 sorteios com teste de 3 amostras. Podem sair {2, 5, 7}, {5, 7, 9} e {2, 7, 9}: a amostra 7 foi testada três vezes, e as amostras 1, 3, 4, 6, 8 e 10 **nunca foram testadas**. A média parece vir de 3 avaliações independentes, mas na prática avaliou quase as mesmas amostras e deixou outras de fora. Analogia: três code reviews em que o revisor, por sorteio, sempre cai nos mesmos arquivos. Na validação cruzada (seção 10) isso é impossível por construção: cada amostra é testada exatamente uma vez.

> **Se perguntarem na prova:** amostragem aleatória = várias partições aleatórias, resultado em média e desvio padrão; desvio alto = instabilidade; crítica: os conjuntos de teste podem se sobrepor ou ser muito parecidos.

---

## 10. Validação cruzada k-fold (slides 20 e 21)

### 10.1 A ideia

A validação cruzada (**cross-validation**) resolve a crítica da seção 9: ela **garante** que os conjuntos de teste são **diferentes e juntos cobrem a base inteira**. Cada amostra é testada **exatamente uma vez**.

Analogia: dividir a turma em 5 grupos; cada grupo faz a prova uma vez, enquanto os outros 4 grupos servem de "material de treino". No final todo mundo foi avaliado uma vez.

### 10.2 Passo a passo (slide 20)

1. Divida a base em **K pedaços (folds) de igual tamanho**.
2. Faça **K rodadas**. Em cada rodada, **um fold fica de fora do treinamento e é usado como teste**; os outros K−1 folds formam o treino.
3. Cada fold será o teste **uma vez**.
4. Junte os K resultados: a métrica é a **média** e o **desvio padrão** das K execuções.

### 10.3 Exemplo com 100 amostras e K = 5

Cada fold tem 20 amostras.

| Rodada | Folds de treino | Fold de teste | Acurácia no teste (exemplo) |
| :-- | :-- | :-- | :-- |
| 1 | 2, 3, 4, 5 | **1** | 0,84 |
| 2 | 1, 3, 4, 5 | **2** | 0,88 |
| 3 | 1, 2, 4, 5 | **3** | 0,80 |
| 4 | 1, 2, 3, 5 | **4** | 0,86 |
| 5 | 1, 2, 3, 4 | **5** | 0,87 |

Resultado final: **média ≈ 0,85** e **desvio padrão em torno de 0,03** (as cinco notas ficam, em geral, a ±0,03 da média; ver a explicação do desvio padrão na seção 9). Por que reportar os dois? A média diz **quanto** o modelo acerta; o desvio diz **quanta confiança** ter nesse número. Um k-fold com 0,85 ± 0,01 e outro com 0,85 ± 0,10 têm a mesma média e merecem credibilidade muito diferente. Atenção: o desvio é entre as K rodadas, **não** é um desvio dentro de cada fold. Em cada rodada o modelo treinou com 80 amostras e testou em 20 que **não** estavam no treino daquela rodada. Ao final, **as 100 amostras** serviram de teste, uma vez cada. Foram treinados **5 modelos**.

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5)      # 5 folds
print(scores.mean(), scores.std())               # média e desvio
```

### 10.4 Quando NÃO usar (slide 21)

A validação cruzada treina o modelo **K vezes**, então custa cerca de **K vezes mais** tempo de computação. O slide diz: só usamos esse método de amostragem para **conjuntos de dados pequenos**; para um conjunto **grande e representativo**, o **hold-out simples é suficiente**.

Exemplo: base de 5 milhões de linhas e modelo que leva horas para treinar: 10 folds seria 10 vezes o custo, sem ganho relevante, porque um teste de 1 milhão de linhas já é muito estável.

### 10.5 Comparação das três estratégias

| | Hold-out | Amostragem aleatória | Validação cruzada |
| :-- | :-- | :-- | :-- |
| Divisões | **1** | **Várias**, sorteadas | **K**, sem sobreposição de teste |
| Resultado | 1 número | Média ± desvio | Média ± desvio |
| Custo | Menor | Médio | Maior (≈ K treinos) |
| Ponto fraco | Teste pode ser "fácil" ou "difícil" | Testes podem se repetir | Custo; não serve a base muito grande |
| Quando usar | Base **grande** | Quando quer variar a partição | Base **pequena** |

⚠ **Pegadinha típica:** "na validação cruzada, o modelo final é treinado K vezes e **testado nos mesmos dados** em que treinou." **Falso.** Em cada rodada o teste é um fold **fora** do treino daquela rodada.

> **Se perguntarem na prova:** k-fold divide em K partes iguais, roda K vezes, cada fold é o teste uma vez, resultado em média e desvio; caro, por isso para bases pequenas; para base grande basta hold-out.

---

## 11. Vazamento de dados (data leakage), slides 22 a 24

### 11.1 O que é (slide 22)

É um dos erros **mais sutis e perigosos** do AM. Ocorre quando **informação do conjunto de teste** (ou informação **que não estaria disponível na hora da previsão real**) **vaza para dentro do modelo durante o treinamento**.

Resultado: o modelo parece um "gênio" nos testes e **fracassa miseravelmente em produção**.

Analogia de software: é testar um sistema de pagamentos usando em produção uma variável de ambiente que só existe no seu notebook. Nos seus testes tudo passa; no servidor real, quebra. Ou, mais próximo: o aluno **viu a prova antes** de fazê-la.

O que torna o vazamento perigoso: **nada dá erro**. O código roda, a acurácia sobe, e você comemora. A mentira só aparece em produção.

### 11.2 Os quatro tipos do slide

| Tipo | O que é | Exemplo | Correção |
| :-- | :-- | :-- | :-- |
| **Temporal** (slide 23) | Usar o **futuro** para prever o **passado** | Prever o preço de ações de ontem treinando com preços de hoje | **Divisão temporal** (Time Series Split): treino = passado, teste = futuro |
| **Duplicação de dados** (slide 23) | O mesmo dado aparece mais de uma vez; uma cópia cai no treino e outra no teste | Paciente fez dois exames idênticos no mesmo dia: um no treino, outro no teste | Remover duplicatas **antes** de dividir (e dividir por paciente) |
| **De atributos** (slide 23) | Um preditor só existe **depois** do evento que se quer prever | Prever pneumonia usando a coluna `Medicamento_Antibiótico_X` (só é prescrito a quem já foi diagnosticado) | Remover atributos "do futuro" |
| **No pré-processamento** (slide 24) | Usar **estatísticas da base inteira** para transformar os dados **antes** de dividir | Normalizar com média e desvio de **toda** a base; preencher nulos com a média **global** | Dividir **primeiro**; calcular as estatísticas **só no treino** |

### 11.3 Vazamento temporal, em detalhe (slide 23)

Para dados que dependem do tempo (ações, clima, vendas), **nunca** use o "futuro" para prever o "passado". Em produção você só terá o passado.

Errado × certo:

```python
# ERRADO: embaralha a série; o treino contém dias DEPOIS dos dias de teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)

# CERTO: respeita a ordem do tempo (treino = início da série, teste = o fim)
corte = int(len(X) * 0.8)
X_train, X_test = X[:corte], X[corte:]
y_train, y_test = y[:corte], y[corte:]
# ou: TimeSeriesSplit, para validação cruzada em séries temporais
```

Embaralhar uma série temporal ao dividir é o erro clássico: o modelo "vê" o dia 11 no treino e é "testado" no dia 10. Ele pode simplesmente interpolar entre os vizinhos.

### 11.4 Vazamento por duplicação, em detalhe (slide 23)

O mesmo registro aparece duas vezes (erro de coleta, vários cadastros do mesmo cliente). Se uma cópia vai para o treino e a outra para o teste, o modelo **já viu** a resposta do teste. O teste deixou de ser "dados novos".

### 11.5 Vazamento de atributos, em detalhe (slide 23)

Pergunta de verificação para cada coluna: "**no momento em que eu precisar fazer a previsão real, eu já terei esse valor?**" Se a resposta for "não" (como o antibiótico prescrito *depois* do diagnóstico de pneumonia), a coluna vaza o alvo.

Outro exemplo: prever se um cliente vai cancelar o contrato usando a coluna `motivo_do_cancelamento` (só é preenchida **quando o cancelamento acontece**). O modelo "acerta" tudo e é inútil.

### 11.6 Vazamento no pré-processamento, em detalhe (slide 24)

Normalizar é transformar os valores usando a **média** e o **desvio padrão** de uma coluna. Se você calcula essas estatísticas na **base inteira** e só depois divide, o treino "sabe" a média do teste. O mesmo vale para **preencher valores ausentes (imputation)** com a média global.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# ERRADO: o scaler enxerga a base inteira (inclui o que será teste)
X_scaled = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# CERTO: divide primeiro; fit só no treino; transform no teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler()
scaler.fit(X_train)                       # aprende média e desvio SÓ do treino
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)         # aplica o que aprendeu no treino
```

**Regra de ouro:** `fit` **só** no treino; no teste, apenas `transform`/`predict`. Em scikit-learn, o `Pipeline` garante isso automaticamente (inclusive dentro de validação cruzada).

### 11.7 A ordem correta do pipeline (o que a prova adora perguntar)

```
1. Remover duplicatas e atributos "do futuro"
2. DIVIDIR em treino e teste (em série temporal, por ordem de tempo)
3. Ajustar (fit) imputação, normalização, seleção de atributos SÓ no treino
4. Aplicar (transform) essas transformações no treino e no teste
5. Treinar o modelo (fit) SÓ no treino
6. Avaliar (predict/score) no teste, uma única vez, no final
```

Qualquer ordem que faça o teste "participar" de um `fit` (de scaler, imputer, seletor ou modelo) tem vazamento.

### 11.8 Complemento: vazamento ao escolher hiperparâmetros [complemento, não é do slide]

Se você testa vários valores de um hiperparâmetro **olhando a nota no conjunto de teste** e fica com o melhor, o teste virou parte do ajuste. É um tipo de vazamento: a nota final fica otimista, porque você escolheu o modelo que "casou" melhor com aquele teste. O correto é escolher hiperparâmetros com **validação** (conjunto de validação ou validação cruzada **dentro do treino**) e deixar o teste para o **final**, uma vez.

> **Se perguntarem na prova:** vazamento = informação do teste/futuro entra no treino; modelo "gênio" nos testes, fracasso em produção. Quatro tipos: temporal, duplicação, de atributos, no pré-processamento. Em normalização/imputação, **dividir primeiro** e calcular estatísticas **só no treino**.

---

## 12. Viés × variância (slides 25 a 32)

Esta seção explica o mesmo fenômeno da seção 5 por outro ângulo.

### 12.1 A analogia do alvo (slides 25 e 26)

Imagine um **alvo de tiro**. O **centro** é o valor verdadeiro que o modelo deveria prever. Cada tiro é uma previsão do **mesmo modelo treinado com dados diferentes** (slide 26). Dois comportamentos de erro:

- **Viés (bias):** os tiros erram **sempre para o mesmo lado**; o centro do grupo de tiros está **longe do alvo**. É erro **sistemático**. É o atirador cuja mira está torta.
- **Variância:** os tiros ficam **espalhados**; mudando os dados de treino, a previsão muda muito. É erro de **instabilidade**. É o atirador de mão trêmula.

### 12.2 Os quatro casos (slide 31)

| | **Baixa variância** (tiros juntos) | **Alta variância** (tiros espalhados) |
| :-- | :-- | :-- |
| **Baixo viés** (centro do grupo no alvo) | **Ideal**: bom acerto e estabilidade | Tiros em volta do centro, espalhados: **overfitting**, não generaliza bem com dados novos |
| **Alto viés** (grupo longe do alvo) | Tiros juntos mas **longe**: **underfitting**, não captura a relação verdadeira | **Pior caso**: inconsistente e com acurácia muito baixa |

Linha mais importante para memorizar:

- **Alto viés = underfitting** (slide 28: "se o seu problema é underfitting, o modelo tem alto bias").
- **Alta variância = overfitting** (slide 28: "se o seu problema é overfitting, o modelo tem alta variância").

### 12.3 O que é do slide e o que é complemento

| Ponto | Origem |
| :-- | :-- |
| Viés = diferença entre a **média das predições** e o valor real (slide 27) | Slide |
| Variância = amplitude/variabilidade das predições (slide 27) | Slide |
| "O bias indica o erro gerado pelo modelo sobre os dados de treino" (slide 27) | Slide, mas é uma **aproximação didática**: viés alto costuma aparecer como erro alto no treino |
| Variância = o quanto a previsão muda quando o **mesmo** modelo é treinado com **outros dados** | Conhecimento consolidado; é o que o slide 26 mostra com a figura |
| Erro total = viés² + variância + ruído irredutível | Complemento (literatura); não aparece nos slides e **não é para cálculo** |

⚠ **Duas versões (slide × literatura).** O slide 27 define o viés pelo **erro nos dados de treino**; a literatura define pela **diferença entre a predição média e o valor real**, que **não** é literalmente o erro de treino. **Na prova**, aceite a frase do slide em contexto de questão que a use, mas, se pedirem a definição conceitual, responda: "viés = erro sistemático; diferença entre a média das predições e o valor real".

⚠ **Duas formas de definir viés e variância (slide 27 × vídeos).** Os vídeos "Machine Learning Fundamentals: Bias and Variance" e "O trade-off de viés e variância (bias-variance tradeoff) - Perguntas de Entrevista" usam outras palavras, mas as ideias são compatíveis:

| | Slide 27 | Vídeos | Exemplo |
| :-- | :-- | :-- | :-- |
| Viés | erro gerado pelo modelo sobre os dados de treino | incapacidade do método de captar a relação verdadeira (uma reta nunca vira curva) | Reta sobre dados curvos: erra no treino e no teste, sempre do mesmo jeito |
| Variância | amplitude/variabilidade das predições | o quanto o ajuste muda de um conjunto de treino para outro | Curva ondulada: erro zero no treino, previsões muito diferentes se trocar 5 pontos |

**Qual responder.** Em questão que reproduz o slide ("o bias indica o erro do modelo sobre os dados de treino"), a frase é aceita. Em questão conceitual, use a dos vídeos: **viés = erro sistemático por simplificação do modelo; variância = sensibilidade do modelo aos dados de treino usados**. E as associações, iguais nas duas versões: **viés alto → underfitting; variância alta → overfitting**. Os vídeos acrescentam uma tendência (não regra): modelos simples (regressão linear/logística) tendem a viés alto e variância baixa; modelos flexíveis (árvores profundas, KNN com k pequeno) tendem a viés baixo e variância alta.

⚠ O slide 31 diz que overfitting é o modelo "**superestimando**" e underfitting "**subestimando**" os dados de treino. É linguagem imprecisa: não significa prever valores acima ou abaixo do real. Leia como "ajustou demais" e "ajustou de menos".

### 12.4 O compromisso entre viés e variância (slides 27, 29 e 30)

**Objetivo:** baixo viés **e** baixa variância. Mas é difícil, porque os dois puxam em direções opostas:

- Aumentar a **complexidade** do modelo faz ele se ajustar melhor aos dados de treino (o **viés cai**), mas ele também passa a seguir o ruído (a **variância sobe**).
- Reduzir a complexidade deixa o modelo estável (**variância cai**), mas simples demais (o **viés sobe**).

Slide 29: em geral, com mais complexidade o **erro de treino cai**, mas o **de teste pode aumentar**. Se o modelo for muito simples, **nem os dados de treino** ele consegue ajustar.

Slide 30: os dados têm **erros embutidos** (ruído); superajustando, o modelo **aprende o ruído**. O objetivo é achar o **ponto ótimo**, onde a complexidade é ideal e o erro é baixo **em treino e em teste**. O slide chama isso de "Bias Trade-off"; na literatura o nome é ***bias-variance trade-off*** (compromisso viés-variância).

```
 erro
  |  \                          /  <- erro de TESTE (forma de U)
  |   \                       /
  |    \_____            ___/
  |          \__________/   ← melhor modelo (fundo do U)
  |   \________________________  <- erro de TREINO (só cai)
  +-------------------------------- complexidade do modelo
    underfitting   |   overfitting
    (alto viés)    |   (alta variância)
```

> **Se perguntarem na prova:** viés alto = underfitting; variância alta = overfitting; o ideal é baixo viés e baixa variância; mais complexidade reduz o viés e aumenta a variância; o ponto ótimo é o fundo do "U" do erro de teste.

---

## 13. Conjunto de validação e parada antecipada (slides 33 e 34)

**O problema.** Com hold-out simples, quando você vai ajustar o modelo (hiperparâmetros, quantas iterações treinar), precisa de uma nota para decidir. Se usar o teste para isso, o teste vira parte do ajuste (seção 11.8). Então cria-se um **terceiro** conjunto.

**Conjunto de validação (slide 33 e 34):** é um **subconjunto do conjunto de treinamento**, usado **durante o treinamento** para acompanhar a generalização e evitar o superajuste. É passado para alguns algoritmos, como redes neurais.

Como funciona (slide 34): **depois de cada iteração** do treinamento, o algoritmo testa o modelo no conjunto de validação. Isso permite a **parada antecipada (early stopping)**: quando o erro de validação **começa a subir**, o treino é interrompido, porque o modelo começou a decorar. Terminado o treino, faz-se um **teste final no conjunto de teste**.

Analogia: o conjunto de validação é o **simulado** que o aluno faz durante o curso para ajustar a forma de estudar; o conjunto de teste é a **prova final**, que só se faz uma vez.

| Conjunto | Para que serve | Quando é usado |
| :-- | :-- | :-- |
| **Treino** | Ajustar os parâmetros do modelo | Durante o treinamento |
| **Validação** (parte do treino) | Acompanhar a generalização, parar o treino, escolher hiperparâmetros | **Durante** o treinamento, repetidamente |
| **Teste** | Estimativa final e honesta | **Uma vez**, no **final** |

⚠ **Armadilha:** confundir validação com teste. O de validação faz parte do processo de ajuste e pode ser consultado várias vezes; o de teste **não pode** influenciar nenhuma decisão.

```python
# ERRADO: escolhe o hiperparâmetro olhando o teste
melhor = None
for k in [1, 3, 5, 15, 31]:
    nota = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train).score(X_test, y_test)
    # ... guarda o k com maior nota no TESTE ...
# a nota final do melhor k é otimista

# CERTO: escolhe com validação cruzada DENTRO do treino; testa uma vez no fim
from sklearn.model_selection import cross_val_score
for k in [1, 3, 5, 15, 31]:
    nota = cross_val_score(KNeighborsClassifier(n_neighbors=k), X_train, y_train, cv=5).mean()
# fica com o melhor k, treina com todo o treino e mede UMA vez no teste
```

Figura típica (slide 34): perda de treino sempre caindo; perda de validação cai, atinge um mínimo e volta a subir. O ponto do mínimo é onde parar.

> **Se perguntarem na prova:** conjunto de validação = subconjunto do treino, usado durante o treinamento para acompanhar a generalização e permitir parada antecipada; o teste final é feito no conjunto de teste, uma vez.

---

## 14. Checklist para avaliar um modelo sem se enganar

Use esta lista como roteiro para qualquer questão de "o que há de errado neste experimento?":

1. **Os dados representam o problema real?** (Viés de amostragem: quem ficou de fora? Como coletaram?)
2. **Há dados suficientes?** Se não, use estratégia de amostragem (validação cruzada).
3. **Os dados estão limpos e os atributos são relevantes?** (Ruído, outliers, colunas inúteis.)
4. **Há atributo que só existe depois do evento?** (Vazamento de atributos.)
5. **Há duplicatas?** Remover **antes** de dividir.
6. **Os dados são temporais?** Divisão por ordem de tempo; **nunca embaralhar**.
7. **Separou o teste antes de qualquer `fit`?** (Normalização, imputação, seleção de atributos e modelo só veem o treino.)
8. **Qual estratégia de validação?** Base grande → hold-out. Base pequena → validação cruzada. Para estabilidade → média e desvio padrão.
9. **Os hiperparâmetros foram escolhidos com validação, e não olhando o teste?**
10. **Comparou erro de treino e de teste?** Treino baixo e teste alto = overfitting. Os dois altos = underfitting.
11. **Desvio padrão alto entre as rodadas?** Modelo ou avaliação instável.
12. **Usou o teste uma única vez, no final?**
13. **Se a nota parece boa demais para ser verdade**, desconfie de vazamento.

---

## Vocabulário em um quadro

| Termo | Significa |
| :-- | :-- |
| Generalização | Funcionar bem em dados novos, nunca vistos |
| Viés de amostragem (sampling bias) | Dados de treino que não representam o problema real |
| Dados não representativos | Amostra que não reflete o problema em que o modelo operará |
| Ruído / outlier | Erro nos dados / valor muito fora do padrão |
| Seleção / agregação de atributos | Escolher ou combinar colunas para ficar só com as relevantes |
| Overfitting (sobreajuste) | Decorou o treino; erro de treino baixo, de teste alto |
| Underfitting (subajuste) | Simples demais; erro alto em treino **e** teste |
| Over-training | Treinar iterações demais (causa de overfitting) |
| Complexidade do modelo | Quanta "flexibilidade" o modelo tem para ajustar os dados |
| Regularização | Penalizar a complexidade para evitar overfitting [complemento] |
| Hold-out | Uma divisão única treino/teste (⅔–⅓ ou 80–20) |
| Amostragem aleatória | Várias divisões aleatórias; média e desvio padrão |
| Desvio padrão alto | Resultados instáveis conforme a amostra |
| Validação cruzada (k-fold) | K partes; K rodadas; cada parte é o teste uma vez |
| Fold | Um dos K pedaços da validação cruzada |
| Conjunto de validação | Subconjunto do treino usado durante o treinamento para acompanhar a generalização |
| Parada antecipada (early stopping) | Interromper o treino quando o erro de validação começa a subir |
| Data leakage (vazamento de dados) | Informação do teste ou do futuro entra no treino |
| Divisão temporal (Time Series Split) | Treino = passado, teste = futuro |
| `fit` / `transform` | Aprender uma estatística (só no treino) / aplicá-la (no treino e no teste) |
| Viés (bias) | Erro sistemático; alto viés = underfitting |
| Variância | Variação das previsões com outros dados; alta variância = overfitting |
| Trade-off viés-variância | Mais complexidade: menos viés, mais variância; buscar o ponto ótimo |

Próximo passo: faça as questões da Aula 4. Responda **antes** de ler as explicações, mesmo que seja no chute, e leia a explicação de **todas** as alternativas, não só da correta.
