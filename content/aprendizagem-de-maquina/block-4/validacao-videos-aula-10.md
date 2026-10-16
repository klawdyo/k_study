# Validação dos vídeos pela transcrição — Aula 10 (Redes Neurais: Perceptron e MLP)

Método: li a transcrição inteira, por minuto, de cada vídeo citado abaixo (arquivos em `estudo/conteudo/transcripts/`) e comparei com os 52 slides de `Aulas/Aula 10 - Redes Neurais` (texto em `estudo/_fontes_extraidas/Aulas__Aula_10_-_Redes_Neurais.pptx.txt`). Todas as durações conferem com o campo `duration` da transcrição. Os `mm:ss` têm precisão de cerca de ±15 s (a legenda vem em blocos). A transcrição é automática (Whisper) e erra termos: "minibet" = mini-batch, "número de order" = número de Euler, "Vs" = viés, "laço" aparece onde se esperava Lasso/Ridge.

Esta ficha **substitui** a versão anterior, que não era confiável. Erros que encontrei nela (e nos itens `a10-v1` a `a10-v5` do `block.json`):

- `a10-v1` (Fernando dos Santos, Perceptron): dizia cobrir "algoritmo de correção de erro e ajuste de conexões, slides 12 a 17" em 08:00–11:02. O vídeo termina anunciando esse algoritmo como "próximo tópico" (09:57). Também dizia cobrir XOR/MCP em 00:30–01:15; não cobre.
- `a10-v4` (Pistori, ativação): os clips apontavam a ReLU em 05:00–09:00; ela está em 08:17–12:15. Dizia cobrir "degrau" e "linear" (slides 46 e 47): não cobre. O título do item estava inventado ("Sigmoide, ReLU e Softmax").
- `a10-v3` (Didática Tech, SGD): dizia cobrir "taxa de aprendizado" (slide 41) em 08:30–13:30. A palavra não aparece no vídeo. O que ele cobre bem é o mini-lote e o SGD (slides 34 e 36).
- `a10-v2` (Sandeco, Backpropagation): dizia cobrir os slides 21 a 24 inteiros; cobre bem a ideia de funções aninhadas e regra da cadeia, mas termina sem mostrar o ajuste das camadas ocultas.
- Títulos de vários itens não eram os reais do YouTube; foram corrigidos na proposta.
- A ficha falava em "12 vídeos avaliados em português": só 5 constavam; as demais transcrições (órfãs) nunca tinham sido lidas.

Legenda: **B** cobre bem · **P** cobre em parte · **X** cobre mas diverge do slide · **L** lacuna (a leitura cobre).

## 1. Tópicos por slide (critério de cobertura)

