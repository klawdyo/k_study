# 04 · Área administrativa: estatísticas, ativar, importar zip, baixar specs

**Depende de:** só do contrato (a tarefa 01 escreve as rotas `/api/admin/*`; a 02, o importador).

## Leia primeiro

`docs/arquitetura.md` (revisão 2: seções 5, 6, 7 e 11), o painel atual (`src/k_study/admin/`: `server.py`, `queries.py`, `web/`), `tests/test_admin.py` e `.tasks/00-manifest.md` (regras gerais). Antes eram DOIS servidores (porta 8766 só para o admin); agora há UM só (`kstudy serve`) e o admin é uma área dele.

## Arquivos desta tarefa

`src/k_study/admin/**` e `tests/test_admin.py`.

## O que fazer

1. Remover `src/k_study/admin/server.py` (servidor separado, login próprio, porta 8766). Manter `admin/queries.py` como biblioteca de consultas, adaptada ao esquema v2: alunos com `name` **e** `email` em todas as respostas, trilhas com `active`; as consultas recebem uma conexão SQLite (somente leitura quando possível) e não conhecem HTTP. Atualizar `tests/test_admin.py` para testar só as consultas, contra um banco temporário criado com o DDL EXATO da seção 4 do contrato (copie o DDL para a fixture).
2. Páginas em `src/k_study/admin/web/`, servidas pelo servidor principal em `/admin/` (`403` para quem não é admin; sem sessão, mandar para `/`). Reaproveitar o dashboard (visão geral, alunos, detalhe do aluno, trilhas, mapa de calor) e adaptar: usar `GET /api/auth/me` para checar `isAdmin` e obter `csrfToken`; todas as chamadas vão para `/api/admin/...` (seção 7); mostrar sempre NOME e E-MAIL do aluno; link "← Voltar às trilhas" para `/`.
3. Telas e ações novas:
   - **Trilhas:** lista com capa (`cover`), título, estado Ativa ou Desativada e nº de alunos; botão para desativar e reativar (`POST /api/admin/trails/<slug>/active` com `{active}`), com confirmação.
   - **Importar trilha:** seletor de `.zip` (e arrastar e soltar), caixa "substituir se já existir" (`replace=1`), envio do corpo cru com `Content-Type: application/zip` e `X-CSRF-Token`, barra de progresso do upload (`XMLHttpRequest`), exibição do resultado (slug e avisos) ou da lista de problemas (`400 invalid_package`), e atualização da lista.
   - **Specs:** botão "Baixar specs para criar uma trilha" que baixa `GET /api/admin/specs.zip`, com uma explicação curta em português de como usar (abrir um agente de IA numa pasta vazia, descompactar o zip e pedir a criação da trilha; o agente baixa o k_transcriptor, gera a pasta da trilha, empacota com `kstudy pack` e o admin envia o zip em "Importar trilha"). Não existe botão de criar trilha: o agente roda localmente, fora do servidor.
4. **Segurança da interface:** nenhum script nem manipulador inline (CSP `script-src 'self'`); nada de `innerHTML` com dados do servidor (use `textContent` e criação de nós); todo `POST` com `X-CSRF-Token`; erros da API exibidos com segurança.
5. Manter gráficos em SVG/canvas escritos à mão, tema claro e escuro, layout responsivo e estados vazios.

## Aceite

Teste de verdade no navegador (desktop e celular; claro e escuro; console sem erros) contra um servidor falso mínimo (fora do repositório) ou contra o real (`py main.py serve --port 8792 --db <banco temporário> --env <.env temporário>`). **Não deixe vídeos tocarem.**

## Ao terminar

Atualize a linha 04 do manifesto e o "Registro".
