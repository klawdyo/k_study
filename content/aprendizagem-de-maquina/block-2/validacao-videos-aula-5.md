# Validação dos vídeos pela transcrição — Aula 5 (Regressão Linear)

Método: refiz a curadoria da Aula 5. Li **inteiras** as transcrições locais (Whisper small, `study transcribe`) dos 5 vídeos anteriores e de 10 candidatos novos, e conferi cada tempo `mm:ss` contra a duração real (campo `duration` do JSON). Os tempos têm precisão de cerca de ±5 s. As transcrições automáticas têm erros ("dinéar" = linear, "SKT/SKRS" = SQT/SQR, "rede" = ridge, "baia" = viés); quando uma ficou ilegível, está dito abaixo. Fonte do critério de cobertura: os 55 slides em `estudo/_fontes_extraidas/Aulas__Aula_5_-_Regressao_Linear.pptx.txt`. A versão anterior desta ficha tinha tempos além da duração e conteúdos que não existiam nos vídeos; esta substitui a anterior. Quando aponto um erro do vídeo que depende de conhecimento meu (fora do vídeo), está marcado "(conhecimento externo)".

## 1. Vídeos aprovados, na ordem dos slides

| id | Vídeo (canal) | Duração | Trechos aprovados | Slides | Observação |
| :-- | :-- | :-: | :-- | :-- | :-- |
| a5-v1 | `88olil97P_Q` Codifike, Explicando como funciona Regressão Linear | 5:48 | 01:40–03:02; 03:13–05:00 | 4–6, 10–12, 20 | Corrigido: 2 erros do vídeo avisados |
| a5-v5 | `ayAxTRN4aVg` Prof. Murakami, Coeficiente de correlação linear EP 1 | 8:38 | 00:46–03:55 | 7–8 | Corrigido: só a parte conceitual |
| a5-v2 | `jSaJjshIAUw` Zurubabel, Função de Custo | 5:33 | 00:25–05:00 | 10–11 | Mantido |
| a5-v6 | `TLlzToeIpGc` Statmeup, Regressão Linear Múltipla | 10:21 | 00:26–03:07; 06:36–06:48; 07:58–08:56; 09:22–10:20 | 13, 15, 19, 52 | **Novo** (Excel; pular testes F e valor-p) |
| a5-v7 | `ejrEX9xrKlw` Born to be AI, Descida do Gradiente: Intuição | 6:06 | 00:00–06:00 | 24, 28, 35, 39 | **Novo** |
| a5-v8 | `szqcb5qQbWQ` Machine Learning para humanos, Descida do gradiente e derivada | 7:23 | 00:50–05:46; 06:20–06:47 | 26–27, 30, 35 | **Novo** (contexto de redes neurais) |
| a5-v9 | `8NloB9J2WTc` Apoena Stack, Gradiente Descendente e Regressão Linear | 23:55 | 00:39–06:32; 11:05–17:03; 17:42–20:00; 21:21–23:05 | 28–36, 39–40, 44 | **Novo**, o melhor para GD; 1 erro avisado |
| a5-v10 | `4M7PU-juavg` pythonando, Regressão linear: Explicando gradiente | 3:28 | 00:00–02:58 | 40–43 | **Novo**, curto |
| a5-v11 | `vEAtjqMLrUQ` Nerd dos Dados, Learning Rate | 16:48 | 04:47–09:50 | 39–40 | **Novo**, `optional` |
| a5-v12 | `eYnBR4EVdX4` Saulo Reis, Regularização II: Regressão Ridge | 10:46 | 02:00–08:50 | 45–46 | **Novo**, substitui o StatQuest |
| a5-v13 | `LuttGjfSQCc` ProfDanilo_DS, Regressão de Lasso, Ridge e Elastic Net | 6:23 | 01:33–05:12 | 45–46 | **Novo**, transcrição ruim, ressalva |
| a5-v14 | `QXy5GTb7pwE` Abel Siqueira, Regularização Ridge/L2, LASSO/L1 e Elastic Net | 21:06 | 07:13–07:57; 10:00–11:50; 12:41–13:36; 15:30–17:30; 17:38–19:30 | 45–46 | **Novo**, `optional`, mais matemático |
| a5-v3 | `wDJjmH3JFqc` Didática Tech, Coeficiente de determinação R2 | 11:52 | 00:45–11:28 | 50–51 | OK; clip estendido (antes cortava 1 min do melhor trecho) |
| a5-v15 | `qoOHUCVG0Gs` Didática Tech, Coeficiente R2 ajustado | 8:22 | 00:14–02:52; 07:19–08:01 | 52 | **Novo** |
| a5-v16 | `_pJX2SFoFtY` Didática Tech, Erro médio absoluto x Erro médio quadrático | 9:58 | 00:03–09:38 | 53–54 | **Novo** |

