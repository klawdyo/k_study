# 02 · Pacotes zip: importar trilha, empacotar trilha, zip das specs

**Depende de:** nada (só do contrato). A tarefa 01 chama as funções daqui.

## Leia primeiro

`docs/arquitetura.md` (revisão 2: seções 3 e 3.1 sobre o pacote zip, 7 rotas admin, 10 segurança, 11.1 assinaturas), `CLAUDE.md`, `docs/modelo-de-dados.md`, `src/k_study/validate.py`. Regras gerais: `.tasks/00-manifest.md`.

## Arquivos desta tarefa

`src/k_study/packages.py` e `tests/test_packages.py`.

## O que fazer

Implemente `packages.py` com as assinaturas EXATAS da seção 11.1 do contrato.

- **`class PackageError(Exception)`** com `problems: list[str]` (mensagens em português).
- **`import_trail_zip(content_dir, data: bytes, replace=False) -> dict`** devolvendo `{"slug", "warnings", "replaced"}`. Verificar TUDO antes de extrair:
  - uma única pasta de topo `<slug>/` com slug `[a-z0-9-]+`;
  - nenhuma entrada com `..`, caminho absoluto, `\`, letra de unidade, byte de controle ou NUL; recusar links simbólicos (atributos externos do zip) e diretórios estranhos;
  - extensões permitidas só `.json .md .png .jpg .jpeg .webp .gif .pdf .txt` (recusar SVG, HTML, JS, executáveis e o resto);
  - limites: ≤ 100 MB compactado; ≤ 300 MB descompactado (somar os tamanhos declarados **e** contar os bytes realmente lidos ao extrair, abortando se passar); ≤ 5000 arquivos; razão de compressão por arquivo ≤ 200 (zip bomb);
  - nomes duplicados após normalização (maiúsculas e minúsculas) recusados.
  - Extrair numa **pasta temporária dentro de `content_dir`** (não na pasta final), depois rodar o validador (`validate.py`, a função que valida uma pasta de trilha) e exigir **zero problemas** (avisos viram `warnings`).
  - Varrer o conteúdo de `.md` e `.json` e recusar `<script`, `<iframe`, `<object`, `<embed`, `javascript:`, `data:text/html` e atributos de evento `on...=`.
  - Conferir que `trail.json` tem `id` igual ao slug e que `cover`, se existir, é imagem png/jpg/webp ≤ 1 MB.
  - Slug já existente sem `replace` → `PackageError`. Com `replace`, trocar de forma **atômica** (renomear a pasta antiga para um backup temporário, mover a nova, apagar o backup só depois do sucesso; em qualquer falha, restaurar a antiga).
  - A pasta temporária é sempre removida em caso de erro. Nunca deixar lixo nem pasta pela metade. Nada de `shell`, `eval` nem execução do conteúdo.
- **`pack_trail(content_dir, slug, out_file) -> list[str]`:** valida a trilha (problemas → `PackageError`), recusa extensão não permitida, ignora lixo (`desktop.ini`, `.DS_Store`, `__pycache__`, `*.tmp`, `_tarefas.md`, `progress.json`, `.env`), grava um zip determinístico (ordem alfabética, datas fixas, deflate) com a pasta de topo `<slug>/` e devolve os avisos. O resultado tem de ser aceito por `import_trail_zip` (teste de ida e volta).
- **`build_specs_zip(root) -> bytes`:** zip em memória com `CLAUDE.md`, todos os arquivos de `specs/` e `docs/modelo-de-dados.md` lidos de `root`, com a mesma estrutura de pastas; não segue links simbólicos; erro claro se faltarem os arquivos; não inclui `.env`, banco nem nada fora dessa lista.

## Testes (pytest, sem rede)

Pacote válido (ida e volta); cada recusa (zip-slip `../x`, caminho absoluto, `\`, link simbólico, extensão proibida, SVG, HTML, pasta de topo errada ou múltiplas, slug inválido, zip bomb por razão e por tamanho, arquivos demais, `<script` em `.md`, `javascript:` em `.json`, `onerror=`, `trail.json` com id diferente, capa inválida, validação com problemas, slug duplicado sem `replace`); `replace` atômico (falha no meio restaura a antiga); pasta temporária sempre limpa; `build_specs_zip` lista exatamente os arquivos esperados e não segue symlink. Monte os zips (inclusive os maliciosos) nos testes com `zipfile` e `ZipInfo`.

## Aceite

Suíte verde; cada tentativa maliciosa falha sem deixar nada no disco; ida e volta de `pack_trail` → `import_trail_zip` funciona com a trilha `content/aprendizagem-de-maquina`.

## Ao terminar

Atualize a linha 02 do manifesto e o "Registro".
