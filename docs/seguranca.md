# Segurança do k_study

Auditoria da revisão 2 (tarefa 06): modelo de ameaças, OWASP Top 10 (2021), achados e correções, riscos residuais e recomendações. Os testes de exploração ficam em `tests/test_exploits.py` e rodam com a suíte (`pytest`). Este documento descreve o estado do código no momento da auditoria; se o código divergir, vale o código.

## 1. Modelo de ameaças

**O que protegemos:** as contas (e-mail, nome, hash da senha), o progresso dos alunos, o segredo do `.env`, o conteúdo das trilhas e a máquina que hospeda o servidor.

**Quem usa:** o administrador (primeira conta criada), alunos (contas comuns) e, de fora, qualquer pessoa que alcance a porta do servidor (no computador, na rede local com `--lan` ou atrás de um proxy).

| Ameaça | Exemplo | Defesa principal |
| :-- | :-- | :-- |
| Aluno curioso ou malicioso | ler o progresso de outro, abrir rotas do admin, ver trilha desativada | sessão obrigatória, `student_id` sempre da sessão, `is_admin` nas rotas admin, trilha inativa dá 404 |
| Visitante sem conta | adivinhar senhas, enumerar contas, ler arquivos do servidor | limite de tentativas, mensagem genérica no login, nenhuma rota serve arquivo por caminho |
| Página de outro site | CSRF contra um admin logado, DNS rebinding | cookie `SameSite=Strict`, token CSRF, checagem de `Origin` e de `Host`, `Content-Type` JSON obrigatório, sem CORS |
| Conteúdo de trilha hostil | `<script>`, `onerror=`, `javascript:` no markdown; zip malicioso | markdown escapado, CSP sem script inline, validação e quarentena do pacote, lista de arquivos permitidos |
| Pacote zip malicioso (do admin ou de alguém que o engane) | zip-slip, link simbólico, zip bomb, SVG com script | importador recusa o pacote inteiro; extração em pasta temporária; troca atômica |
| Atacante na rede (`--lan`) | espionar o tráfego, usar o servidor da casa | só redes privadas; **sem HTTPS próprio** (use proxy com HTTPS) |
| Roubo do disco ou do backup | copiar `data/k_study.db` | senhas só como hash `scrypt` + segredo; sem o `.env` as senhas não podem ser testadas |

**Entrada com o Google (opcional):** CSRF de login (alguém fazer a vítima entrar na conta do atacante) é barrado por `state` guardado em cookie assinado do navegador que iniciou o fluxo e por PKCE; um link de retorno aberto em outro navegador é recusado (`test_callback_sem_passar_pelo_inicio...`); `nonce` e `aud`/`iss`/`exp` impedem reaproveitar um `id_token` de outro cliente; `email_verified` é exigido; contas criadas pelo Google recebem um hash que nunca confere como senha, para que ninguém as "reivindique" cadastrando uma senha; o segredo do cliente nunca é enviado ao navegador; mensagens de erro são chaves fixas (nada da URL é refletido).

**Fora de escopo:** quem já controla o computador do servidor (acesso ao `.env`, ao banco e ao terminal pode tudo); ataques de negação de serviço distribuídos; confidencialidade do tráfego sem HTTPS.

## 2. OWASP Top 10 (2021)

