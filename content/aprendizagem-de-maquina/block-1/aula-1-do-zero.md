# Aula 1 do zero: o que é aprendizado de máquina, afinal?

Este texto assume que você **sabe programar** e **não sabe nada de ciência de dados**. Cada ideia vem primeiro com uma analogia de software, depois com o termo técnico que a professora usa nos slides. As palavras em **negrito** são as que podem aparecer na prova.

Leia na ordem. No fim de cada seção há uma frase "Se perguntarem na prova", que é o resumo do que precisa ficar.

---

## 1. Programar do jeito de sempre × deixar a máquina descobrir a regra

Imagine que você precisa fazer um filtro de spam.

**Jeito convencional (o que você já faz).** Você escreve as regras:

```python
def e_spam(email):
    if "ganhou" in email.texto and "sorteio" in email.texto:
        return True
    if email.remetente not in agenda_de_contatos and email.tem_link:
        return True
    return False
```

Você olhou para spams, percebeu padrões e **codificou as regras à mão**. A máquina só executa. Entrada + regras → saída.

**Jeito do aprendizado de máquina (AM).** Você não escreve as regras. Você entrega à máquina **10 mil e-mails que alguém já marcou como "spam" ou "não spam"**, e um programa **descobre sozinho** quais características separam uns dos outros. Entrada + saídas conhecidas → regras (que ficam guardadas num **modelo**).

| | Algoritmo convencional | Aprendizado de máquina |
| :-- | :-- | :-- |
| Quem escreve as regras | O programador | A própria máquina, a partir de exemplos |
| O que você fornece | As regras | Exemplos (com a resposta certa) e um jeito de medir se está acertando |
| Quando compensa | Regra simples e conhecida | Regra difícil de escrever (reconhecer rosto, voz, fraude) |

O slide 14 diz exatamente isso: no AM, "os meios de avaliar o desempenho obtido até o momento são fornecidos, assim como o modo de buscar novas hipóteses". Traduzindo: a máquina recebe uma **nota** (quanto acertou) e um **método de tentar de novo** com ajustes.

> **Se perguntarem na prova:** no algoritmo convencional o programador especifica as regras; no AM a máquina descobre as regras a partir dos dados.

---

## 2. IA e AM não são a mesma coisa

- **Inteligência Artificial (IA)** é o campo **grande**: tudo que faz máquinas se comportarem de forma inteligente.
- **Aprendizado de Máquina (AM, *machine learning*)** é uma **parte** da IA: a que cria algoritmos que **aprendem a partir de dados**.

Pense em "veículos" e "carros": todo carro é veículo, nem todo veículo é carro. **A IA inclui o AM, mas o AM não define toda a IA** (slide 10).

**Um pouco de história (slides 10 e 11).** Em **1950**, Alan Turing publicou *Computing Machinery and Intelligence* e propôs o **Jogo da Imitação**, uma forma de perguntar "uma máquina pode pensar?":

- Há três participantes: **A** é um computador, **B** é uma pessoa, e **C** é um juiz (uma pessoa que **não vê** nem A nem B, só conversa por escrito).
- A e B tentam convencer C de que são humanos.
- Se C **não consegue decidir de forma coerente** quem é a máquina, **o computador vence**.

**Por que a IA "explodiu" a partir de 2012 (slide 17)?** Três pilares:

1. **Big Data**: a internet gerou um volume enorme de fotos, vídeos e textos para treinar os modelos.
2. **Poder de processamento (GPUs)**: chips de placa de vídeo eram ótimos para as contas que a IA exige.
3. **Arquiteturas avançadas**: redes como as **CNNs** (para imagem) e, mais recentemente, os **Transformers** (a base do ChatGPT).

> **Se perguntarem na prova:** IA ⊃ AM. Turing, 1950, Jogo da Imitação. Os pilares da IA moderna: dados em volume, GPUs e novas arquiteturas.

---

## 3. Raciocínio indutivo: aprender com exemplos

Há duas formas de raciocinar:

- **Dedução**: parte de uma **regra geral** e chega a um **caso particular**. "Todo mamífero tem coluna vertebral; um cão é mamífero; então cão tem coluna." Se a regra geral for verdadeira, a conclusão é garantida.
- **Indução**: parte de **vários casos particulares** e chega a uma **regra geral**. "Vi 1.000 cães; todos latiam; então cães latem." A conclusão é uma **aposta bem fundamentada**, não uma garantia.