Tempo de vídeo nos trechos aprovados: cerca de 85 min, dos quais 12 min são `optional` (a5-v11 e a5-v14).

## 2. Fichas por vídeo

### a5-v1 — Codifike, Explicando como funciona Regressão Linear (5:48) · CORRIGIDO
- **Cobre:** 01:44–02:52 resíduo como diferença para a reta, elevar ao quadrado "porque pode ser negativo", soma dos quadrados dos resíduos (a reta usada é a horizontal da média); 03:13–03:43 equação da reta, Y dependente, X independente, "A é o ângulo", B é o valor de Y quando X = 0; 03:43–04:57 "método dos mínimos quadrados", curva do erro e derivada ("a derivada de cada ponto nos diz a inclinação").
- **Erros do vídeo (agora em `warnings`):** (1) 01:02–01:07 "o R² ... com isso saberemos a inclinação da reta": errado, o R² mede a qualidade do ajuste (conhecimento externo). (2) 04:36–04:47 "a melhor inclinação é aquela onde o mínimo quadrado é zero": errado, é o mínimo da SQR, só é zero se a reta passa por todos os pontos (conhecimento externo). Notação Y = aX + b contra Y = α + βx dos slides.
- **Correção da ficha anterior:** a ordem estava invertida (a equação da reta está em 03:13, não em 00:45) e o clip terminava em 03:18, cortando a parte do mínimo. Slides 12 (estratégias) e 20 (OLS × GD, inversão de matriz) só têm a ideia do mínimo por derivada.
- **Nível:** iniciante; superficial. **Veredito:** aprovar só 01:40–03:02 e 03:13–05:00, lendo os avisos.

### a5-v5 — Prof. Murakami, Coeficiente de correlação linear EP 1 (8:38; antes 6:26) · CORRIGIDO
- **Cobre:** 00:46–01:32 r entre −1 e +1, r = +1 correlação linear perfeita positiva; 01:32–02:19 r = −1 perfeita negativa, r = 0 pontos dispersos; 02:19–03:55 força (perto de ±1 forte, afastado fraca). Slides **7 e 8**, não 23 a 28 como estava.
- **Não cobre:** que Pearson mede só relação linear, multicolinearidade (slide 8), causalidade, exemplo felicidade × expectativa de vida (slide 9). A ficha anterior inventava "05:00–06:20 não causalidade": a palavra "causalidade" nunca aparece.
- **Depois de 03:55 (até 08:38):** cálculo manual de r com colunas x², y², xy: fora dos slides e contra a regra "sem cálculo".
- **Veredito:** aprovar só 00:46–03:55.

### a5-v2 — Zurubabel, Função de Custo (5:33) · OK
- **Cobre:** 00:25–01:07 função de custo = número que diz quão bom é o modelo; 01:07–04:00 fórmula J com soma dos erros ao quadrado dividida por 2m; 04:10–04:40 por que elevar ao quadrado (5−1 e 1−5 dão 16).
- **Avisos:** θ0/θ1 e 1/(2m) de Andrew Ng; não diz SQR/MSE; termina antes de minimizar (slide 12); voz rouca e trechos refeitos.
- **Veredito:** aprovar 00:25–05:00. Didática mediana, serve para o conceito.

### a5-v6 — Statmeup, Regressão Linear Múltipla – Introdução (10:21) · NOVO
- **Cobre:** 00:26–01:16 regressão simples (tamanho → preço) e por que usar várias variáveis; 02:46–03:07 equação ŷ = b₀ + b₁x₁ + b₂x₂; 06:36–06:48 R² ajustado serve para comparar modelos com números diferentes de variáveis; 07:58–08:56 coeficientes "mantida a idade constante", "mantido o tamanho constante"; 09:22–10:20 gráfico 3D com plano (duas variáveis).
- **Não cobre:** a palavra hiperplano, padronização dos betas (slide 19), multicolinearidade. Entre 02:40 e 07:10 é Excel, teste F e valores-p: fora dos slides.
- **Veredito:** aprovar só os trechos acima. Único vídeo de regressão múltipla em português aceitável dos encontrados.