| Slide | Tópico |
| :-- | :-- |
| 1 e 2 | Título da aula e do assunto (sem conteúdo) |
| 3 | Neurônio biológico: bilhões de neurônios, milhares de sinapses cada |
| 4 | Dendritos (entrada), corpo (soma, processa), axônio (saída); impulso só passa se for forte o bastante. Traz [IMAGEM] |
| 5 | Plasticidade: o cérebro aprende reforçando ou enfraquecendo conexões |
| 6 | Rede neural artificial: unidades simples, camadas, conexões com pesos que guardam o conhecimento. [IMAGEM] |
| 7 | Neurônio MCP (McCulloch e Pitts, 1943). Quase só [IMAGEM] |
| 8 | MCP: entradas x, pesos w, uma saída y; pesos guardam o conhecimento (plasticidade). [IMAGEM] |
| 9 | MCP: função de ativação e limiar; **o MCP não aprende**. [IMAGEM] |
| 10 | Perceptron (Rosenblatt, 1958): aprendizagem por correção do erro; uma camada; converge se o problema for linearmente separável. [IMAGEM] |
| 11 | Aprendizado = ajuste dos pesos usando o erro |
| 12 | Correção de erro: e = Yd − Y; w novo = w + n·e·x; taxa de aprendizagem pequena |
| 13 a 17 | Exemplo numérico do Perceptron (E lógico): 13 é só [IMAGEM]; 14 codificar entradas e saída ([IMAGEM]); 15 pesos aleatórios em [0; 1] e taxa 0,3; 16 e 17 só [IMAGEM] |
| 18 | Limitação: uma camada só resolve problemas lineares; camadas intermediárias + ativação não linear. [IMAGEM] |
| 19 e 20 | Rede de Perceptrons (MLP): camadas tomam decisões cada vez mais abstratas; um Perceptron tem uma saída, as setas múltiplas só reutilizam a saída. [IMAGEM] |
| 21 | MLP: o erro só é conhecido na saída; como estimar o erro das camadas intermediárias? |
| 22 | Backpropagation (Rumelhart, 1986): conexão forte → ajuste grande; fraca → ajuste pequeno |
| 23 | Fase forward: entrada, soma, ativação não linear, erro na saída |
| 24 | Fase backward: regra da cadeia, derivadas parciais, gradiente, SGD, convergência |
| 25 | Função de custo; MSE; minimizar C(w, b) com descida do gradiente. [IMAGEM] |
| 26 a 28 | Gradiente descendente: descer pelo negativo do gradiente; analogia do vale e da bola; derivadas dão a forma local. [IMAGEM] |
| 29 e 30 | Derivada = inclinação da tangente; sinal da derivada; vetor gradiente. [IMAGEM] |
| 31 a 33 | Passos: valor inicial; custo; derivada; coeficiente = coeficiente − alfa × delta; repetir até o custo chegar perto de zero |
| 34 | Mini-batch (ex. 128 amostras): erro médio e atualização; forma mais comum |
| 35 | Hiperparâmetros: camadas, neurônios, otimizador, taxa de aprendizado, função de ativação |
| 36 | Otimizadores: gradiente descendente, SGD (taxa fixa), Adam (taxa por peso, adaptativa) |
| 37 a 40 | Regularização: parada antecipada (validação), L1 e L2 (constante × proporcional a w), Ridge/Lasso, Dropout |
| 41 | Taxa de aprendizado: pequena demora, grande ultrapassa o mínimo; valores 0.001 a 0.3. [IMAGEM] |
| 42 a 45 | Função de ativação: por que uma pequena mudança no peso deve dar uma pequena mudança na saída; decide se o neurônio ativa; transformação não linear; sem ela a rede é regressão linear |
| 46 | Degrau (gradiente zero, só didática) |
| 47 | Linear (derivada constante; saída de regressão) |
| 48 | Sigmoide (empurra para os extremos; saída de classificação binária) |
| 49 | ReLU, max(0, x); padrão das camadas ocultas |
| 50 | Softmax (multiclasse, probabilidades) |
| 51 | Como escolher a ativação; ReLU só nas camadas ocultas |
| 52 | Tabela: tipo de problema × função de custo × ativação de saída (binária, multiclasse, multilabel, regressão, regressão com outliers) |

## 2. Matriz slide × vídeo

Os ids são os itens propostos (`a10-vN`). **Opc.** = vídeo opcional. O vídeo de cada id está na seção 3.

