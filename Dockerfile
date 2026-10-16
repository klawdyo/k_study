# k_study em contêiner. Só biblioteca padrão do Python: não há nada para instalar além do próprio Python.
#
#   docker build -t k_study .
#   docker run -d --name k_study -p 8765:8765 -v k_study_data:/data k_study
#
# Abra http://localhost:8765/ : o primeiro cadastro vira administrador.
# Tudo o que precisa sobreviver fica no volume /data: banco, .env (segredo) e as trilhas importadas (/data/content).
# Entrada com o Google (opcional): -e GOOGLE_CLIENT_ID=... -e GOOGLE_CLIENT_SECRET=...  (veja .env.example)
# Atrás de um domínio com HTTPS (proxy reverso): -e K_STUDY_ALLOWED_HOSTS=estudos.seudominio.com -e K_STUDY_HTTPS=1
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    K_STUDY_HOST=0.0.0.0 \
    K_STUDY_CONTENT=/data/content \
    K_STUDY_DB=/data/k_study.db \
    K_STUDY_ENV=/data/.env

WORKDIR /app

# o programa e os arquivos que o administrador baixa em "Baixar specs" (CLAUDE.md, specs/ e docs/modelo-de-dados.md)
COPY main.py ./
COPY src ./src
COPY CLAUDE.md ./
COPY specs ./specs
COPY docs/modelo-de-dados.md ./docs/modelo-de-dados.md

# usuário sem privilégios; /data é a única pasta gravável
RUN useradd --uid 10001 --no-create-home --home-dir /app --shell /usr/sbin/nologin kstudy \
    && mkdir -p /data/content \
    && chown -R kstudy:kstudy /data
USER kstudy

VOLUME /data
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8765/api/auth/me', timeout=3).status == 200 else 1)"]

CMD ["python", "main.py", "serve", "--port", "8765"]
