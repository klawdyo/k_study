# CLAUDE.md · k_study

> ⚠️ **NUNCA EDITE ESTE ARQUIVO.**  
> A única fonte da verdade para instruções e diretrizes de agentes neste repositório é [AGENTS.md](file:///f:/dev/Python/k_study/AGENTS.md).  
> Qualquer atualização, adição de regra ou mudança de contexto deve ser feita **exclusivamente no `AGENTS.md`**.  
> Este arquivo atua exclusivamente como ponteiro estático de entrada para o Claude.

---

## Resumo Operacional

- **Fonte da verdade absoluta:** Leia [AGENTS.md](file:///f:/dev/Python/k_study/AGENTS.md) antes de agir.
- **Idioma com a pessoa:** Sempre responda e interaja em **português do Brasil**.
- **Duas frentes de atuação:**
  1. **Criador de Trilhas (`content/<slug>/`):** Roda fora do servidor. Entrevista obrigatória em `specs/01-entrevista.md`. A entrega é a pasta validada e o pacote `<slug>.zip` gerado por `py main.py pack <slug>`. Você **não acessa o servidor de produção**.
  2. **Evolução do Sistema (`src/k_study/`):** O contrato técnico supremo é `docs/arquitetura.md`. O núcleo roda **exclusivamente com a biblioteca padrão do Python 3.10+** (zero dependências externas de produção).
- **Tarefas planejadas:** Se `.tasks/` existir, consulte `.tasks/00-manifest.md` e siga o fluxo de tarefas.
- **Segurança e regras:** SQL 100% parametrizado, sem rotas que sirvam arquivos por caminho de cliente, proteção CSRF em escrita, hashing com scrypt e segredo do `.env`.
- **Convenção de Idioma:** Código, nomes de variáveis/funções/classes e chaves JSON em inglês; especificações, documentação, interface, mensagens, comentários e docstrings em português do Brasil.
- **Comandos:** `py main.py validate [slug]`, `py main.py pack <slug>`, `py main.py serve --port 8765`, `py -m pytest tests/`.

Para o mapa completo de arquivos, regras inegociáveis de conteúdo e padrões de desenvolvimento, consulte [AGENTS.md](file:///f:/dev/Python/k_study/AGENTS.md).