| # | Categoria | Controles existentes | Evidência (teste) | Status |
| :-: | :-- | :-- | :-- | :-- |
| A01 | Controle de acesso | toda rota de dados exige sessão; rotas admin exigem `is_admin`; filtros por `student_id` da sessão; **nenhuma rota serve arquivo por caminho** (conteúdo por ids e lista `assets`); trilha inativa dá 404; `/admin/` só para admin | `test_exploits`: caminhos, trilha inativa, rotas admin, id vindo do corpo, isolamento; `test_server`; `test_auth` | OK |
| A02 | Falhas criptográficas | senha: `scrypt` (n=2^15, r=8, p=1, sal de 16 bytes) sobre `HMAC-SHA256(segredo, senha)`; tokens com `secrets`; só o SHA-256 do token vai ao banco; `.env` fora do git, `0600` quando possível; comparações com `compare_digest`; segredo nunca em log nem resposta | `test_security`, `test_auth` (hash, formato, sem texto puro), `test_exploits::test_segredo_nunca_aparece_em_respostas` | OK; sem HTTPS próprio (A02 no transporte: ver riscos) |
| A03 | Injeção | SQL sempre parametrizado (fragmentos fixos no código); sem `shell=True`, `eval` ou `exec`; markdown com HTML escapado, links e imagens filtrados; interface do admin sem `innerHTML`; CSP | `test_exploits::test_injecao_de_sql_nao_funciona`, `test_script_em_nome...`, `test_pagina...sem_script_inline`; verificação no navegador com trilha hostil | OK |
| A04 | Design inseguro | corpo JSON ≤ 1 MB; zip ≤ 100 MB; limite de tentativas; limite de cadastros por endereço; importação em quarentena; só um import de cada vez; tempo máximo de conexão parada | `test_exploits` (zips, 413, cadastros em massa, replace simultâneo, `Handler.timeout`) | OK (ver achado 3 e 4) |
| A05 | Configuração incorreta | cabeçalhos de segurança em toda resposta; sem listagem de diretório; sem traceback ao cliente (erro 500 genérico); `Server: KStudy` sem versão; `--lan` só com redes privadas; `OPTIONS`/`PATCH` respondem 405 sem CORS | `test_server`, `test_exploits` | OK |
| A06 | Componentes vulneráveis e desatualizados | só biblioteca padrão no servidor; único componente de terceiros no navegador: `marked` 12.0.2, vendorizado (abril de 2024) | conferido manualmente a versão (`web/vendor/marked.min.js`) | **Recomendação:** conferir os avisos de segurança do `marked` a cada atualização; não encontrei vulnerabilidade conhecida para a 12.0.2 até o meu conhecimento atual, mas **não consultei um banco de avisos nesta auditoria** (sem rede) |
| A07 | Falhas de identificação e autenticação | política de senha; limite de tentativas por e-mail+IP e por IP (429 + `Retry-After`); mensagem genérica; hash fictício quando o e-mail não existe; token de sessão trocado a cada login; expiração deslizante (30 dias) e absoluta (90); logout apaga no servidor | `test_auth`, `test_exploits` (fixação de sessão, IP falso, senha gigante) | OK; `check` revela se a conta existe (decisão de produto, ver riscos) |
| A08 | Falhas de integridade | pacote validado antes de registrar; extração em pasta temporária; troca atômica com restauração; CSRF em toda escrita; scripts só de `self` | `test_packages`, `test_exploits` | OK |
| A09 | Falhas de registro e monitoramento | `audit_log` com logins, falhas, cadastros e ações do admin (sem senhas nem tokens); o servidor não imprime tokens | `test_auth::test_auditoria_de_logins` | OK; sem rotação nem painel do `audit_log` (ver riscos) |
| A10 | SSRF | a única requisição de saída é a troca do código OAuth em `https://oauth2.googleapis.com/token` (endereço fixo, só com o login do Google configurado); nada vindo do usuário entra na URL; resposta limitada a 1 MB e tempo de 10 s | revisão do código (`oauth.exchange_code` é o único uso de `urllib.request`); `test_oauth::test_exchange_code_fala_so_com_o_endereco_fixo_do_google` | OK |

Também cobertos: **CSRF** (token por sessão, token pré-login, beacon no corpo só em `/api/track`), **CORS** (nenhum cabeçalho `Access-Control-*`), **cookies** (`HttpOnly`, `SameSite=Strict`, `Secure` com `K_STUDY_HTTPS=1`), **enumeração de usuários**, **fixação de sessão**, **DoS por corpo grande** e **condições de corrida** (primeiro admin com `BEGIN IMMEDIATE`; `replace` serializado).