**O AM é indutivo.** É assim que uma criança aprende o que é um cachorro: ninguém dá a definição formal, ela vê vários exemplos e generaliza.

**Em código (slide 18).** A dedução é como **executar** uma função que já existe: você chama `e_spam(email)` e a regra geral (escrita por você) produz o caso particular. A indução é o caminho inverso, é **escrever a função a partir de exemplos**: você olha 1.000 e-mails e tenta descobrir qual regra geral os explica. O AM automatiza esse segundo caminho. Note que o slide 18 diz que o raciocínio dedutivo obtém conclusões sobre algo **em particular** a partir de conhecimento **geral**, e que a indução obtém conclusões **gerais** a partir de um conjunto **particular** de exemplos. Os dois sentidos são opostos; não troque.

Mas a indução tem um **risco** (slide 19): se os exemplos forem **poucos** ou **mal escolhidos**, a regra que você tira deles pode valer pouco. Se a criança só viu poodles brancos, pode concluir que "cachorro é branco e pequeno". Guarde essa ideia: ela volta na Aula 4 como **viés de amostragem**.

> **Se perguntarem na prova:** a indução generaliza a partir de exemplos; exemplos insuficientes ou mal escolhidos geram conclusões de pouco valor.

---

## 4. Como os dados são organizados (isso você vai usar o tempo todo)

Pense numa **tabela de banco de dados**:

| Idade | Peso (kg) | Fumante | Diagnóstico |
| :-- | :-- | :-- | :-- |
| 52 | 80 | sim | doente |
| 31 | 65 | não | saudável |
| 45 | 90 | sim | doente |

- Cada **linha** é uma **amostra** (também chamada de **exemplo**, **registro**, **padrão**, **instância**). Corresponde a uma ocorrência: um paciente.
- Cada **coluna** é um **atributo** (também chamado de **característica**, **campo**, **variável**, ***feature***). Corresponde a uma propriedade da amostra.
- Uma linha, vista como lista de valores, é um **vetor de características**: `[52, 80, sim]`.

Os atributos têm dois papéis (slide 29):

- **Atributos preditivos** (as entradas, o "X"): descrevem o objeto. Aqui: idade, peso, fumante.
- **Atributo alvo** (a saída, o "y"; também **rótulo**, **classe**): o que se quer prever. Aqui: diagnóstico.

> **Analogia de software:** os preditivos são os **parâmetros de entrada** de uma função; o alvo é o **valor de retorno** que você gostaria que a função devolvesse.

**Cuidado com colunas de identificação** (nome, matrícula, CPF): elas não ajudam a aprender e geralmente são removidas, porque o modelo poderia "decorar" quem é quem em vez de aprender o padrão.

> **Se perguntarem na prova:** amostra = linha; atributo = coluna; atributo alvo = o que se quer prever.

---

## 5. Os dois grandes tipos de aprendizado

A pergunta que separa os dois é: **a tabela tem a coluna do alvo?**

| | **Supervisionado** | **Não supervisionado** |
| :-- | :-- | :-- |
| A base tem atributo alvo? | **Sim** (cada exemplo vem com a "resposta certa") | **Não** |
| Analogia | Estudar com **gabarito**: o professor corrige | Receber uma pilha de documentos e **organizar sozinho** sem ninguém dizer como |
| Natureza da tarefa | **Preditiva**: prever o alvo de um objeto novo | **Descritiva**: descobrir e descrever padrões nos dados |

**Pegadinha clássica:** "a base tem atributo alvo, logo é não supervisionado." **Errado.** Com alvo = **supervisionado**. Sem alvo = **não supervisionado**.

### A definição formal do supervisionado e o argmax (slide 53)

O slide 53 define o aprendizado supervisionado por três equações (que aparecem como imagem, então o que vale é o texto do slide). Em linguagem de programador:

- Existe uma função **verdadeira e desconhecida** `f(x)`: a regra do mundo real que liga a entrada `x` ao alvo (por exemplo, "este e-mail é spam?"). Você nunca a vê; só vê **exemplos** dela, o conjunto de dados `D` (pares entrada e saída).
- Existe um **conjunto de hipóteses** `H`: todas as funções candidatas que o seu tipo de modelo consegue representar (todas as retas possíveis `w × x + b`, por exemplo). Cada **hipótese** `h` é uma dessas candidatas.
- Aprender é **escolher a `h` dentro de `H` que melhor se ajusta aos dados `D`**. O símbolo **argmax** significa "o argumento que maximiza": não é o valor máximo, é **qual hipótese** produz o máximo.

```python
# argmax em código: devolve QUAL candidata ganha, não a nota dela
melhor_h = max(H, key=lambda h: probabilidade(h, D))   # argmax
nota     = probabilidade(melhor_h, D)                   # isto seria o max
```

O slide diz que a hipótese escolhida é a que **maximiza a função de probabilidade que relaciona cada hipótese aos dados de entrada e saída**. Ou seja: entre todas as retas, fica a que torna os dados observados **mais prováveis**. No fim, espera-se que `h` fique **tão próxima quanto possível** da `f(x)` verdadeira. Analogia: `f` é o comportamento real de um sistema legado que você não pode ler; `h` é a sua reimplementação, escolhida entre várias versões por ser a que **melhor reproduz as respostas** observadas dele.

> **Se perguntarem na prova:** argmax = o argumento (a hipótese `h` de `H`) que maximiza a probabilidade dada `D`; o objetivo é `h` o mais próxima possível de `f(x)`. Notações como f̂(x) ou "estimador" em outros materiais são nomes diferentes para a mesma ideia; use `h` e `H`, como no slide.

---

## 6. As quatro tarefas principais

### Dentro do supervisionado (tarefas preditivas)

O que muda é o **tipo do alvo**:

- **Classificação**: o alvo é **discreto**, ou seja, um conjunto **finito** de valores possíveis, chamados de **classes**. Exemplos: spam/não spam; doente/saudável; bom pagador/mau pagador; qual dígito (0 a 9) aparece numa imagem.
- **Regressão**: o alvo é **contínuo**, ou seja, um número que pode cair em qualquer ponto de um intervalo. Exemplos: preço de uma casa, lucro de uma empresa, temperatura de amanhã. O algoritmo busca uma **equação** que leve das entradas à saída.

**Teste rápido para decidir:** "a resposta é uma **categoria** ou um **número com valores intermediários**?" Categoria → classificação. Número → regressão. (Atenção: um código de classe como 0, 1, 2 **não** torna a tarefa uma regressão. Se são categorias, continua sendo classificação.)

A classificação ainda se divide em **binária** (duas classes, como sim/não) e **multiclasse** (várias classes possíveis). ⚠ O slide 44 chama a multiclasse de "multilabel". Na literatura, *multilabel* (multirrótulo) é outra coisa: um mesmo objeto recebe **vários rótulos ao mesmo tempo** (um filme que é "comédia" e "romance"). Na prova, responda com a nomenclatura do slide, mas saiba a diferença.

### Dentro do não supervisionado (tarefas descritivas)

- **Agrupamento** (*clustering*): reunir exemplos **parecidos** em grupos, sem saber de antemão quais são os grupos. Os grupos são nomeados **depois**, por uma pessoa. Exemplo: separar notícias por assunto sem que ninguém tenha classificado nenhuma. Usos: segmentar clientes por perfil, achar **outliers** (pontos que não se parecem com ninguém), criar filtros automáticos.
- **Associação**: achar **itens que aparecem juntos** em transações. Exemplo clássico: quem compra fralda também compra cerveja. A base é de transações (compras, filmes assistidos).

**Associação em detalhe (slides 63 a 66).** O slide 63 define a tarefa como identificar padrões, como **valores que ocorrem juntos num mesmo exemplo** da base. Os slides 64 a 66 são só figuras (o exemplo de compras); o que importa é a ideia. A base é uma lista de **transações**, cada uma sendo um conjunto de itens:

| Transação | Itens |
| :-- | :-- |
| 1 | pão, leite, manteiga |
| 2 | pão, manteiga |
| 3 | leite, cerveja, fralda |
| 4 | pão, leite, manteiga, fralda |