| Slides | Cobertura | Vídeos e trechos |
| :-- | :-: | :-- |
| 3 | B | a10-v6 (00:43–04:00) |
| 4 | B | a10-v7 (02:35–04:50); a10-v11 (03:00–04:20, analogia) |
| 5 | P | a10-v6 (01:13–02:00, aprender por experiência); a10-v8 (12:53–15:15, a rede muda os pesos). Nenhum vídeo usa a palavra "plasticidade": fica para a leitura |
| 6 | B | a10-v8 (00:00–10:00); a10-v6 (03:02–04:00) |
| 7 | P | a10-v7 (02:00–02:35, "criado em 1943"). Os nomes McCulloch e Pitts: leitura |
| 8 | B | a10-v7 (00:00–01:50); a10-v8 (03:00–06:00); a10-v11 (00:00–03:00) |
| 9 | P | a10-v11 (conta com função degrau e limiar, 00:00–05:10); a10-v7. **"O MCP não aprende": L**, leitura cobre |
| 10 | P | a10-v1 (01:21–05:55). Rosenblatt, 1958 e a convergência para problemas linearmente separáveis: **L parcial** (a10-v11 mostra a separabilidade em 15:10–17:50) |
| 11 | B | a10-v10 (03:57–07:00); a10-v1 (07:35–09:55); a10-v8 (12:53–15:15) |
| 12 | B | a10-v10 (06:00–15:30) **X** (usa μ e δ; inicia pesos em zero); a10-v11 (11:00–13:00) |
| 13 a 14, 16, 17 | B | a10-v11 (05:10–15:00): E lógico, previsão, erro e atualização. Os slides são imagens; o exemplo exato deles não está no texto extraído |
| 15 | X | a10-v10 e a10-v11 inicializam em zero (slide: aleatório em [0; 1]); taxa 0,1 contra 0,3 do slide |
| 18 | B | a10-v12 (01:00–03:00); a10-v11 (15:10–17:50); a10-v13 (00:00–04:50, Opc.) |
| 19 e 20 | B | a10-v12 (03:00–06:00); slide 20 só de forma implícita em 04:30–06:00 |
| 21 | B | a10-v14 (06:30–09:00); a10-v15 (00:00–04:00, Opc.) |
| 22 | B | a10-v14 (06:30–09:00: delta oculto vem de pesos × deltas seguintes); a10-v15 (04:00–08:30, Opc., **X** leve); a10-v2 (03:00–05:00, Opc.) |
| 23 | B | a10-v14 (01:30–05:30); a10-v12 (06:00–09:53) |
| 24 | P | a10-v14 (09:00–11:40, repetir por época e critério de parada); a10-v2 (05:00–09:30 e 01:00–01:35, Opc.). Os nomes "regra da cadeia", "gradiente" e "convergência" por extenso: a10-v2 e a10-v15 (Opc.) |
| 25 | B | a10-v16 (00:00–06:45); a10-v17 (00:58–02:00, MSE) |
| 26 a 28 | B | a10-v17 (03:30–06:20); a10-v18 (00:00–03:30, Opc.) |
| 29 | B | a10-v17 (04:15–06:20, inclinação da reta tangente) |
| 30 | B | a10-v17 (05:00–06:20, sinal da inclinação); a10-v18 (00:00–01:10, gradiente como seta) |
| 31 a 33 | B | a10-v17 (09:00–12:00: regra "peso novo = peso antigo − taxa × inclinação"). O critério de parar com custo perto de zero (slide 33): P, o vídeo fala em número de épocas |
| 34 | B | a10-v19 (01:30–05:50); a10-v3 (04:20–12:00, Opc.) |
| 35 | P | Camadas e neurônios: a10-v8 (10:00–12:00). Taxa: a10-v17. Função de ativação: a10-v4. Otimizador: a10-v19 e a10-v18. Conceito de hiperparâmetro: a10-v20 (Opc.). Nenhum vídeo traz a lista inteira do slide, a leitura junta |
| 36 | B | SGD: a10-v19. Adam (taxa por peso): a10-v21 (Opc., inglês); a10-v18 (11:05–12:50, só cita) |
| 37 e 38 | B | a10-v5 (00:00–04:25) |
| 39 | B | a10-v5 (07:35–13:45) **X**: o vídeo liga L2 a "laço" |
| 40 | B | a10-v5 (04:50–07:35, Dropout; L1/L2 em 07:35–13:45) |
| 41 | B | a10-v17 (07:00–09:00); a10-v22 (00:00–08:10, Opc.). Os valores 0.001 a 0.3: L |
| 42 | P | a10-v23 (03:30–05:20, suave e diferenciável). A frase "pequena mudança no peso, pequena mudança na saída": leitura |
| 43 | P | a10-v23 (05:20–07:30, degrau não é diferenciável) |
| 44 | B | a10-v4 (02:00–03:00, a função decide se o neurônio dispara) |
| 45 | B | a10-v4 (03:00–03:50) **X** (frase com "linear" e "não linear" trocados em 03:35); a10-v13 (00:55–03:00, Opc.) |
| 46 | P | a10-v23 (05:20–07:30, o degrau não ajuda no gradiente); a10-v11 (degrau em ação, limiar 1) **X** |
| 47 | L | Só a reta y = a·x + b em a10-v4 (00:00–01:00). A função linear como ativação e seu uso na saída de regressão: leitura |
| 48 | B | a10-v4 (05:20–07:30); a10-v23 (01:10–03:30) |
| 49 | B | a10-v4 (08:17–12:15) |
| 50 | B | a10-v4 (07:30–08:15); a10-v26 (03:00–04:50, Opc., inglês); a10-v25 (02:11–03:35, Opc.) |
| 51 | P | a10-v4 (ReLU rápida, sigmoide para probabilidades); a10-v26 (03:45, Softmax só na saída, Opc.). Que a ReLU é padrão das ocultas e só deve ser usada nelas: leitura |
| 52 | P | Binária: a10-v24 (00:00–00:58). Multiclasse: a10-v25 e a10-v26 (Opc.). **L:** multilabel, regressão com MSE e regressão com outliers (MAE), e a tabela inteira |

Slides sem vídeo (a leitura cobre): 9 (só a parte "MCP não aprende"), 47, 52 (linhas multilabel e regressão), e as partes de nome/data citadas acima (5, 7, 10, 41). Os demais têm pelo menos um vídeo que cobre.

## 3. Fichas por vídeo

A ordem segue os slides. `Item` é o id proposto em `proposta_b4_aula10.json`. Tudo foi lido na transcrição inteira.