### a5-v7 — Born to be AI, Descida do Gradiente: Intuição (6:06) · NOVO
- **Cobre:** 00:00–01:35 a função de erro como altura sobre os parâmetros, não confundir com a reta; 01:38–03:07 o gradiente aponta para onde o erro mais cresce, anda-se no sentido contrário; 04:06–06:00 passos pequenos, risco de passar do mínimo, imagem da bolinha que desce.
- **Avisos:** começa no meio de uma aula; notação θ1, θ2; não mostra a fórmula de atualização.
- **Veredito:** aprovar o vídeo inteiro. Melhor intuição geométrica do gradiente descendente que achei em português.

### a5-v8 — Machine Learning para humanos, Redes neurais #15: Descida do gradiente e derivada (7:23) · NOVO
- **Cobre:** 00:50–01:50 peso novo = peso antigo − taxa de aprendizado × inclinação; 01:49–05:46 inclinação de reta e de parábola, encolher o intervalo até virar derivada = inclinação da tangente; 06:20–06:47 fórmula com a derivada do erro.
- **Avisos:** contexto de redes neurais ("peso", η); uma variável só.
- **Veredito:** aprovar 00:50–05:46 e 06:20–06:47. Cobre bem os slides 26 e 27 (derivada).

### a5-v9 — Apoena Stack, Gradiente Descendente e Regressão Linear (23:55) · NOVO, principal de GD
- **Cobre:** 00:39–01:35 fórmula de atualização; 02:50–05:34 sinal da derivada decide o sentido do passo, derivada zero no mínimo; 05:46–06:32 função convexa; 11:05–14:20 taxa pequena (lenta) e alta (oscila, não converge); 14:25–16:25 passos diminuem sozinhos porque a inclinação tende a zero (slide 44); 16:29–17:03 valores típicos 0,01; 0,001; 0,03 (slide 40); 17:42–20:00 β0 e β1 atualizados juntos; 21:21–23:05 animação.
- **Avisos:** aos 13:47 diz que divergir é "demorar para chegar" (errado; conhecimento externo); a derivação de 06:32 a 11:05 é cálculo, pular; slide 40 diz que taxa alta "leva a mínimo local", o vídeo diz que passa do mínimo e oscila.
- **Veredito:** aprovar os trechos acima. Pausado, claro, o único que liga custo → derivada → atualização → taxa de aprendizado.

### a5-v10 — pythonando, Regressão linear: Explicando gradiente (3:28) · NOVO
- **Cobre:** 00:00–00:40 curva do erro; 00:43–01:40 taxa 0,5: saltos grandes, não chega ao menor erro; 01:42–02:44 taxa 0,1: chega, mas com mais iterações; 02:57–03:17 custo cresce com mais dados.
- **Avisos:** a imagem está no vídeo (a transcrição só tem a fala); 0,5 é só exemplo.
- **Veredito:** aprovar 00:00–02:58, curto e direto para slides 40 a 43.

### a5-v11 — Nerd dos Dados, Learning Rate (16:48) · NOVO, opcional
- **Cobre:** 04:47–06:00 taxa de aprendizado = quanto muda a cada erro (0,1; 0,001; 0,01); 06:02–09:00 analogia de descer a montanha de olhos vendados; taxa alta oscila, baixa demora; 09:01–09:50 comparativo.
- **Avisos:** contexto de redes neurais; 13:00–15:30 explicação do "buraco" e "gradiente não pode chegar a zero nem passar de zero" é confusa e errada (conhecimento externo); exageros e propaganda.
- **Veredito:** aprovar 04:47–09:50 só como complemento (`optional`).

### a5-v12 — Saulo Reis, Regularização II: Regressão Ridge (10:46) · NOVO
- **Cobre:** 02:00–03:07 regularização reduz a influência de features por penalidade e permite modelos complexos sem overfitting; 04:01–06:00 somar termos quadráticos dos parâmetros ao custo obriga o gradiente a diminuí-los; 06:29–08:49 Ridge λ × Σθ², λ grande demais dá modelo constante (underfitting), λ zero pode dar overfitting.
- **Não cobre:** Lasso, seleção de variáveis, geometria. Notação θ; 09:00–10:30 é cálculo da regra de atualização.
- **Veredito:** aprovar 02:00–08:50. Explica o slide 45 e o Ridge do slide 46 do zero.

