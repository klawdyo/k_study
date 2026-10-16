# 05 · Leituras: o texto "do zero"

A leitura (`aula-N-do-zero.md`) é o centro da aula. Ela existe porque material de estudo escrito para quem já sabe foi rejeitado: o aluno passa a responder por intuição. O padrão de qualidade está em `content/aprendizagem-de-maquina/block-1/aula-1-do-zero.md` e `block-4/aula-10-do-zero.md` (com tabela de cobertura): leia um antes de escrever.

## Padrão

1. **Explicar do zero para o perfil da entrevista.** Cada ideia: **analogia do mundo do leitor** (a profissão dele) + exemplo concreto primeiro, **termo técnico depois**. Se o material usa o termo, mostre a ponte ("o que o material chama de X é isto").
2. **Ordem do material.** Siga a numeração (slide/página) e cite-a em cada seção ("slide 14"). Se a ordem do material atrapalha pré-requisitos, siga a ordem lógica e registre na tabela de cobertura onde cada slide foi parar.
3. **Cobertura 100% declarada.** No início, uma **tabela por tópico/slide**: número · assunto · tipo (`T` texto coberto, `F` só figura aberta e descrita, `T+F`) · seção da leitura. Todo tópico do material aparece. Slide só com figura: **abra e descreva**, ou marque "a verificar" (nunca finja ter lido).
4. **Exemplo numérico pequeno** (na entrada; quando a avaliação não tem cálculo, o exemplo só ilustra e **não exige conta do aluno**).
5. **"Se perguntarem na prova"** (ou "Se perguntarem na avaliação") no fim das seções: uma frase com o que precisa ficar. Adapte o rótulo ao objetivo (prova, entrevista, trabalho).
6. **Divergências material × literatura.** Onde o material diverge de livros/prática (ex.: uma métrica que o material diz limitada a 0..1 e a literatura admite negativa), registre **as duas versões** e diga **qual responder** na avaliação do aluno. Marque com um título "Atenção: divergência" (sem callout `[!NOTE]`).
7. **Armadilhas e erros comuns** em tabelas pequenas (o que parece certo e não é).
8. **Trechos de código EXECUTADOS.** Todo código na leitura e nas explicações foi rodado por você (instale a biblioteca se faltar). O "código corrigido" tem de funcionar. Comentários curtos; identificadores em inglês, comentários em português.
9. **Tamanho:** 350 a 700 linhas por aula (o validador avisa abaixo de 250, exceto arquivos `guia`/`guide`). Mais curto só com a aula realmente pequena e declarado no brief. Mais do que 900 linhas: divida em duas leituras.
10. **Para cada item de `goals` do vídeo/leitura:** o aluno deve conseguir responder ao final.

## Honestidade com o material

- **Atribua ao material só o que está nele.** O que é seu (exemplo, analogia, tabela, código) é **"exemplo nosso"**. Nunca ponha na boca do professor/slide algo que ele não disse.
- **Não copie o material literalmente.** Parafraseie e explique; citação curta de uma definição, entre aspas, com o número do slide, é aceitável; reconstruir o material por trechos, não.
- **Figuras:** **nunca copie slides ou figuras de terceiros.** Gere as suas (matplotlib, SVG, ASCII) com sementes fixas, ou descreva em texto/tabela. Figura que você abriu e conferiu pode ser descrita; copiar o arquivo só se a pessoa for a dona e autorizar. Toda imagem citada tem de existir em `figures/` (`../figures/x.png` a partir do bloco).
- **Sem fatos inventados:** nada de datas, nomes, números ou referências que você não verificou. "A verificar" é uma resposta válida.

## Formato

- Português do Brasil; termos técnicos mantidos com o original entre parênteses na **primeira** ocorrência ("validação cruzada (*cross-validation*)").
- **Sem LaTeX** (`$...$`, `\frac`…): use Unicode (→ ≤ ≥ × ≈ Σ √ ² μ σ).
- **Sem callouts** `> [!NOTE]` / `> [!TIP]` e **sem emojis**. Citação simples `>` é aceitável para "Se perguntarem na prova".
- Tabelas Markdown simples; blocos de código com a linguagem (` ```python `).
- Cabeçalho `#` único no topo; seções `##` numeradas na ordem do material.

## Esqueleto

```text
# Aula N do zero: <tema>
Parágrafo: leitor-alvo, como ler, o que fica em negrito.
**A pergunta que a aula inteira responde:** ...
## Cobertura por slide (tabela)
## 1. <tópico> (slides X–Y)
   analogia → exemplo → termo técnico → tabela/código → "Se perguntarem na prova"
## 2. ...
## Slides que só têm figura (descrição do que foi aberto)
## Divergências material × literatura
## Resumo final (checklist do que sair sabendo)
```

## Guia de leitura de código (opcional, para trilhas com código)

`guia-ler-codigo.md`: como ler um trecho do assunto do zero (para que serve cada função/comando, a **ordem correta das etapas**, erros de lógica comuns). Alimenta as questões de código (`06`). Nome com `guia`/`guide` é isento do aviso de leitura curta.

## Checklist antes de entregar a leitura

- [ ] Tabela de cobertura com todos os tópicos do material.
- [ ] Cada seção: analogia → exemplo → termo → "Se perguntarem…".
- [ ] Divergências registradas com as duas versões e qual responder.
- [ ] Todo código executado; sem LaTeX; sem callouts; sem emojis.
- [ ] Nada atribuído ao material que não esteja nele; "exemplo nosso" onde couber.
- [ ] Figuras próprias (ou descritas); todas existem em `figures/`.
- [ ] 350 a 700 linhas.