### s-Ue8SdQy3I — Hashtag Programação — O que são Redes Neurais e Deep Learning (13:55) · item a10-v6
- **Cobre:** 00:43–01:57 cérebro como máquina de aprender (criança e a vela: aprender por experiência); 02:04–03:00 neurônio simples (passa ou não passa informação), poder pela quantidade e paralelismo; 03:02–04:00 rede artificial com camadas ocultas e deep learning; 07:45–11:55 peso, viés e ativação com o exemplo da banana.
- **Não cobre:** dendrito, corpo, axônio, plasticidade; MCP; Perceptron.
- **Divergências:** diz que a ativação serve para "adequar os dados entre 0 e 1" (08:55 a 09:10); só vale para algumas funções.
- **Nível:** iniciante total, sem fórmulas. Português claro; pedido de curtida no início.
- **Veredito:** aprovar só 00:43–04:00 (slides 3, 5 e 6).

### wNBJFswcy00 — Hemerson Pistori — Neurônios Artificiais e Biológicos (19:56) · item a10-v7
- **Cobre:** 00:00–01:50 neurônio artificial (entradas × pesos, soma, ativação); 02:00–02:35 "criado em 1943"; 02:35–04:50 neurônio biológico (dendritos, soma/integração, limiar de disparo, axônio e terminais). De 04:57 em diante: neurociência real (sinapses químicas, neurotransmissores, células da glia), para dizer que o modelo é muito simplificado.
- **Não cobre:** nome McCulloch e Pitts; "MCP não aprende"; plasticidade.
- **Veredito:** aprovar só 00:00–04:50 (slides 4, 7, 8 e 9). O resto não está nos slides.

### TbGUV3nR2bI — Hemerson Pistori — Aula IA 01: Parâmetros, Pesos, Viés e Arquitetura (15:29) · item a10-v8
- **Cobre:** 00:00–03:00 rede como neurônios simples que trocam números; 03:00–06:00 peso como número que multiplica o sinal na conexão (equivalente à sinapse); 06:00–10:00 viés; 10:00–12:00 parâmetros, arquitetura, camadas ocultas, rede profunda; 12:53–15:15 a rede aprende mexendo nos parâmetros.
- **Não cobre:** função de ativação, regra de correção do erro.
- **Nível:** iniciante total; muito didático. Português.
- **Veredito:** aprovar 00:00–12:00 e 12:53–15:15 (slides 6, 8, 11 e parte do 35).

### 8lKamMoQKQ0 — Fernando dos Santos — Redes Neurais: Perceptron (11:02) · item a10-v1 (mantido)
- **Cobre:** 00:00–01:05 revisão do neurônio; 01:21–03:00 Perceptron como rede mais simples, para classificação; 03:00–04:20 camada de entrada "sensorial" que só replica; 04:27–05:50 camada de saída com neurônios que calculam; 07:35–09:55 conhecimento nos pesos, aprender é achar pesos; 09:57 anuncia o aprendizado delta.
- **Não cobre:** a regra de correção do erro (o item anterior dizia que cobria), Rosenblatt, 1958, convergência, MCP.
- **Veredito:** aprovar só 01:21–05:55 e 07:35–10:00 (slides 10 e 11).

### PXSHPkMXD8o — Fernando dos Santos — Redes Neurais: Perceptron e o Aprendizado Delta (16:21) · item a10-v10 (novo)
- **Cobre:** 03:57–05:00 conhecimento nos pesos; 05:00–06:00 aprendizado supervisionado; 06:00–07:00 aprendizado delta; 07:00–09:15 iterativo, critério de parada, época; 09:15–10:50 erro = desejado − obtido e taxa de aprendizado; 10:50–15:30 cinco passos e fórmula de atualização; 15:30–16:20 critérios de parada.
- **Divergências:** pesos em zero (slide: aleatório em [0; 1]); μ e δ no lugar de n e e; "década de 60" no lugar de 1958; saída "0 ou −1".
- **Veredito:** aprovar 03:57–16:20 (slides 10, 11, 12 e 15). Melhor vídeo para a regra do slide 12.

### 0chlwnUKoHA — IA Expert Academy — Teoria sobre Redes Neurais Artificiais: cálculos passo a passo Perceptron (17:52) · item a10-v11 (novo)
- **Cobre:** 00:00–03:00 conta do neurônio com função degrau; 03:00–04:20 analogia com o neurônio biológico; 05:10–15:00 treino do E lógico (previsão, erro, atualização w = w + taxa × entrada × erro); 15:10–17:50 linearmente separável (E, OU) e XOR.
- **Divergências:** degrau com limiar 1 (slide 46: x ≥ 0); pesos iniciais zero; taxa 0,1 (slide: 0,3); os pesos 0,5 finais foram escolhidos, não aprendidos.
- **Veredito:** aprovar inteiro. É o mais parecido com o exemplo dos slides 13 a 17.