### a5-v13 — ProfDanilo_DS, Regressão de Lasso, Ridge e Elastic Net (6:23) · NOVO, com ressalva
- **Cobre:** 01:33–02:20 multicolinearidade; 02:08–02:30 regularizadores adicionam viés; 02:58–03:44 Lasso (L1) zera coeficientes e os não anulados são os importantes; 04:10–05:10 Ridge (L2) encolhe sem reduzir o número de variáveis; 05:10–05:50 Elastic Net.
- **Problema:** a transcrição está bem ruim ("rede" = ridge, "baia" = viés, trechos sem sentido em 05:30–05:50). As ideias acima foram lidas nos trechos legíveis; **confira pelo áudio**.
- **Veredito:** aprovar 01:33–05:12. É o único vídeo curto que põe Lasso e Ridge lado a lado em português.

### a5-v14 — Abel Siqueira, Regularização Ridge/L2, LASSO/L1 e Elastic Net (21:06) · NOVO, opcional
- **Cobre:** 07:13–07:57 Ridge = custo + λ Σβ²; 10:00–11:50 polinômio de grau alto, regularizar suaviza o overfitting, demais puxa tudo a zero; 12:41–13:36 Lasso soma dos módulos, manda parâmetros a zero; 15:30–17:30 Lasso zera rápido, Ridge puxa todos devagar; 17:38–19:30 escolher λ por validação.
- **Problema:** 00:00–07:00 é matriz mal-condicionada (XᵀX), álgebra linear; 12:00–12:35 a transcrição repete "L1" sem sentido.
- **Veredito:** só como complemento, nos trechos acima.

### a5-v3 — Didática Tech, Coeficiente de determinação R2 (11:52) · OK
- **Cobre:** 00:45–02:00 gráfico e modelo da média; 02:00–04:00 SQT; 04:00–06:10 SQR; 06:14–07:10 R² = (SQT − SQR)/SQT; 07:10–09:00 R² = 0 (igual à média) e R² = 1; 09:20–11:28 "87% melhor que a média" e "explica 87% da variância".
- **Avisos:** diz que R² fica entre 0 e 1 (versão do slide 51; a literatura admite negativo em teste: responder com o slide); "SKT/SKRS". Remete o R² ajustado ao próximo vídeo da série (a5-v15).
- **Veredito:** aprovar 00:45–11:28. Melhor vídeo da aula.

### a5-v15 — Didática Tech, Coeficiente R2 ajustado (8:22) · NOVO
- **Cobre:** 00:14–01:49 o R² só melhora ao adicionar variáveis; 01:49–02:52 o ajustado penaliza a quantidade e só sobe se a nova variável for relevante; 07:19–08:01 resumo. 03:00–07:00 é a fórmula, algébrica.
- **Veredito:** aprovar 00:14–02:52 e 07:19–08:01.

### a5-v16 — Didática Tech, Erro médio absoluto × erro médio quadrático (9:58) · NOVO
- **Cobre:** 01:03–02:45 erro absoluto de duas turmas; 03:14–04:20 erro quadrático; 05:11–06:05 o MSE penaliza muito mais o que está longe; 07:00–09:40 quando usar um ou outro.
- **Avisos:** o "erro" é a diferença para a média da turma, não para uma previsão; soma em vez de média (6, 14; 10, 62); não fala de RMSE.
- **Veredito:** aprovar 00:03–09:38.

## 3. Descartados

| Vídeo | Motivo |
| :-- | :-- |
| `Xm2C_gTAl8c` StatQuest, Ridge vs Lasso, Visualized (a5-v4 anterior, 9:06) | Áudio em inglês; a transcrição "pt" é uma tradução forçada ilegível ("o sumo dos resíduos em um graf", "a loja é igual a 40"); aos 00:23 o vídeo diz que **pressupõe que você já conhece Ridge e Lasso** (os slides 45–46 são a introdução). Ficou como lacuna substituída por a5-v12/v13/v14. |
| `CiP5Cu5fclU` Practical stats, Lasso e Ridge explicadas (3:46) | Áudio em inglês (narração sintética, "deep dive"), apesar do título em português. Conteúdo correto (Ridge círculo, Lasso losango, escolher Ridge ou Lasso), mas só em inglês; não necessário. |
| `xdDL_8Sg6JI` Zurubabel, Gradient Descent (Parte 1) (8:18) | Fala confusa, fórmula errada que ele mesmo corrige ("eu errei"), sem desenho legível na transcrição; só 01:00–02:50 ("valor inicial, taxa de aprendizado, descer pouco a pouco") tem algo útil, já dito melhor por a5-v7 e a5-v9. |