## 3. Varredura de segredos

Feita em **dois repositórios** (k_study: 35 commits, 265 arquivos; k_transcriptor: 18 commits, 17 arquivos), na árvore atual (rastreada e não rastreada) e em todo o histórico (`git log --all -p`), com um scanner próprio em Python (expressões regulares para chaves e tokens conhecidos, URLs com senha, chaves privadas, JWT, caminhos pessoais, e-mails e entropia), já que `gitleaks` e `trufflehog` não estavam instalados.

- **Nenhum segredo real encontrado** (chaves de IA, nuvem, GitHub, Slack, Stripe, JWT, chaves privadas, senhas em URL, `.env`, bancos, cookies).
- Falsos positivos: e-mails de teste (`a@b.co`, `exemplo.com`), `git@github.com` em documentação e o texto `C:\Users\...` que descreve o padrão na tarefa 06.
- `.env`, `data/` e `*.db` estão no `.gitignore` do k_study e **nenhum está rastreado, nem no histórico**. O `.env` foi acrescentado ao `.gitignore` nesta revisão.
- **Informativo:** o nome e o e-mail do autor (`klawdyo@gmail.com`) estão nos metadados de todos os commits dos dois repositórios; ficam públicos quando publicados. Se isso for indesejado, é preciso reescrever o histórico antes de publicar (decisão e autorização do dono do repositório).
- **Recomendação para o k_transcriptor:** o `.gitignore` dele não lista `.env`; não há `.env` lá hoje, mas vale acrescentar. Não alterei esse repositório (fora do escopo desta tarefa).

## 4. Achados e correções

| # | Achado | Gravidade | Correção | Teste |
| :-: | :-- | :-: | :-- | :-- |
| 1 | O e-mail aceitava caracteres de HTML e de controle de sintaxe (`<script>@x.co`, `a"b@x.co`): ficavam guardados como texto e a interface escapa, mas apareceriam em logs e telas futuras | baixa | validação passou a aceitar só `atext` do RFC 5322 na parte local e letras, números e hífen no domínio | `test_security::test_email_e_nome`, `test_exploits::test_script_em_nome...` |
| 2 | O servidor aguardava indefinidamente um cliente parado (slowloris), segurando uma thread por conexão | média | `Handler.timeout = 60` s sem receber bytes; o descarte de corpo excedente espera no máximo 2 s | `test_servidor_derruba_conexao_parada`, `test_upload_gigante...` |
| 3 | Cadastros ilimitados por um mesmo endereço: qualquer visitante poderia criar contas e consumir CPU (scrypt) e disco | média | máximo de 60 cadastros por endereço em 15 min (cabe uma sala inteira atrás do mesmo IP); `429` com `Retry-After` | `test_cadastros_em_massa_do_mesmo_ip_sao_limitados` |
| 4 | Duas importações do mesmo slug ao mesmo tempo podiam deixar um backup temporário para trás e uma troca inconsistente | baixa | importação serializada por um trinco do processo | `test_replace_simultaneo_so_um_vence` |
| 5 | Métodos `OPTIONS` e `PATCH` caíam na página de erro padrão (HTML, sem cabeçalhos de segurança) | informativa | respondem 405 em JSON, com os mesmos cabeçalhos, sem CORS | `test_sem_cors_e_metodos_extras_recusados` |