### yV6KKoKfo3g — Fernando dos Santos — Redes Neurais: Conceito de MultiLayer Perceptron (MLP) e a propagação de entradas (9:54) · item a10-v12 (novo)
- **Cobre:** 00:00–01:00 MLP = Perceptron + camada oculta; 01:00–03:00 a camada oculta torna separável o que não era; 03:00–06:00 topologia; 06:00–09:53 propagação para frente com soma, φ e viés.
- **Não cobre:** treinamento; o nome XOR.
- **Veredito:** aprovar inteiro (slides 18, 19, 20 e 23).

### 1OkCbD5cs7o — Frame Zero — Solving the XOR Problem: Perceptrons and Non-Linearity (10:32, inglês) · item a10-v13 (novo, opcional)
- **Cobre:** 00:00–00:55 XOR e a reta única; 00:55–03:00 camadas lineares empilhadas colapsam em uma; 03:00–04:50 a ativação não linear (ReLU) resolve; depois do 05:00 mostra a dobra do espaço e o XOR com duas ReLU.
- **Veredito:** aprovar só 00:00–04:50, como opcional, porque explica o slide 45 melhor que o vídeo em português. Aviso de idioma em `note`.

### IjdJNPpJ8nE — Fernando dos Santos — Redes Neurais: Visão geral do treinamento de MLP com o Backpropagation (11:49) · item a10-v14 (novo)
- **Cobre:** 00:00–01:20 backpropagation como generalização do aprendizado delta; 03:00–05:30 erro e delta na saída (erro × derivada da ativação); 06:30–09:00 camadas ocultas sem saída desejada: delta vem dos deltas seguintes ponderados pelos pesos (a ideia do slide 22); 09:00–11:40 época e critério de parada.
- **Divergências:** usa "delta" no lugar de "gradiente"; não usa "regra da cadeia" nem "convergência".
- **Veredito:** aprovar 00:00–11:40 (slides 21 a 24). É o melhor vídeo em português para esses slides.

### DG9jPLfWhoA — Hemerson Pistori — Aula IA 10: Backpropagation (Retropropagação) (12:55) · item a10-v15 (novo, opcional)
- **Cobre:** feedforward, erro de cada saída, derivada parcial, regra da cadeia, ajuste proporcional à influência, soma dos pedidos nas camadas anteriores, propagação para trás.
- **Divergência leve:** o ajuste do peso depende da saída do neurônio de origem; o slide 22 fala do valor do peso. As duas coisas valem na conta.
- **Veredito:** aprovar como complemento visual opcional.

### L3lbrdCTK9w — Sandeco — Backpropagation: Entenda de uma vez por todas! (10:28) · item a10-v2 (mantido, agora opcional)
- **Cobre:** 00:26–01:35 duas fases e ciclo até o erro mínimo; 01:35–03:00 funções aninhadas; 03:00–05:00 engrenagens: cada peso tem parte da culpa; 05:00–09:30 derivação para W5 com a regra da cadeia (conta); 09:10 aviso de que a derivada da ativação pode ser zero.
- **Não cobre:** atualização das camadas ocultas (W1); convergência.
- **Veredito:** aprovar 00:26–05:00 como opcional; 05:00–09:30 só para quem quiser a conta.

### Odm-cm-nxVo — Hemerson Pistori — Aula IA 03: Função de Perda (12:41) · item a10-v16 (novo)
- **Cobre:** 00:00–06:45 função de perda como número que mede o erro, exemplo com soma das diferenças, perda × peso, aprender = reduzir a perda, erro aceitável.
- **Divergência:** o exemplo não usa MSE; só diz que poderia usar o quadrado.
- **Veredito:** aprovar só 00:00–06:45 (slide 25). Depois do 07:00 é paisagem 3D da perda de redes reais.

### vH4eSfGkJhQ — Machine Learning para humanos — Redes neurais artificiais #13: Backpropagation e descida do gradiente (12:13) · item a10-v17 (novo)
- **Cobre:** 00:58–02:00 exemplo e MSE; 02:00–04:15 perda × peso em parábola; 04:15–06:20 inclinação da reta tangente e sentido do movimento; 07:00–09:00 tamanho do passo e taxa de aprendizagem; 10:00–11:50 regra "peso novo = peso antigo − taxa × inclinação".
- **Divergência:** título fala em backpropagation, mas só trata da descida do gradiente; aos 01:09 troca "dependente" por "independente".
- **Veredito:** aprovar 00:58–12:05 (slides 25 a 33 e 41). Melhor vídeo para o gradiente.