Repare que **não existe coluna alvo**: ninguém diz "o que prever". O algoritmo varre as transações e devolve **regras do tipo "quem leva pão e manteiga também costuma levar leite"**. Aqui, pão e manteiga aparecem juntos em 3 das 4 transações. Analogia de software: é como analisar **logs de requisições** para descobrir que "quando o endpoint `/login` é chamado, `/perfil` quase sempre vem logo em seguida", sem ter definido isso antes. O resultado é uma **descrição** dos dados, por isso a tarefa é descritiva e não supervisionada. Usos: recomendação ("quem assistiu a este filme também assistiu a..."), disposição de produtos na loja, promoções combinadas.

> **Confusão a evitar:** associação **não** agrupa clientes (isso é agrupamento) e **não** prevê um alvo (isso é supervisionado). Ela só encontra **o que ocorre junto**.

> **Diferença que cai em prova:** no **agrupamento** você forma **grupos de objetos parecidos**; na **associação** você descobre **que itens ocorrem juntos**. E repare: o agrupamento do slide 58 mostra que um grupo achado pela máquina **pode não ter significado relevante**; os parâmetros (como o número de grupos) mudam o resultado.

### Resumo em uma figura mental

```
Aprendizado de máquina
├── Supervisionado (tem alvo)  → tarefas preditivas
│   ├── Classificação  (alvo discreto: classe)
│   └── Regressão      (alvo contínuo: número)
└── Não supervisionado (sem alvo) → tarefas descritivas
    ├── Agrupamento    (formar grupos por similaridade)
    └── Associação     (itens que ocorrem juntos)
```

---

## 7. Três variações que ficam "fora" da árvore clássica (slide 67)

| Aprendizado | Ideia em uma linha | Exemplo |
| :-- | :-- | :-- |
| **Semissupervisionado** | **Parte** dos dados tem rótulo, parte não. O modelo aprende com os rotulados e **rotula os outros quando tem boa confiança**, depois retreina. Existe porque **rotular é caro**. | 500 fotos rotuladas e 50 mil sem rótulo |
| **Ativo** | É um semissupervisionado em que o algoritmo **escolhe quais** exemplos mandar para um humano rotular, para não gastar rótulo com exemplo redundante. | O sistema pede ao médico que rotule só os exames mais "duvidosos" |
| **Por reforço** | Um **agente** age num ambiente, recebe **recompensa** quando acerta e **punição** quando erra, e aprende sozinho a melhor estratégia. | Robô aprendendo a melhor trajetória entre dois pontos |

**Semissupervisionado, em mais detalhe (slides 68 a 70).** O slide 69 diz que existem **dois sabores**:

- **Classificação (ou regressão) semissupervisionada**: só parte dos exemplos tem rótulo de classe. É o caso das 500 fotos rotuladas.
- **Agrupamento semissupervisionado com restrições**: aqui **nenhum** dado tem rótulo, mas você conhece **restrições entre pares de objetos**: "estes dois **devem** ficar no mesmo grupo" e "estes dois **não podem** ficar no mesmo grupo". Exemplo: ao agrupar chamados de suporte, um analista aponta que os chamados A e B são o mesmo problema (devem ficar juntos) e que A e C são problemas diferentes (devem ficar separados). Você não deu nome a nenhum grupo; só deu **dicas sobre pares**. Analogia de software: é um agrupamento comum (não supervisionado) ao qual você adiciona **regras de validação** (`must_link(a, b)`, `cannot_link(a, c)`) que o algoritmo precisa respeitar.

O slide 70 descreve o **laço de autotreinamento**: (1) treina com os rotulados; (2) usa o modelo para prever a classe dos não rotulados; (3) os que foram preditos **com boa confiança** ganham o rótulo previsto e entram no treino; (4) repete até acabar a condição. Observe a crítica no final do slide: como **todos** os dados não rotulados acabam rotulados, entram também **exemplos redundantes** que pouco ajudam. Esse é o problema que o aprendizado ativo resolve.

