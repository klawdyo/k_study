# 03 · Interface do aluno: login em etapas, nome, cores, rotas por id

**Depende de:** só do contrato (a tarefa 01 escreve o servidor real; desenvolva contra o contrato e teste contra o servidor real se já existir).

## Leia primeiro

`docs/arquitetura.md` (revisão 2: seções 5, 6, 7 e 8), a interface atual (`src/k_study/web/index.html`, `app.js`, `style.css`, `vendor/`) e `.tasks/00-manifest.md` (regras gerais).

Para testar sem o servidor real, escreva um servidor falso mínimo FORA do repositório (pasta temporária) que implemente as rotas do contrato. Se o real já existir: `py main.py serve --port 8791 --db <banco temporário> --env <.env temporário>`.

## Arquivos desta tarefa

`src/k_study/web/**` (só eles).

## O que fazer

1. **Login em etapas (seção 5):** a tela pede só o e-mail (validar formato, tirar espaços, minúsculas) → `POST /api/auth/check`; se existe, pede a senha → `POST /api/auth/login`; se não existe, pede senha, confirmação da senha e NOME → `POST /api/auth/register`; se `firstUser` for verdadeiro, avisar que esta conta será a administradora. Mostrar os erros da API (`message`) e o limite de tentativas (`429` com `Retry-After`: "tente de novo em N minutos"). Botão "mostrar senha"; `autocomplete` corretos (`username`, `current-password`, `new-password`); sem senha em log nem em URL.
2. **Nome e e-mail sempre juntos** onde o aluno aparecer (cabeçalho, menu do usuário). Menu do usuário com "Sair". Para admin (`isAdmin`), na grade de trilhas, um botão **"Administração"** que leva a `/admin/`.
3. **Grade de trilhas** (`GET /api/trails`): a barra de progresso **conta tudo**, `done / items` (o servidor conta toda aula feita, obrigatória ou opcional); mostrar também "N obrigatórias" quando houver opcionais; usar a capa (`cover`, uma URL; `loading="lazy"`) quando existir, com um degradê elegante como alternativa; estado vazio claro.
4. **Obrigatória × opcional com cores próprias e acessíveis:** "Opcional" num chip âmbar/neutro distinto; "Obrigatória" (ou "Importante") na cor de destaque; contraste suficiente nos temas claro e escuro, e nunca só pela cor (também texto). Aparecem no menu lateral, no cabeçalho de cada aula e na lista do bloco.
5. **Conteúdo por IDS, nunca por caminho:** bloco em `/api/trails/<slug>/blocks/<block>`; conteúdo da aula em `.../items/<item>/content`; transcrição em `.../items/<item>/transcript`; imagens em `/api/trails/<slug>/figures/<nome>` (reescrever `../figures/x.png` no markdown e nos enunciados das questões para essa rota usando só o nome do arquivo; nome fora de `[A-Za-z0-9._-]+` não vira imagem). Remover qualquer uso da rota antiga `/files/`.
6. **Markdown seguro (XSS):** o `marked` configurado para NÃO inserir HTML bruto (o renderer `html` escapa); só links `http`, `https`, `mailto`, âncoras e rotas internas (`target=_blank` com `rel="noopener noreferrer"`); imagens só pela rota de figuras; nunca `innerHTML` com texto do conteúdo fora do renderizador seguro; nomes, e-mails e títulos sempre com `textContent`. Teste com conteúdo hostil (`<script>`, `<img onerror>`, `[x](javascript:...)`) e confira que nada executa. A CSP do servidor é `script-src 'self'`: NENHUM script nem manipulador inline (`onclick=`); use `addEventListener`.
7. **CSRF:** pegar `csrfToken` de `GET /api/auth/me` e enviar `X-CSRF-Token` em toda escrita com `Content-Type: application/json`; o rastreio por `sendBeacon` envia o token no corpo (`csrf`). Em `403 csrf_failed`, recarregar o token e tentar uma vez.
8. Manter tudo que já funciona (seletor de bloco, menu, selos, próxima aula, vídeos com trechos, transcrição, questões uma por vez, anotações, rastreio de tempo, tema claro e escuro, celular) e a acessibilidade. Nenhum "null" ou "undefined" na tela.

## Aceite

Teste de verdade no navegador (desktop e celular; claro e escuro; console sem erros). **Não deixe vídeos do YouTube tocarem nos testes** (o usuário ouve o áudio): não clique em trechos nem em horários; verifique pelo DOM.

## Ao terminar

Atualize a linha 03 do manifesto e o "Registro" (o que testou e contra qual servidor).
