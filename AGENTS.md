# AGENTS.md · k_study

> **Fonte da verdade para todos os agentes de IA.**  
> Este documento é o ponto de entrada canônico e a **única fonte da verdade** para qualquer agente autônomo (Claude, Gemini, Antigravity, OpenCode, Codex, Devin, Cursor, Copilot, etc.) trabalhando no repositório **k_study**.  
> Todos os arquivos específicos de agentes (`CLAUDE.md`, `GEMINI.md`, `ANTIGRAVITY.md`, `OPENCODE.md`) apontam para este guia.
>
> ⚠️ **REGRA DE MANUTENÇÃO:** **NUNCA altere os arquivos satélites (`CLAUDE.md`, `GEMINI.md`, `ANTIGRAVITY.md`, `OPENCODE.md`).**  
> Toda e qualquer evolução de regras, fluxo, comandos, arquitetura ou instruções deve ser registrada **exclusivamente neste arquivo (`AGENTS.md`)**. Mantenha sempre e apenas o `AGENTS.md` atualizado.

O **k_study** é um servidor local de **trilhas de aprendizagem** (cursos com vídeos, leituras e questões). O projeto envolve duas frentes de atuação distintas:

1. **Criador de Trilhas (Conteúdo):** O agente roda **fora do servidor, no computador da pessoa**. Cria a pasta `content/<slug>/`, valida com `kstudy validate` e gera o pacote `.zip` com `kstudy pack <slug>` para importação pelo administrador em `/admin/`.
2. **Desenvolvedor do Sistema (Código):** O agente evolui o servidor, CLI, banco, segurança ou interfaces em `src/k_study/`. O núcleo utiliza **apenas a biblioteca padrão do Python 3.10+** (zero dependências externas de produção).

> **Comunicação:** Sempre responda e interaja com a pessoa em **português do Brasil**.

---

## 1. Mapa de Navegação do Repositório

| Caminho | O que é | Quando consultar |
|---|---|---|
| `specs/00-visao-geral.md` | Visão geral do pipeline, ambiente e premissas | Antes de qualquer ação de criação de trilha |
| `specs/01-entrevista.md` | Roteiro obrigatório de entrevista | Ao receber pedido de criação de trilha |
| `specs/02-estrutura-do-conteudo.md` | Organização de blocos, itens e arquivos | Ao planejar a estrutura da trilha |
| `specs/03-pipeline-de-geracao.md` | Fases do pipeline de geração | Durante a execução passo a passo |
| `specs/04` a `06` | Vídeos (k_transcriptor), leituras e questões | Ao produzir cada tipo de conteúdo |
| `specs/07-validacao-e-qualidade.md` | Critérios de validação, qualidade e empacotamento zip | Antes e durante o empacotamento |
| `specs/08-servidor-e-admin.md` | Como o servidor funciona (contas, admin) | Para entender o fluxo de importação e uso |
| `specs/09-templates.md` | Modelos de arquivos de conteúdo | Ao criar novos arquivos de trilha |
| `docs/arquitetura.md` | **O contrato técnico supremo do sistema** | Antes de alterar qualquer código, rota, banco ou CLI |
| `docs/modelo-de-dados.md` | Esquema exato de arquivos de conteúdo | Ao gerar ou manipular arquivos de trilhas |
| `docs/seguranca.md` | Auditoria OWASP, modelo de ameaças e CSRF | Ao mexer em autenticação, rotas ou banco |
| `src/k_study/` | Código-fonte do servidor, segurança, web e CLI | Ao desenvolver ou dar manutenção no sistema |
| `content/aprendizagem-de-maquina/` | Trilha de referência real e completa | Para calibrar o nível de qualidade e profundidade |
| `.tasks/00-manifest.md` | Registro e manifesto de tarefas em andamento | Ao dar continuidade ao desenvolvimento do repositório |

---

## 2. Frente 1: Criação de Trilhas de Conteúdo

Se a pessoa solicitou a criação de uma trilha de aprendizagem:

1. **Você não acessa o servidor nem o banco de dados:** Seu produto final é a pasta `content/<slug>/` e o arquivo `<slug>.zip`. O administrador o importa pela interface web em `/admin/`.
2. **Ordem de leitura obrigatória:**
   - `specs/00-visao-geral.md`
   - `specs/01-entrevista.md`
   - `specs/02-estrutura-do-conteudo.md`
   - `specs/03-pipeline-de-geracao.md`
   - Consulte `specs/04` (vídeos), `05` (leituras), `06` (questões), `07` (qualidade e zip), `08` e `09`.
   - Consulte `docs/modelo-de-dados.md` para o formato exato dos arquivos.
   - Use `content/aprendizagem-de-maquina/` como exemplo de excelência.
