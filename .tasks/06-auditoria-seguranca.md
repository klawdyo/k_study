# 06 · Auditoria de segurança (OWASP) e varredura de segredos

**Depende de:** tarefas 01 a 05 **unidas** na branch de trabalho. Antes de começar, confira: `git log --oneline` mostra os commits delas e `py main.py serve` sobe com login por senha, CSRF e `/admin/`. Se não, pare e avise o usuário.

## Leia primeiro

`docs/arquitetura.md` (revisão 2, em especial as seções 5 a 10), `CLAUDE.md` e `.tasks/00-manifest.md` (regras gerais). Escopo: o k_study e o projeto irmão k_transcriptor (pasta `k_transcriptor` ao lado, repositório próprio).

## Parte 1 · Varredura de segredos (antes de qualquer publicação)

Nos DOIS repositórios, no que está versionado **e** em todo o histórico (`git log --all -p`, `git rev-list --all`), procure:
- chaves e tokens de IA (`sk-ant-`, `sk-`, `AIza`, `hf_`...); de nuvem e storage (AWS `AKIA`/`ASIA`, Azure, JSON de conta de serviço do GCP, S3, R2, Backblaze, Dropbox, Drive); de GitHub (`ghp_`, `github_pat_`); Slack (`xox`); Stripe; JWTs;
- chaves privadas (`-----BEGIN ... PRIVATE KEY-----`); senhas em URLs (`://usuario:senha@`); `.env`; bancos `.db`; cookies;
- e-mails e dados pessoais indevidos; caminhos pessoais (`C:\Users\...`); URLs internas.

Use `gitleaks` ou `trufflehog` se estiverem instalados; senão escreva um scanner em Python com expressões regulares e entropia (inclua os `transcripts` e todo o `content/`). Confirme que `.env`, `data/` e `*.db` estão no `.gitignore` e que NENHUM está rastreado. Relate cada achado com arquivo, linha e commit. Para achados reais, **não reescreva o histórico sozinho**: proponha o procedimento (reescrita do histórico e rotação do segredo) e peça autorização.

## Parte 2 · Auditoria de segurança completa

Leia TODO o código do servidor (`server.py`, `security.py`, `db.py`, `indexer.py`, `packages.py`, `cli.py`, `admin/queries.py`) e as interfaces (`web/`, `admin/web/`). Para cada categoria do OWASP Top 10 (2021), A01 a A10 (controle de acesso; falhas criptográficas; injeção, incluindo SQL, XSS, path traversal e zip-slip; design inseguro; configuração; componentes vulneráveis, conferindo a versão do `marked` vendorizado e outras dependências; autenticação; integridade; registro e monitoramento; SSRF), e ainda CSRF, CORS, cabeçalhos, cookies, rate limit, enumeração de usuários, fixação de sessão, upload de zip (zip bomb, zip-slip, symlink, extensão, conteúdo ativo), DoS por corpo grande e condições de corrida (primeiro admin, `replace` de trilha):

- Escreva **testes de exploração reais** (requisições HTTP contra um servidor de teste com banco e `.env` temporários) que tentam: acessar `/../../data/k_study.db`, `%2e%2e`, `%2f`, barras invertidas e NUL; ler conteúdo de outra trilha ou de outro aluno; usar sessão de aluno em rotas admin; escrever sem CSRF ou com token de outra sessão; forçar login sem limite; injetar `<script>` e `javascript:` em markdown, nomes e e-mails; enviar zips maliciosos; ler o `.env`.
- Cada falha encontrada: **corrija** (commit atômico `fix:` com teste) e registre.

## Entregáveis

`docs/seguranca.md` em português: modelo de ameaças; tabela OWASP A01 a A10 (controle existente, evidência ou teste, status); achados e correções; riscos residuais e recomendações (HTTPS, proxy reverso, backup do `.env` e do banco, rotação do segredo, atualização de dependências). Uma linha no `CLAUDE.md` apontando para ele. Suíte completa verde várias vezes.

## Aceite

Nenhum segredo versionado (ou procedimento proposto e aguardando o usuário); todos os testes de exploração falham do lado do atacante; `docs/seguranca.md` completo.

## Ao terminar

Atualize a linha 06 do manifesto e o "Registro" (achados, correções, riscos residuais e o que depende do usuário).