### OzNWEeIVJvI — Hemerson Pistori — Aula IA 05: Otimizadores, Descida de Gradiente, Mínimos Locais (14:14) · item a10-v18 (novo, opcional)
- **Cobre:** gradiente como seta, oposto para descer, atualização por subtração, taxa α, otimizadores (SGD, Adam) citados.
- **Extra (fora dos slides):** mínimos locais, platôs, saltos para escapar.
- **Veredito:** aprovar 00:00–03:10, 06:25–09:10 e 11:05–12:45 como opcional.

### qX-5Yng2Qac — Hemerson Pistori — Aula IA 06: SGD, Tamanho de Minilotes, Descida de Gradiente Estocástica (11:27) · item a10-v19 (novo)
- **Cobre:** 01:30–05:50 SGD com mini-lotes (aproximação do gradiente, tamanho do lote, 1 exemplo = SGD puro); 05:50–07:10 memória da GPU; 07:10–08:20 passos dentro de uma época; lotes de 4, 8 até 64.
- **Veredito:** aprovar 00:00–09:15 (slides 34 e 36). Melhor vídeo para o mini-lote.

### snXZg11IJ-8 — Didática Tech — Gradiente Descendente Estocástico (14:03) · item a10-v3 (mantido, agora opcional)
- **Cobre:** custo de usar todas as amostras, SGD com parte dos dados, "andar do bêbado", compromisso do tamanho do lote.
- **Não cobre:** taxa de aprendizado, Adam (o item antigo dizia cobrir).
- **Veredito:** aprovar 01:00–13:30 como opcional; boa intuição, mas a10-v19 cobre o mesmo em menos tempo.

### OuDcVDJZsYo — Hemerson Pistori — Aula IA 07: Momento, Hiperparâmetros, Ponto de Sela (13:15) · item a10-v20 (novo, opcional)
- **Cobre:** 04:56–05:50 hiperparâmetro × parâmetro (taxa, lote, momento); 05:50–06:58 conjunto de validação para escolher hiperparâmetros.
- **Veredito:** aprovar só 04:56–06:58. O resto (momento, ponto de sela) está fora dos slides.

### nb09yQZ-iFQ — DataMListic — The Adam Optimizer is Just Momentum + RMSProp (4:19, inglês) · item a10-v21 (novo, opcional)
- **Cobre:** zigue-zague da descida simples; momentum; RMSProp (taxa própria por direção); Adam junta as duas, com correção de viés.
- **Veredito:** aprovar só 00:00–03:00, opcional. Não achei vídeo em português claro sobre o Adam.

### rujn32cMeO8 — Hemerson Pistori — Aula IA 09: Regularização, Early Stopping, Dropout, Weight Decay L1 e L2 (13:51) · item a10-v5 (mantido)
- **Cobre:** 00:00–04:25 parada antecipada (validação, paciência, tolerância, melhor conjunto de pesos); 04:50–07:35 Dropout; 07:35–10:05 L2; 10:05–11:10 L1; 11:10–13:45 esparsidade L1 × L2.
- **Divergência:** aos 10:30 liga L2 a "laço" (Lasso); o slide 40 diz L2 = Ridge e L1 = Lasso. Explica L1/L2 como penalidade na perda, enquanto o slide 39 fala do efeito no ajuste do peso.
- **Veredito:** aprovar os trechos indicados (os tempos do item antigo estavam certos; o aviso sobre Lasso/Ridge é novo).

### 9g6CjmkiwRw — Machine Learning para humanos — Redes neurais artificiais #14: Backpropagation e learning rate (13:25) · item a10-v22 (novo, opcional)
- **Cobre:** efeito da taxa em animações: pequena, média, grande, divergência; depois do 08:15, mínimos locais e taxa que diminui.
- **Veredito:** aprovar só 00:00–08:10, opcional (slide 41).

### G-lFSSY8qhE — Hemerson Pistori — Aula IA 08: Funções de Ativação, Não-Linearidades, ReLU, Softmax (13:59) · item a10-v4 (mantido, clips corrigidos)
- **Cobre:** 00:00–03:50 neurônio linear → ativação não linear; 04:00–04:50 tangente hiperbólica (extra); 05:20–07:30 logística/sigmoide (0 a 1, probabilidade); 07:30–08:15 Softmax; 08:17–12:15 ReLU, Leaky ReLU, derivadas; 12:15–13:55 derivada da sigmoide (extra).
- **Divergências:** a fala de 03:35 está com "linear" e "não linear" trocados; não trata de degrau nem de linear (slides 46 e 47).
- **Veredito:** aprovar 00:00–03:50, 04:45–08:17 e 08:17–12:15.