**Aprendizado ativo, em mais detalhe (slide 72).** É uma estratégia semissupervisionada que **seleciona interativamente** quais amostras serão rotuladas, para **evitar amostras redundantes** e melhorar o modelo. As amostras **não selecionadas são descartadas** (detalhe do slide). A diferença para o semissupervisionado "passivo" do slide 70 está em quem decide: no passivo o modelo usa tudo que tem; no ativo o algoritmo **escolhe e pergunta**. Exemplo: você tem 50 mil imagens de raio-X sem rótulo e um radiologista que só consegue rotular 200. O algoritmo treina um modelo inicial e pede ao radiologista justamente os exames sobre os quais **tem mais dúvida**, e não 200 sorteados ao acaso (que seriam quase todos casos fáceis e parecidos). Analogia de software: é a **triagem de bugs**: com uma pessoa só para revisar, você não revisa os 50 mil logs, e sim os poucos que o classificador não sabe resolver. O "humano no laço" é chamado de oráculo na literatura.

> **Analogia:** o semissupervisionado é estudar com poucas questões corrigidas e muitas sem gabarito. O ativo é você escolher quais questões pedir para o professor corrigir. O reforço é aprender videogame jogando: pontos sobem ou descem, ninguém explica a regra.

---

## 8. Classificação, em duas fases (slide 39)

Toda classificação acontece em **duas etapas separadas no tempo**:

1. **Fase de aprendizagem (ou treinamento).** Um **algoritmo de aprendizagem** (também chamado de **algoritmo de indução** ou **indutor**) recebe amostras com a classe conhecida e **constrói um modelo classificador**.
2. **Fase de reconhecimento (uso).** O classificador pronto é aplicado a **objetos novos** para determinar a classe deles.

Analogia: a fase 1 é o **build/treino**; a fase 2 é o **runtime em produção**. O algoritmo é o compilador; o modelo é o binário.

**Dois tipos de abordagem** (slides 45 e 46, só para reconhecer os nomes):

- **Estatísticos**: a saída é uma **probabilidade** e a classe sai de um **limiar** (*threshold*). Ex.: regressão logística, Naïve Bayes, redes bayesianas, SVM.
- **Estruturais**: baseados em **regras**, **distâncias** ou **redes neurais**. Ex.: árvores de decisão, k-NN, Random Forest, MLP.

Você vai estudar vários deles nas próximas aulas; por enquanto basta saber que existem essas duas famílias.

**Como distinguir (slides 44 a 46).** O slide 44 avisa que os classificadores parecem semelhantes, mas têm funções e objetivos diferentes, e que a escolha da abordagem (estatística ou estrutural) depende do caso. O critério é **o que o modelo devolve e como decide**:

- **Estatístico** devolve um **número entre 0 e 1** (probabilidade de pertencer à classe) e um **limiar** (*threshold*) converte isso em decisão. Exemplo: o modelo diz "probabilidade de spam = 0,83"; com limiar 0,5, a classe é "spam". Analogia: um `if score > 0.5`. Mudar o limiar muda a decisão sem retreinar o modelo.
- **Estrutural** decide por uma **estrutura**: uma sequência de regras (árvore de decisão: "se idade > 40 e fumante, então doente"), **distâncias** (k-NN: "a classe dos vizinhos mais próximos") ou **neurônios** (rede neural). Analogia: um `if/else` aninhado, ou uma busca "quem se parece mais com este exemplo?".

> **Se perguntarem na prova:** estatísticos = saída em probabilidade + limiar (regressão logística, Naïve Bayes, redes bayesianas, SVM, Gaussian Process); estruturais = regras, distâncias ou redes neurais (árvores de decisão, k-NN, Random Forest, MLP). O slide 44 chama de "multilabel" a classificação com várias classes; use a nomenclatura do slide, mas saiba a diferença (seção 6).

---

## 9. Treino e teste: a ideia mais importante do curso

Imagine que você quer saber se um aluno aprendeu a matéria. Se a prova tiver **exatamente as mesmas questões** que ele treinou, uma nota alta não prova que ele aprendeu: ele pode ter **decorado as respostas**.

O AM tem o mesmo problema, então separamos os dados:

- **Dados de treino**: os exemplos que o modelo **vê** para aprender (com a resposta certa).
- **Dados de teste**: exemplos que o modelo **nunca viu**, guardados para a "prova". Mede-se o percentual de acertos (a **acurácia**) **só neles**.

Exemplo do slide 25: para um modelo que reconhece cachorros, o treino usa fotos de cães e não cães já rotuladas; o teste usa **fotos novas**, que não participaram do treinamento.