## 4. Mapa de cobertura final (slides × vídeos)

| Slides | Tópico | Vídeo e trecho | Situação |
| :-- | :-- | :-- | :-- |
| 3–6 | Regressão, Y = α + βx, dependente/independente | a5-v1 03:13–03:43 | parcial (notação a, b) |
| 7–9 | Pearson; correlação X-Y e X-X | a5-v5 00:46–03:55; multicolinearidade em a5-v13 01:33–02:20 | slide 7–8 ok; slide 9 (exemplo felicidade) e causalidade: leitura |
| 10 | Erro, resíduo | a5-v1 01:40–03:02; a5-v3 04:00–06:10 | bom |
| 11 | Função de custo | a5-v2 00:25–05:00 | bom |
| 12 | Estratégias para achar α e β | a5-v1 03:43–04:57 (só mínimo por derivada); a5-v7 | parcial: força bruta × passos × GD fica na leitura |
| 13–17 | Simples × múltipla, hiperplano | a5-v6 | bom (plano 3D com duas variáveis; "hiperplano" na leitura) |
| 18–19 | Quando aplicar; beta; padronizar | a5-v6 07:58–08:56 (interpretação do coeficiente) | **LACUNA**: padronizar para comparar betas, boa correlação linear |
| 20–22 | OLS (matriz) × GD; complexidade | nenhum | **LACUNA**: OLS matricial, inversão de matriz, custo linear |
| 23–25, 28 | Gradiente descendente: ideia | a5-v7; a5-v9 | bom |
| 26–27 | Derivada | a5-v8; a5-v9 02:50–05:34 | bom |
| 29–34 | SQR, fórmulas de atualização de m e b | a5-v9 00:39–01:35 e 17:42–20:00 | parcial: as derivadas de m e b exigem cálculo e ficam na leitura |
| 35–40 | Taxa de aprendizado, convergência, valores típicos | a5-v9; a5-v10; a5-v11 (opcional) | bom |
| 41–44 | Hiperparâmetros: iterações e taxa (figuras) | a5-v9 21:21–23:05; a5-v10 | parcial (figuras específicas na leitura) |
| 45–46 | Regularização, Ridge, Lasso | a5-v12; a5-v13; a5-v14 (opcional) | bom (Ridge em a5-v12; Lasso em a5-v13 e a5-v14) |
| 47–48 | Conclusão: MQO × GD | nenhum | **LACUNA** (leitura) |
| 50–51 | SQR, R² | a5-v3 | bom |
| 52 | R² ajustado | a5-v15; a5-v6 06:36–06:48 | bom |
| 53–54 | MAE, MSE | a5-v16 | bom (sem RMSE) |

## 5. Lacunas que ficam para a leitura (`aula-5-do-zero.md`)
1. **OLS (mínimos quadrados ordinários) matricial, inversão de matriz, custo × GD, quando usar cada um** (slides 20–22 e 47): não achei vídeo em português que compare os dois; os candidatos eram só cálculo manual (Murakami) ou OLS simples. Não transcrevi mais.
2. **Padronizar variáveis para comparar betas** e "quando aplicar regressão" (slides 18–19).
3. **Estratégias de otimização** do slide 12 (força bruta, passos, passos variáveis).
4. **Derivadas parciais de m e b** (slides 30–34) e a figura das iterações (slides 41–44).
5. **Exemplo felicidade × expectativa de vida e causalidade** (slide 9).
6. **Hiperplano** com mais de duas variáveis pelo nome (slide 15).
7. **RMSE** e a comparação MAE × MSE do slide 54.
8. **Lasso/Ridge**: "sossega-leão" e geometria só em a5-v14 (opcional); a transcrição de a5-v13 é ruim, vale conferir pelo áudio.

## 6. Pendências de metadados em `block.json` (não editei)
Duração de a5-v5 passou de 6:26 para **8:38**; títulos reais dos vídeos; a5-v4 sai; slides de a5-v5 passam para 7–8. O JSON final está em `proposta_b2_aula5.json` (scratchpad), com clips dentro das durações e `optional` em a5-v11 e a5-v14.

- **11/10/2026 (agente principal):** o a5-v13 passou de obrigatório a opcional: é um resumo curto, com legenda ruim, dos mesmos slides 45 e 46 do a5-v12; nada foi removido.