### DlBhJdHQElI — Didática Tech — Aprenda a função Sigmóide (8:30) · item a10-v23 (novo)
- **Cobre:** 00:00–01:10 motivação; 01:10–03:30 fórmula e gráfico em S, corte em 0,5; 03:30–05:20 combinação linear de variáveis; 05:20–07:30 por que não o degrau (não diferenciável).
- **Veredito:** aprovar 00:00–07:30 (slides 43, 46 e 48).

### GdNmDQRdL2o — Sandeco — Entenda a Entropia Cruzada de Uma Vez Por Todas (4:08) · item a10-v24 (novo)
- **Cobre:** 00:00–00:58 classificação binária usa entropia cruzada binária, não o erro quadrático; depois, exemplos numéricos.
- **Veredito:** aprovar só 00:00–00:58 (slide 52, linha da classificação binária).

### qAnGJNA7HKA — Byte Criativo — Função de Perda (Loss Function) (6:06) · item a10-v25 (novo, opcional)
- **Cobre:** 02:11–03:35 multiclasse com entropia cruzada categórica e Softmax (soma 100%). Divulgação, com exemplo de LLM.
- **Veredito:** aprovar só 02:11–03:35, opcional.

### LoGPU2oXp8g — Professor Bryce — Better Activation & Loss for Classification: Softmax & Categorical Crossentropy (14:50, inglês) · item a10-v26 (novo, opcional)
- **Cobre:** 00:00–05:40 por que sigmoides na saída multiclasse atrapalham, Softmax, entropia cruzada categórica; 06:00–14:30 derivação do gradiente (fora do escopo).
- **Veredito:** aprovar só 00:00–05:40, opcional.

## 4. Vídeos avaliados e descartados

Todos foram lidos na íntegra; o motivo é específico.

| ID | Vídeo | Motivo |
| :-- | :-- | :-- |
| xGShRYE55uM | Machine Learning para humanos — Perceptron Parte I (11:07) | Trata o neurônio como regressão linear (Celsius → Fahrenheit, w e b) com código PyTorch. Sem classificação e sem a regra de correção do erro do slide 12. Útil só como introdução de peso e viés como reta, já coberta por a10-v8. |
| aZJww0sB7Dg | Machine Learning para humanos — Perceptron Parte II (11:54) | Mostra separação linear (00:55–02:50), soma ponderada com limiar e um exemplo de aprovação. Bom, mas repete o que a10-v11 e a10-v12 fazem com mais aderência ao exemplo do slide. |
| gppAMo4mNZ0 | Sandeco — Dropout (5:34) | Explicação correta de Dropout, mas já coberta por a10-v5 (04:50–07:35); evita um vídeo repetido. |
| iMiM1_1mJCQ | Dr. Data Science — Why Do We Need Hidden Layers? XOR (11:44, inglês) | XOR calculado à mão com pesos dados, em inglês; o usuário não terá cálculo na prova, e a ideia está em a10-v12 e a10-v13. |
| r2TvNmAxiCU | Mısra Turp — All Hyperparameters of a Neural Network (7:27, inglês) | Resumo geral do ciclo de treino que adia os detalhes para outras aulas; não cobre a lista do slide 35 melhor que a10-v8, a10-v20 e a10-v4. |
| YhatZb5SzE0 | Mısra Turp — How Many Hidden Layers and Neurons (4:35, inglês) | Dá regras práticas (1 a 2 camadas, 100 a 300 neurônios), que não estão nos slides; o slide 35 só lista os hiperparâmetros. |
| x_vMFs9d6H4 | Daniel Hasan Dalip — Adam e RMSProp (8:52) | Explica média móvel exponencial e termina com Adam em um parágrafo confuso; a transcrição quebrada não permite confiar. Usei o vídeo em inglês nb09yQZ-iFQ. |
| MWZakqZDgfQ | ByteQuest — ADAM Explained Visually (2:23, inglês) | Revisão de fórmulas que pressupõe os vídeos anteriores da série; menos claro que nb09yQZ-iFQ. |
| CqOfi41LfDw | StatQuest — Neural Networks Part 1 (18:54, inglês) | Excelente (a rede ajusta uma curva somando ativações com pesos e vieses), mas é longo, usa Softplus e duplica o que a10-v12 e a10-v13 já mostram em português ou em menos tempo. Recomendo só a quem quiser a segunda camada de intuição. |
| IN2XmBhILt4 | StatQuest — Neural Networks Part 2: Backpropagation (17:34, inglês) | Rigoroso, mas só atualiza o último viés; backpropagation já está em a10-v14, a10-v15 e a10-v2 em português. |
| 68BZ5f7P94E | StatQuest — Neural Networks Part 3: ReLU In Action (8:58, inglês) | ReLU em ação com bom detalhe de derivada no ponto de dobra (07:30), mas a10-v4 cobre a ReLU em português. |
| xkOhhoC007s | Monte Carlo Digital — Introdução ao neurônio de McCulloch–Pitts (6:40) | Dá o nome MCP, a soma Σ x·w e uma lista de ativações (incluindo identidade e degrau, 03:00–04:20), mas não cita 1943, nem que o MCP não aprende; o tratamento é superficial e já coberto por a10-v7 e a10-v11. |
| osa3zIEJjgw | Victor Lavrenko — Neurônio de McCulloch e Pitts (3:29, inglês) | Boa analogia neurônio ↔ modelo, mas cita a sigmoide como "squashing function" e não o degrau do MCP; em inglês e redundante com a10-v7. |

