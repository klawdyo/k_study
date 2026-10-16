# 07 · Validação e qualidade

`py main.py validate <slug>` confere a **estrutura**. Ele **não prova qualidade**. Uma geração anterior passou no validador e a auditoria achou: validação de vídeos **inventada** (tempos além da duração do vídeo, `covers` que não existem na fala, vídeo em inglês transcrito como português), LaTeX nas leituras, leituras com 184 a 235 linhas, respostas quase sempre na mesma alternativa e sempre a mais longa. Use esta spec para não repetir.

## O que o `validate` REPROVA (erros; saída 1)

- ids duplicados (itens no bloco, questões no arquivo); tipo de item desconhecido;
- bloco do `trail.json` cujo `id` difere do `id` dentro do `block.json`;
- `path`/`transcript`/`promptFile` inexistente ou que sai da pasta da trilha;
- imagem Markdown (`![](...)`) que não existe (em leituras, enunciados e explicações);
- vídeo com URL sem id do YouTube; `clips` com `end` ≤ `start`; `review` sem `transcript`;
- questão `single` sem exatamente 1 correta; `multiple` com menos de 2; tipo de questão desconhecido;
- alternativa **sem `explanation`**; questão sem `generalExplanation`;
- **caracteres de controle** no texto (uma barra invertida mal escapada no JSON, como `\beta`, `\text`).

## O que só AVISA (heurísticas; leia e decida)

- trecho ou horário de `covers` além do fim do vídeo por mais que max(30 s, 5%), ou trecho que começa muito depois da última fala (o fim do vídeo pode ser música ou silêncio);
- LaTeX em Markdown ou questões (a interface não renderiza);
- posição da correta: mais de 60% numa mesma letra (com ≥ 6 `single`); correta a mais longa em mais de 70% das `single`;
- explicações de alternativa com menos de 40 caracteres;
- leitura com menos de 250 linhas (a meta é 350 a 700; arquivos `guia`/`guide` são isentos).

Aviso não é erro, mas **todo aviso deve ser lido**; resolva ou justifique no brief. Se este texto divergir do validador (`src/k_study/validate.py`), vale o código.

## O que ele NÃO prova (você tem de conferir)

- Que um `mm:ss` de `covers`/`clips`/`verdict` existe **de fato na fala** (só o fim do vídeo é checado).
- Que o vídeo **ensina** o tópico que a ficha diz, ou que o idioma é o declarado.
- Que a leitura **cobre 100%** do material e não atribui a ele o que não diz.
- Que o gabarito está certo, o código roda e os distratores são plausíveis.
- Que não há conteúdo de terceiros copiado literalmente.
- Que a trilha cabe na meta de tempo e na ordem de pré-requisitos.

## Checklist de auditoria própria (antes de dar como pronta)

**Vídeos**
- [ ] Li a transcrição **inteira** de cada vídeo do bloco e de cada candidato descartado (nenhuma transcrição órfã).
- [ ] Amostrei pelo menos 3 `mm:ss` por vídeo contra `ktr text ID`: a fala bate com o `covers`.
- [ ] Idioma e legibilidade da transcrição conferidos (`lang`, texto com sentido).
- [ ] `warnings` registram onde o vídeo diverge do material.
- [ ] Cada tópico do material tem vídeo bom ou lacuna declarada após 2 rodadas; nenhum vídeo fraco só para preencher.
- [ ] Didático para o nível; nenhum vídeo didático trocado por um técnico; só duplicado 100% removido.
- [ ] Tempo obrigatório por aula dentro da meta; opcionais marcados.

**Leituras**
- [ ] 350 a 700 linhas; tabela de cobertura; "Se perguntarem…"; divergências com as duas versões.
- [ ] Sem LaTeX, sem callouts, sem emojis; nada atribuído ao material que não esteja nele.
- [ ] Todo código executado.
- [ ] Figuras próprias, existentes.

**Questões**
- [ ] Todo tópico coberto; mistura de tipos igual à da avaliação real; sem cálculo se a avaliação não tem.
- [ ] Toda alternativa explicada com o porquê; sem citação por letra.
- [ ] Posições equilibradas; correta não é sistematicamente a mais longa.
- [ ] Gabaritos refeitos (contas, código rodado).

**Geral**
- [ ] `validate` sem erros; avisos tratados.
- [ ] `brief.md` atualizado (decisões, pendências, totais).
- [ ] Servidor aberto no navegador: um vídeo com trechos, uma leitura com imagem, uma questão, o cartão de transcrição.

## Auditoria por subagente independente

Depois de pronto, rode um subagente **que não escreveu nada** da trilha, só lê. Instruções: "Audite `content/<slug>/` contra `specs/07-validacao-e-qualidade.md`. Para cada bloco: (1) confira 5 vídeos por amostragem lendo a transcrição contra o `review`; (2) procure gabaritos suspeitos refazendo 10 questões; (3) liste tópicos do material sem leitura/questão; (4) liste afirmações atribuídas ao material que ele não contém; (5) liste LaTeX, citação por letra, posições concentradas. Devolva uma lista de achados com arquivo e linha, sem corrigir." Corrija você mesmo e registre no brief. Se o conteúdo é crítico para a pessoa (prova próxima), repita a auditoria depois das correções.

## O que NUNCA fazer

1. **Inventar** timestamps, `covers`, números, referências, canais ou o que um vídeo diz.
2. **Remover um vídeo** (ou rodar `ktr clean`) sem ter lido a transcrição contra o material e registrado o veredito e o motivo na ficha; só com certeza de que nenhum vídeo baixado pode ser útil.
3. **Decidir por título**; trocar um vídeo didático por um técnico; completar lista com vídeo fraco.
4. **Mexer em ids publicados** (trilha, bloco, item, questão) ou embaralhar alternativas de questões já respondidas por alunos.
5. **Editar o banco** (`data/k_study.db`) ou o progresso de alunos; zerar progresso.
6. **Publicar material de terceiros literal** (slides, figuras, trechos longos de livros, transcrições como obra).
7. Pôr LaTeX, callouts ou emojis nas leituras; deixar barra invertida mal escapada em JSON.
8. Entregar gabarito não conferido ou código não executado como se tivesse sido.
9. Baixar vários vídeos ao mesmo tempo, guardar áudio/vídeo dentro de `content/` ou no Git.
10. Perguntar "posso continuar?" a cada etapa depois da entrevista aprovada; ou, ao contrário, mudar o escopo aprovado sem avisar.
11. Alterar `docs/arquitetura.md` ou o código do servidor para "consertar" conteúdo: conteúdo se corrige no arquivo.