3. **Regras inegociáveis de conteúdo:**
   1. Não crie nada antes da entrevista aprovada; grave as decisões em `content/<slug>/brief.md`.
   2. Depois da aprovação, seja autônomo: decida, registre e siga; só pare se bloqueado.
   3. Nunca invente fato, timestamp, número, referência ou o que um vídeo diz.
   4. Vídeo só entra depois de **ler a transcrição inteira**; nunca decida pelo título; todo `mm:ss` deve existir na transcrição.
   5. Nunca remova um vídeo nem rode `ktr clean` sem ler a transcrição e registrar o veredito na ficha.
   6. Um vídeo bom por tópico; o mais didático para o nível da pessoa; só remova duplicado com 100% de certeza.
   7. Leitura do zero (350 a 700 linhas, cobertura 100% declarada, código testado/executado, sem LaTeX, sem callouts, sem emojis); nada atribuído ao material que ele não diga.
   8. Toda alternativa de questão tem explicação detalhada com o porquê; sem citar alternativa por letra ("A", "B"); gabaritos conferidos.
   9. Nunca altere IDs já publicados, o banco (`data/k_study.db`) nem o progresso de alunos; nunca embaralhe questões já respondidas.
   10. Não copie material de terceiros literalmente (slides, figuras, livros); `validate` OK **não** prova qualidade: faça a auditoria completa de `specs/07`.
   11. O pacote zip segue **exatamente** as regras de `specs/07` (uma pasta de topo `<slug>/`, extensões permitidas, sem HTML, JS, SVG nem links simbólicos); nunca ponha segredos, `.env`, banco ou áudio nele.

---

## 3. Frente 2: Evolução do Código do Sistema

Se a pessoa pediu melhorias, correções ou recursos no software `k_study`:

1. **O Contrato Manda:** `docs/arquitetura.md` é a fonte da verdade. Se precisar alterar rota, tabela de banco, comando ou modelo, atualize a documentação primeiro e o código em seguida (`docs/modelo-de-dados.md`, `specs/`, `README.md`).
2. **Biblioteca Padrão Estrita:** O servidor de produção roda exclusivamente com a biblioteca padrão do Python (3.10+). Nunca adicione dependências ao `dependencies` do `pyproject.toml`.
3. **Segurança:**
   - Consultas SQL 100% parametrizadas (`sqlite3`).
   - Nenhuma rota serve arquivos por caminho arbitrário fornecido pelo cliente (proteção contra path traversal).
   - Toda mutação de estado (POST/PUT/DELETE) exige CSRF token.
   - Senhas criptografadas exclusivamente com `hashlib.scrypt` e o segredo do `.env` (nunca versionado).
   - Sem frameworks no front-end, sem `innerHTML` com dados externos, sem scripts inline (CSP estrita).
4. **Tarefas Planejadas:** Se `.tasks/` existir, consulte `.tasks/00-manifest.md`, respeite o fluxo de trabalho e registre o progresso.
5. **Testes:** Rode os testes antes de commitar:
   ```bash
   pip install -e ".[dev]"
   py -m pytest tests/
   ```
   Se alterar API ou validador, garanta testes de contrato.
6. **Commits e Versionamento:**
   - Conventional Commits atômicos (tipo em inglês, descrição em português no imperativo: `feat: adiciona ...`, `fix: corrige ...`).
   - A versão do projeto é calculada pelos commits: não edite à mão.
   - **Nunca registre breaking change** (`!` ou `BREAKING CHANGE:`) sem autorização prévia e explícita do usuário.
   - **Nunca execute push** nem altere repositórios remotos sem autorização explícita da pessoa.
7. **Dados Reais:** Não comite dados reais (`content/` com material de terceiros, transcrições ou banco) em repositórios públicos.

---

## 4. Convenção de Idioma

- **Em inglês:** Nomes de arquivos de código, módulos, classes, funções, variáveis, tabelas e colunas de banco, chaves JSON, comandos e opções de CLI, códigos de erro da API.
- **Em português do Brasil:** Especificações (`specs/`), documentação (`docs/`, `README.md`), interface gráfica, mensagens vistas por pessoas (saída e erros do CLI, `--help`, erros de API), comentários e docstrings no código, e comunicação direta com o usuário.

---

## 5. Comandos Frequentes

Dentro do repositório, execute com `py main.py <comando>` (Windows) ou `python3 main.py <comando>` (Linux/macOS), ou `kstudy <comando>` se instalado em modo editável:

```bash
# Conteúdo e Trilhas
py main.py new-trail SLUG --title "Título" [--description "Descrição"]   # Cria esqueleto content/<slug>/
py main.py validate [slug]       # Validação (erros reprovam; avisos alertam)
py main.py pack SLUG [--out F]   # Valida e empacota em .zip pronto para importação
py main.py import-trail ZIP [--replace]   # Importa pacote localmente

# Servidor e Administração
py main.py serve [--port 8765] [--lan] [--content-dir D] [--db F] [--env F]   # Alunos em /, admin em /admin/
py main.py sync                          # Sincroniza trilhas do diretório content/
py main.py trails                        # Lista trilhas disponíveis
py main.py set-admin EMAIL               # Concede permissão de administrador
py main.py reset-password EMAIL          # Redefine senha de conta
py main.py import-progress --email E --trail SLUG ARQ.json  # Importa progresso de aluno

# Transcrições (k_transcriptor)
ktr search|transcribe|text|queue|clean ...
```

**Códigos de saída do CLI:**
- `0`: Sucesso.
- `1`: Problemas de validação de conteúdo.
- `2`: Erro de uso ou de ambiente.