Tudo o que foi **tentado e falhou do lado do atacante** (testes em `tests/test_exploits.py`): ler o banco e o `.env` por `..`, `%2e%2e`, `%2f`, `%5c`, barras invertidas, NUL e duplo escape; listar diretórios; ler trilha desativada ou de outro slug; usar sessão de aluno em qualquer rota admin; escrever sem CSRF, com token de outra sessão, com token pré-login ou por formulário externo; fixar a sessão; burlar o limite com `X-Forwarded-For`; derrubar o servidor com senha de 100 mil caracteres; SQL injection em e-mail, senha, slug, ids e admin; `<script>` em nome e e-mail; dez tipos de zip malicioso (zip-slip, caminho absoluto, link simbólico, SVG, HTML, script em markdown, `javascript:` em JSON, zip bomb, arquivo que não é zip, sem pasta de topo); importar sem ser admin ou sem CSRF; upload de 500 MB declarado.

Verificado **no navegador** (servidor real): trilha com `<script>`, `<img onerror>`, `javascript:` e imagem externa no markdown não executa nada nem carrega nada de fora; links `javascript:` e `//host` viram texto; a interface administrativa não tem script inline nem `innerHTML`.

## 5. Riscos residuais

1. **Sem HTTPS no servidor.** Em rede local (`--lan`), senhas e cookies trafegam em texto claro. Mitigação: proxy reverso com HTTPS e `K_STUDY_HTTPS=1`; só use `--lan` em rede de confiança.
2. **Enumeração de contas por `POST /api/auth/check`:** a tela de entrada precisa saber se o e-mail já tem conta. Não há contagem de chamadas de `check` (só bloqueio quando o e-mail ou o endereço já estão no limite de falhas). Mitigação: uso em grupo de confiança.
3. **Quem cadastra primeiro com um e-mail é o dono dele** (não há confirmação por e-mail). A conta antiga sem senha (migração) pode ser "reivindicada" por quem informar o e-mail primeiro. Mitigação: `reset-password` pelo dono do servidor e uso em grupo de confiança.
4. **Atrás de um proxy,** todos os clientes aparecem com o IP do proxy e compartilham os limites de tentativa (o servidor não confia em `X-Forwarded-For`, de propósito).
5. **Negação de serviço:** o scrypt custa cerca de 100 ms de CPU por tentativa de login; há limite por e-mail e por endereço, mas uma botnet distribuída pode saturar. O upload de zip (até 100 MB) é lido para a memória (só admin). O `audit_log` e as visitas crescem sem rotação.
6. **Conteúdo importado é confiável para o administrador, não para o navegador:** o markdown é escapado e a CSP bloqueia scripts, mas a defesa depende do `marked` configurado em `web/app.js` e da CSP; mudanças ali exigem repetir os testes de conteúdo hostil.
7. **`marked` 12.0.2** não é a versão mais recente; sem consulta a um banco de avisos nesta auditoria.
8. **Provedor externo:** quem controla a conta Google de uma pessoa controla a conta dela no k_study (entra pelo e-mail verificado). Vale para quem usa o botão; contas só com senha seguem protegidas pela senha.
9. **Segredo no `.env`:** quem lê o arquivo e o banco pode testar senhas offline (o `scrypt` ainda encarece cada tentativa). Perder o `.env` invalida todas as senhas.

## 6. Recomendações

- Publicar o servidor só atrás de **HTTPS** (proxy reverso) e com `K_STUDY_HTTPS=1`.
- **Backup do `.env` junto com o banco** (`data/k_study.db`); guarde-os em lugar com acesso restrito.
- **Rotacionar o segredo** (trocar `K_STUDY_SECRET`) invalida as senhas: se for necessário (vazamento), troque o valor, reinicie e use `kstudy reset-password EMAIL` para cada conta (ou peça redefinição a quem tem acesso ao computador).
- Atualizar o `marked` e conferir os avisos de segurança dele de tempos em tempos; manter o Python atualizado.
- Antes de publicar o repositório: decidir sobre os metadados de autoria, `materials/` e `transcripts/` (direitos de terceiros) e não versionar `.env`, `data/` nem áudios.
- Acrescentar `.env` ao `.gitignore` do k_transcriptor.
- Revisar o `audit_log` periodicamente (logins falhos em sequência, importações inesperadas).