Outras transcrições órfãs em `transcripts/` (B8NysmnG2Ys, hldHO4KwaL8, oz_rZ92Tmls) não têm relação com a Aula 10; as de SVM (Q7vT0--5VII, Qc5IyLW_hns, Toet3EiSFcM, Y-WFZd9_gtE, _VDIhWvaOA4, efR1C6CvhmE e outras) pertencem à Aula 11 e não foram avaliadas aqui.

## 5. Lacunas que a leitura precisa cobrir

- Slide 5: o nome plasticidade e a ligação com o ajuste dos pesos.
- Slide 7 e 9: nomes McCulloch e Pitts, 1943 e a frase "o MCP não aprende" (só se disse que o modelo é de 1943).
- Slide 10: Rosenblatt, 1958 e o resultado de convergência para problemas linearmente separáveis.
- Slide 15: pesos aleatórios em [0; 1] e taxa 0,3 (os vídeos usam zero e 0,1).
- Slide 24: os nomes "regra da cadeia", "gradiente" e "convergência" nas duas fases (existem em a10-v2 e a10-v15, opcionais).
- Slide 35: lista completa de hiperparâmetros num só lugar.
- Slide 41: valores típicos da taxa (0.001 a 0.3).
- Slides 46, 47 e 51: degrau com limiar 0, função linear na saída de regressão, e a regra "ReLU só nas camadas ocultas".
- Slide 52: linhas multilabel, regressão (MSE) e regressão com outliers (MAE), e a tabela inteira.


## Redução por sobreposição (agente principal, 11/10/2026)

Pedido do usuário: se vários vídeos se sobrepõem, não é preciso manter todos, MAS sem trocar um vídeo didático por outro mais técnico (o usuário é engenheiro de software sem base em ciência de dados). Critério: mais didático para esse nível, com mais analogias e que cubra mais slides. Todos os vídeos abaixo foram lidos na auditoria e aprovados; saíram do bloco só por sobreposição (regra do usuário: só sai o que for duplicado sem valor a mais; se dois vídeos se completam, ficam os dois) com um mais didático ou mais completo. Aula 10: ficaram a10-v6, v7, v8, v1, v11, v12, v14, v16, v17, v3, v5, v4, v23, v24, v25 e, como opcionais que se completam com os outros, v2 (analogia das engrenagens) e v22 (animações da taxa de aprendizado). As transcrições continuam em `estudo/conteudo/transcripts/`; para trazer um de volta, basta reinseri-lo no `block.json`.

- a10-v10 (Fernando dos Santos: Redes Neurais: Perceptron e o Aprendizado Delta)
- a10-v13 (Frame Zero: Solving the XOR Problem: Perceptrons and Non-Linearity)
- a10-v15 (Hemerson Pistori: Aula IA - 10 - Backpropagation (Retropropagação))
- a10-v18 (Hemerson Pistori: Aula IA - 05 - Otimizadores, Descida de Gradiente, Mínimos L)
- a10-v19 (Hemerson Pistori: Aula IA - 06 - SGD, Tamanho de Minilotes (Batch Size), Desci)
- a10-v20 (Hemerson Pistori: Aula IA - 07 - Momento, Hiperparâmetros, Ponto de Sela (Sadd)
- a10-v21 (DataMListic: The Adam Optimizer is Just Momentum + RMSProp)
- a10-v26 (Professor Bryce: Better Activation & Loss for Classification: Softmax & Categ)
