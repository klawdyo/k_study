# study-app

App local de estudo: uma **interface web + API HTTP** que serve aulas (vídeos, leituras e questões) a partir de uma **pasta de dados** e guarda o seu progresso em **um único arquivo**. Também traz as **ferramentas de linha de comando** usadas para montar as aulas (busca no YouTube, legendas, transcrição local e validação do conteúdo).

- O app usa **somente a biblioteca padrão do Python**. As dependências pesadas (reconhecimento de fala) são opcionais.
- **Código e dados ficam separados.** Este repositório guarda só código. A pasta de dados (aulas, figuras, transcrições, `progress.json`) fica em outro lugar (por exemplo, uma pasta sincronizada) e é escolhida na primeira execução.
- **Fonte única de verdade.** A interface não guarda estado: conteúdo e progresso passam somente pela API, e a API é a única a gravar o `progress.json`.
- Código, identificadores, nomes de arquivos e chaves JSON são em inglês. O texto da interface e os arquivos Markdown que o estudante lê são em português.

## Instalação

```bash
git clone git@github.com:klawdyo/estudos.git
cd estudos
python -m venv .venv
.venv\Scripts\activate                # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -e .                      # só o app
pip install -e ".[all]"               # + legendas + transcrição local (yt-dlp, faster-whisper)
```

Extras: `captions` (youtube-transcript-api), `transcribe` (yt-dlp + faster-whisper), `dev` (pytest).

## Primeira execução: escolher a pasta de dados

```bash
study serve
```

Abra <http://localhost:8765/>. Se nenhuma pasta de dados estiver configurada, o app mostra a tela **"Onde estão os arquivos do curso?"** com uma dica de onde a pasta fica. Você tem duas formas de informar o local, e **o app nunca lista o disco**:

1. **Escolher o arquivo `config.json`** na janela de seleção do próprio sistema operacional (o servidor abre o seletor no seu desktop; no Linux pode ser preciso instalar `python3-tk`);
2. **colar o caminho** da pasta no campo de texto.

Depois clique em **Usar esta pasta**. A escolha fica salva **neste computador**, fora da pasta de dados (porque o caminho muda de um computador para outro):

| Sistema | Arquivo de configurações |
| :-- | :-- |
| Windows | `%APPDATA%\study-app\settings.json` |
| Linux / macOS | `~/.config/study-app/settings.json` (ou `$XDG_CONFIG_HOME/study-app/settings.json`) |

Para trocar depois, use o botão **"Trocar a pasta de dados"** no fim do menu lateral, ou `study data-dir CAMINHO` na linha de comando.

Ordem de precedência (a primeira que existir vence):

1. `--data-dir CAMINHO` (parâmetro de qualquer comando);
2. variável de ambiente `STUDY_DATA_DIR`;
3. a pasta salva neste computador (tela de escolha ou `study data-dir`).

Quando a pasta vem do parâmetro ou da variável de ambiente, ela fica **fixa** e a interface não oferece a troca. `STUDY_WORK_DIR` define a pasta temporária do áudio baixado (padrão: pasta temporária do sistema; nunca a coloque dentro de uma pasta sincronizada). `STUDY_SETTINGS_FILE` muda o local do arquivo de configurações (usado nos testes).

## Comandos

```bash
study serve [--port 8765]            # API + interface em http://localhost:8765/
study data-dir [CAMINHO]             # mostra ou salva a pasta de dados deste computador
study validate                       # confere a pasta de dados (rode antes de dar um bloco por pronto)
study search TERMOS...               # busca no YouTube: id | duração | canal | título | visualizações
study captions ID... [--pause 6]     # baixa as legendas do YouTube para <dados>/transcripts (o YouTube limita)
study captions --text ID             # imprime uma transcrição guardada, com minutagem
study transcribe ID... [--model small] [--pause 20] [--overwrite]
                                     # reconhecimento de fala local, UM vídeo por vez; o áudio é apagado depois
```

