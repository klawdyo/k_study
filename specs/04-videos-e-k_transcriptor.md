# 04 · Vídeos e o k_transcriptor

O k_study **não** busca nem transcreve vídeos. Isso é feito pelo **k_transcriptor** (outro repositório do mesmo autor; comando `ktr`). Ele busca no YouTube, baixa **só o áudio** (um por vez), transcreve localmente com o Whisper (GPU NVIDIA se houver; senão CPU) e guarda a transcrição com minutagem. A transcrição é o que permite **conferir o que o vídeo realmente diz**.

## Instalar o k_transcriptor

1. Procure uma pasta irmã (`../k_transcriptor`) ou uma instalação existente (`ktr where`; `ktr --help`). Se já houver, use-a.
2. Se não houver, clone fora da pasta do k_study (por exemplo, ao lado dele). A URL é **`https://github.com/klawdyo/k_transcriptor.git`**; um clone existente mostra a URL com `git remote -v`.

   ```bash
   git clone https://github.com/klawdyo/k_transcriptor.git ../k_transcriptor
   cd ../k_transcriptor
   ```
3. Instale seguindo o `README.md` do próprio k_transcriptor (hoje: `.\install.ps1` no Windows, `sh install.sh` em Linux/macOS; o README pode indicar `py main.py setup`: **vale o README dele**). Requer Python 3.10+. O instalador faz `ktr doctor --download-model` (baixa o modelo, cerca de 0,5 GB na primeira vez).
4. Confira: `ktr doctor`.

Antes de baixar qualquer áudio, **tenha a autorização da pessoa** (pergunta B5 da entrevista) registrada no `brief.md`.

## Comandos do dia a dia

```bash
ktr search regressão linear explicação              # id | duração | canal | título | views   (--limit N)
ktr transcribe ID1 ID2 --language auto --copy-to content/<slug>/transcripts
ktr text ID                                         # lê a transcrição com mm:ss
ktr queue --watch                                   # fila ao vivo, em outro terminal
ktr export ID1 ID2 --to content/<slug>/transcripts # copia transcrições já em cache
ktr captions ID1 ID2                                # legenda do YouTube (rápido, mas o IP é bloqueado após ~15 consultas)
ktr clean                                           # apaga os áudios; ÚNICO que apaga
ktr where                                           # onde fica o cache
```

- **Fila única.** Várias chamadas, em vários terminais, entram na mesma fila; cada chamada só retorna quando os **seus** vídeos terminam. Downloads **um por vez** (não aumente `--downloads`); transcrição até 2 em paralelo (`--workers`).
- **Idioma.** O padrão é `pt`. **Use `--language auto`** sempre que o vídeo puder estar em outro idioma: forçar `pt` num vídeo em inglês produz texto sem sentido.
- **Tempo.** Na GPU, dezenas de vídeos em poucos minutos; na CPU, ≈ 4× o tempo do vídeo. Rode em segundo plano e escreva leituras enquanto espera.
- **Bloqueio do YouTube** (saída 3): peça à pessoa para trocar de rede (por exemplo, o celular) e rode o mesmo comando de novo; a fila retoma.
- **Saída:** 0 ok, 1 algum vídeo falhou, 2 erro de uso, 3 bloqueio.
- **IDs que começam com `-`:** use `--` antes (`ktr text -- -abc12345678`).
- **Transcrição automática tem erros** (nomes técnicos, sotaque). Leia como apoio, não como verdade, mas não decida pelo título.
- **Áudio nunca fica dentro de `content/`** nem no Git. `ktr clean` só com a fila vazia (`ktr queue`) e **só com certeza** (regra 8 abaixo).

## Como escolher vídeos (regras aprendidas, todas obrigatórias)