> **Se perguntarem na prova:** o teste deve usar dados que o modelo **não viu** no treinamento. Testar com os mesmos dados do treino não mede aprendizado.

---

## 10. O processo de AM em 7 etapas (slides 75 a 82)

Pense num **pipeline de entrega de software**. A ordem importa, e a prova gosta de perguntar "a ordem está certa?".

| # | Etapa | O que acontece | Analogia de software |
| :-- | :-- | :-- | :-- |
| 1 | **Coleta de dados** | Reunir exemplos em **quantidade** e **qualidade** suficientes. Mais exemplos tende a ajudar; qualidade depende de escolher bons atributos. | Levantar requisitos e fontes de dados |
| 2 | **Preparação dos dados** | Corrigir dados incompletos, inconsistentes, duplicados ou ruidosos; mudar escala, normalizar, discretizar; checar **balanceamento** das classes; **separar treino e teste**. | Limpeza e normalização antes de usar a entrada |
| 3 | **Seleção do modelo** | Escolher o tipo de modelo adequado ao tipo de dado e à complexidade (regressão linear, logística, agrupamento, aprendizado profundo…). | Escolher a arquitetura |
| 4 | **Treinamento** | O modelo melhora **a cada exemplo avaliado**, ajustando seus **parâmetros**. | Compilar/otimizar |
| 5 | **Avaliação** | Usar os **dados de teste** separados para ver se acerta em dados desconhecidos. | Testes de aceitação |
| 6 | **Ajuste de parâmetros** (de **hiper**parâmetros) | Definir novos valores dos controles do processo de aprendizado e repetir. | Tunar configurações |
| 7 | **Aplicação** | Usar o modelo treinado para fazer previsões reais. | Deploy |

### Detalhes de cada etapa (slides 76 a 81)

- **Coleta (76).** O slide diz que mais exemplos é melhor, e que a **qualidade** depende dos **atributos escolhidos**: priorize os mais relevantes para o modelo. Os dados podem incluir atributos previsores e, conforme o tipo de aprendizado, o **alvo** (supervisionado tem alvo; não supervisionado não).
- **Preparação (77).** Lista do slide: transformação de unidade, conversão de escala, normalização, discretização, mudança de representação; avaliar o **balanceamento** (se cada classe ou faixa aparece em quantidade parecida; exemplo: 95% de e-mails normais e 5% de spam é desbalanceado); tratar ou eliminar dados **incompletos, inconsistentes, duplicados ou ruidosos**.
- **Divisão treino/teste (78).** O slide 78 coloca a separação **ainda na preparação**, antes do modelo. Isso é importante: a divisão acontece cedo, e o teste fica guardado até a avaliação. Motivo dado: não confundir um modelo **especializado nos dados de treino** com um que **generaliza**.
- **Seleção do modelo (79).** Escolher conforme o **tipo de dado** e a **complexidade**; os exemplos do slide são regressões lineares, regressões logísticas, classificação, agrupamento e aprendizado profundo.
- **Treinamento (80).** Melhorar o modelo **a cada amostra avaliada**, alterando só os parâmetros w e b.
- **Avaliação, ajuste e aplicação (81).** Avalia nos dados separados; depois, se preciso, define novos hiperparâmetros e repete; por fim usa o modelo.

**Ordem em código** (um erro de ordem aqui é pegadinha típica de prova):

```python
X_tr, X_te, y_tr, y_te = train_test_split(X, y)   # 2. preparação: separa cedo
modelo = EscolheModelo()                           # 3. seleção
modelo.fit(X_tr, y_tr)                             # 4. treinamento (só com treino)
acc = modelo.score(X_te, y_te)                     # 5. avaliação (só com teste)
# 6. ajusta hiperparâmetros e volta ao passo 4
# 7. modelo.predict(dados_novos)                   # aplicação
```

Avaliar **antes** de treinar, ou treinar com o teste, são exemplos de ordem errada. Observação de nomenclatura: o slide 75 chama a etapa 6 de "ajuste de parâmetros", mas o slide 81 deixa claro que o que se ajusta ali são os **hiperparâmetros**; os parâmetros w e b são ajustados sozinhos na etapa 4.