`python -m study_app <comando>` também funciona (use `PYTHONPATH=src` ao rodar de um clone sem instalar).

### Sobre `study transcribe`

Para cada vídeo, baixa **só o áudio** (m4a, cerca de 1 MB por minuto) em `STUDY_WORK_DIR`, transcreve com o faster-whisper na CPU, grava `<dados>/transcripts/<id>.json` e **apaga o áudio**. Medido: cerca de 4 vezes a duração do vídeo com o modelo `small` numa CPU de 16 núcleos; a primeira execução baixa o modelo (~0,5 GB, guardado no cache do Hugging Face). Um `403` do YouTube pode ser passageiro: repita aquele vídeo sozinho. Os termos de uso do YouTube em geral proíbem baixar vídeos sem autorização do autor: use para estudo pessoal, poucos vídeos, e nunca guarde nem compartilhe o áudio.

`study captions` é bem mais rápido, mas o YouTube bloqueia o IP depois de cerca de 15 consultas seguidas (`IpBlocked`); quando isso acontecer, use `transcribe`.

## Pasta de dados

```
config.json                   lista de blocos
progress.json                 gravado SOMENTE pela API
transcripts/<videoId>.json    {lang, generated, duration, source, title, segments: [[segundo, "texto"], ...]}
figures/                      imagens usadas pelas leituras e pelas questões
block-1/block.json            seções -> itens (video | markdown | pdf | link | questions)
block-1/*.md, *.pdf           leituras
block-1/*-questions.json      conjuntos de questões
```

Todo caminho é relativo ao arquivo que o contém e precisa ficar dentro da pasta de dados. Esquema completo: [docs/data-model.md](docs/data-model.md).

## API

| Rota | O que faz |
| :-- | :-- |
| `GET /api/setup` | situação da pasta de dados: `{configured, dataDir, source, home, sep, savedDir}` |
| `POST /api/setup/pick` | abre o seletor de arquivos do sistema e devolve a pasta do `config.json` escolhido (não grava; `409` se a pasta estiver fixada) |
| `PUT /api/setup` | `{"path": "..."}` escolhe e salva a pasta de dados (recusa se não houver `config.json`; `409` se a pasta estiver fixada por parâmetro ou variável de ambiente) |
| `GET /api/config` | devolve o `config.json` (`409` enquanto não houver pasta configurada) |
| `GET /api/content/<caminho>` | lê um arquivo dentro da pasta de dados (nunca fora dela) |
| `GET /api/progress` | estado completo `{items, answers, notes}` |
| `PUT /api/progress/items/<bloco>/<item>` | `{"done": true}` |
| `PUT /api/progress/answers/<bloco>/<item>/<questão>` | `{"chosen": ["a"], "correct": true}` |
| `DELETE /api/progress/answers/<bloco>/<item>/<questão>` | apaga a resposta |
| `PUT /api/progress/notes/<bloco>/<item>` | `{"text": "..."}` (texto vazio apaga a anotação) |

Toda gravação de progresso salva o `progress.json` de forma atômica e devolve o estado completo atualizado. **Limites (por decisão):** só `127.0.0.1`, sem autenticação, um único usuário, a última gravação vence (o app não lista o disco; pedidos cujo cabeçalho `Host` não seja `localhost`, `127.0.0.1` ou `::1` são recusados com `403`, contra ataques de DNS rebinding; mesmo assim, não exponha o servidor na rede). Renomear o id de um item ou de uma questão faz o progresso dela sumir (a chave muda). A API não edita conteúdo: o conteúdo se edita como arquivo. A transcrição é de propósito um comando, e não uma rota da API.

## Comportamento da interface

Abrir um item com um clique o marca como feito (dá para desmarcar na própria página); itens opcionais não contam e são pulados pelo "PRÓXIMO"; quando a aba volta a ter foco, a interface relê o estado da API; se a API estiver fora do ar, aparece uma faixa vermelha e nada é salvo.

## Desenvolvimento

```bash
pip install -e ".[dev]"
pytest
```