1. **Leia a transcrição inteira**, por minuto. **Nunca decida pelo título** (títulos podem estar traduzidos, enganosos ou de outro idioma).
2. **Todo `mm:ss` citado** em `covers`, `clips` e `verdict` tem de **existir** na transcrição e caber na `duration` real. Já houve validação inventada: tempos além da duração, `covers` que não estão na fala. O validador só **avisa** (um clip pode passar do fim por música ou silêncio): leia o aviso e decida.
3. **Confira idioma e qualidade da transcrição.** Texto ilegível ou em outro idioma: repita com `--language auto`; se continuar ilegível, descarte ou declare em `note`.
4. **Trechos (`clips`) com `slides` e `note`:** use só a parte útil; pule vinhetas, introduções repetidas, patrocínios, partes de código longas demais para o nível ou fora do escopo. `slides` cita o número no material; `note` diz o que o trecho ensina e o que pular.
5. **Avisos de divergência (`warnings`):** onde o vídeo diz algo diferente do material, simplifica ou erra (a transcrição pode trocar uma frase: avise). Divergência material × literatura: veja `05`.
6. **`covers` reais:** apenas o que o vídeo realmente explica, com horário. `notCovered` diz o que falta.
7. **Um vídeo bom por tópico.** Sem sobreposição desnecessária. Em empate: português, mais curto e mais didático.
8. **Escolha o mais didático PARA O NÍVEL da pessoa.** Analogias, exemplos, passo a passo, `profile` "iniciante". **Nunca troque um vídeo didático por um mais técnico/completo**; os técnicos viram opcionais.
9. **Só remova duplicado com 100% de certeza** (mesmo conteúdo, mesmo exemplo, nada que o outro não tenha). Se os vídeos se completam (outro exemplo, outra analogia, código × teoria), **mantenha os dois**, o menos essencial como `optional: true`. Na dúvida, opcional em vez de remover.
10. **Nenhum vídeo é removido, nem `ktr clean` rodado, sem leitura da transcrição e veredito com motivo na ficha.** Cada vídeo baixado foi baixado para ser comparado com o material. Transcrição que não está em nenhum bloco nem ficha ("órfã") conta como não avaliada. Quem integra confere pessoalmente; o relatório de um subagente não substitui a leitura.
11. **Meta de tempo obrigatório por aula** (padrão 60 a 120 min): vídeos aprovados que só repetem o que outro já cobre saem do bloco e ficam na ficha como "redundante" (continuam lidos e registrados); o que cobre tópico sem outro vídeo, ou é muito melhor, fica (opcional se passar da meta).
12. **Sem lacunas sem tentar duas rodadas** de busca por tópico. Se continuar sem vídeo bom: a leitura cobre, e a ficha lista a lacuna. **Não complete a lista com vídeo fraco.** Vídeo em inglês só se claramente superior, com aviso em `note`.
13. **Canal e título** do item vêm do que você viu (busca/oEmbed); se não conferiu o canal no YouTube, registre "a verificar" na ficha, não invente.

## Ficha de conferência (`block-N/validacao-videos-aula-N.md`)

Uma por aula (ou por rodada: `...-aula-N-rodada2.md`). Estrutura:

1. **Cabeçalho:** método (li a transcrição inteira de cada candidato, local, Whisper `small`, com erros), tópicos conferidos (N tópicos do material, onde está o texto), limites (o que não foi visto, material só com figura), legenda da matriz (B cobre bem · P parcial · – não cobre · X diverge/erra).
2. **Tabela de IDs:** sigla, ID, canal/título, duração, idioma.
3. **Matriz tópico × vídeo** (linhas = tópicos do material com slides; colunas = vídeos).
4. **Fichas por vídeo:** cobre (com `mm:ss`), não cobre, divergências, nível e foco, idioma/qualidade da transcrição, trechos recomendados (soma de minutos), **veredito** (`aprovar`, `aprovar só os trechos X`, `opcional`, `redundante`, `descartar`) com motivo.
5. **Descartados** com motivo; **redundantes** (por sobreposição) com o vídeo que cobre.
6. **Lacunas** (tópicos sem vídeo bom; coberto pela leitura; 2 rodadas feitas).

Modelo em `09-templates.md`. A ficha é registro: não aparece na interface.

## Direitos de terceiros

- Os vídeos são **linkados** (incorporados do YouTube). Não os reenvie nem os hospede.
- As transcrições servem a **estudo pessoal** e à conferência; não as redistribua como obra. Se o repositório da trilha for público, avalie se `transcripts/` deve ir para o `.gitignore` (decisão da pessoa; registre no brief).
- Cite sempre o **link original** (a URL do item).
- Os termos do YouTube em geral proíbem baixar vídeos sem autorização do autor: use poucos vídeos, para estudo, e nunca compartilhe o áudio.