### Parâmetros × hiperparâmetros (confusão frequente)

O slide 80 usa o exemplo mais simples possível: **uma reta**, `saída = w × entrada + b`.

- **w** é o **peso** e **b** é o **viés** (*bias*). São os **parâmetros do modelo**. **O treinamento mexe neles** para a reta passar o mais perto possível dos dados.
- **Hiperparâmetros** são os controles **do processo de aprendizado**, definidos **por você**, antes ou entre os treinos. Exemplos do slide 81: a **quantidade de repetições** sobre o conjunto de treino e a **taxa de aprendizado** (o tamanho de cada ajuste dos parâmetros).

> **Analogia:** parâmetros são as **variáveis que o programa aprende** (como os pesos guardados no modelo). Hiperparâmetros são as **flags de configuração** que você passa na linha de comando (`--epochs 50 --lr 0.01`).

**Mesma distinção em código (slide 81).**

```python
modelo = Modelo(taxa_aprendizado=0.01, repeticoes=50)  # hiperparâmetros: VOCÊ escolhe
modelo.fit(X_tr, y_tr)                                  # o treino descobre w e b
print(modelo.w, modelo.b)                               # parâmetros: o MODELO aprendeu
```

Os dois hiperparâmetros do slide: **quantidade de repetições** (quantas vezes o processo percorre todo o conjunto de treino; na literatura costuma se chamar épocas) e **taxa de aprendizado** (o "fator" que diz o quanto w e b mudam a cada ajuste). Taxa pequena demais: o aprendizado é lento. Grande demais: os ajustes passam do ponto e o modelo não se acerta. Regra de bolso: **parâmetro = o treino calcula; hiperparâmetro = você define e testa valores diferentes**. Cuidado: alguns materiais chamam os hiperparâmetros de "parâmetros". Na prova, siga o slide: parâmetros são w e b.

---

## 11. Generalização: o objetivo final (slide 82)

Um modelo bem-sucedido deve valer **não só para os dados de treino, mas para casos futuros**. Isso é a **capacidade de generalização**. Quanto mais o resultado esperado e o obtido coincidem **em dados novos**, maior a generalização.

**Em código:** um modelo que não generaliza é como um teste unitário que passa só porque você **fixou (hardcoded) a resposta esperada** para os casos do teste. Funciona nos casos conhecidos e quebra no primeiro input novo. Exemplo numérico: um modelo acerta 100% das fotos de treino mas só 60% das fotos novas; ele decorou. Outro acerta 88% no treino e 86% no teste; ele generalizou. O que mede a generalização é o desempenho **nos dados de teste** (seção 9), porque são os que simulam "casos futuros". O slide também condiciona o sucesso a haver **iterações suficientes** para a máquina aprender: sem repetições suficientes, nem os dados de treino são aprendidos.

Se o modelo só funciona nos dados que viu, ele **não é inteligente**: é um "especialista nos dados treinados" (um **decorador**). Esse problema tem nome, **overfitting**, e é o tema central da Aula 4.

---

## Vocabulário em um quadro

| Termo | Significa |
| :-- | :-- |
| Amostra / exemplo / registro / instância | Uma linha da tabela |
| Atributo / feature / característica / variável | Uma coluna da tabela |
| Atributo preditivo | Coluna usada como entrada |
| Atributo alvo / rótulo / classe | Coluna que se quer prever |
| Supervisionado | Base **com** alvo |
| Não supervisionado | Base **sem** alvo |
| Classificação | Alvo **discreto** (classes) |
| Regressão | Alvo **contínuo** (número) |
| Agrupamento | Formar grupos por similaridade, sem alvo |
| Associação | Achar itens que ocorrem juntos em transações |
| Modelo | O que o treinamento produz e guarda (as "regras aprendidas") |
| Treinar | Ajustar os parâmetros do modelo com os dados de treino |
| Parâmetro | Valor que o treinamento ajusta (peso `w`, viés `b`) |
| Hiperparâmetro | Controle que **você** define (taxa de aprendizado, repetições) |
| Generalizar | Funcionar bem em dados novos |

Próximo passo: faça as questões da Aula 1. Responda **antes** de ler as explicações, mesmo que seja no chute, e leia a explicação de **todas** as alternativas, não só da correta.
