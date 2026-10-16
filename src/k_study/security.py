"""Segurança do k_study: .env, senhas, e-mail e nome, CSRF, limite de tentativas e cabeçalhos (docs/arquitetura.md, 5 e 6).

Apenas biblioteca padrão. Nada aqui imprime ou registra o segredo, senhas ou tokens.
"""
import base64
import hashlib
import hmac
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

SECRET_NAME = "K_STUDY_SECRET"
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 15, 8, 1
MIN_PASSWORD, MAX_PASSWORD = 8, 128
MAX_BODY = 1_000_000
PRE_COOKIE = "kstudy_pre"

# parte local: só caracteres "atext" do RFC 5322 (sem < > " ( ) , ; : \ [ ] nem espaços); domínio: letras, números e hífen
EMAIL = re.compile(r"^[\w.!#$%&'*+/=?^`{|}~\-]+@[\w\-]+(\.[\w\-]+)+$")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")

FAILS_PER_KEY, FAILS_PER_IP, WINDOW_SECONDS = 5, 30, 15 * 60
REGISTRATIONS_PER_IP = 60          # cadastros por endereço na janela (uma sala inteira atrás do mesmo IP cabe)

SECURITY_HEADERS = {
    "Content-Security-Policy": ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                                "img-src 'self' data:; frame-src https://www.youtube-nocookie.com https://www.youtube.com; "
                                "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


# ---- .env e segredo ------------------------------------------------------------------------------------------------

def parse_env(text: str) -> dict:
    """Parser de `CHAVE=valor` com comentários `#` e aspas opcionais."""
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def load_env(path: Path) -> None:
    """Carrega o .env para os.environ SEM sobrescrever variáveis já definidas."""
    path = Path(path)
    if not path.is_file():
        return
    for key, value in parse_env(path.read_text(encoding="utf-8")).items():
        os.environ.setdefault(key, value)


GOOGLE_ENV_BLOCK = """
# Entrada com o Google (opcional). Deixe as duas vazias para NÃO mostrar o botão "Entrar com o Google".
# Crie as credenciais em https://console.cloud.google.com/apis/credentials (ID do cliente OAuth, tipo "Aplicativo da Web").
# O endereço de retorno é fixo no sistema e NÃO se informa neste arquivo. É no Google que você o informa, em
# "URIs de redirecionamento autorizados": o endereço do servidor seguido de /auth/oauth/google/callback, por exemplo
#   http://localhost:8765/auth/oauth/google/callback
#   https://estudos.seudominio.com/auth/oauth/google/callback
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
"""


def ensure_secret(path: Path) -> str:
    """Devolve o segredo; cria o .env (0600 quando possível) se ele ou a chave não existirem.
    Ao escrever, deixa também GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET vazias (com o comentário de como configurar)."""
    path = Path(path)
    load_env(path)
    secret = os.environ.get(SECRET_NAME)
    if secret:
        return secret
    secret = secrets.token_hex(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    block = f"# k_study: segredo local. NUNCA versione este arquivo.\n{SECRET_NAME}={secret}\n"
    if "GOOGLE_CLIENT_ID" not in existing:
        block += GOOGLE_ENV_BLOCK
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(existing + block)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    os.environ[SECRET_NAME] = secret
    return secret


# ---- senhas --------------------------------------------------------------------------------------------------------

def _pepper(password: str, secret: str) -> bytes:
    return hmac.new(secret.encode("utf-8"), password.encode("utf-8"), hashlib.sha256).digest()


def _scrypt(material: bytes, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(material, salt=salt, n=n, r=r, p=p, maxmem=256 * 1024 * 1024, dklen=32)


def hash_password(password: str, secret: str) -> str:
    """Formato `scrypt$n$r$p$<sal b64>$<hash b64>`; scrypt sobre HMAC-SHA256(segredo, senha)."""
    salt = secrets.token_bytes(16)
    digest = _scrypt(_pepper(password, secret), salt, SCRYPT_N, SCRYPT_R, SCRYPT_P)
    return "$".join(["scrypt", str(SCRYPT_N), str(SCRYPT_R), str(SCRYPT_P),
                     base64.b64encode(salt).decode(), base64.b64encode(digest).decode()])


def verify_password(password: str, stored: str, secret: str) -> bool:
    """Comparação em tempo constante. Hash vazio ou malformado nunca confere."""
    try:
        scheme, n, r, p, salt, expected = (stored or "").split("$")
        if scheme != "scrypt":
            return False
        n, r, p = int(n), int(r), int(p)
        salt_bytes, expected_bytes = base64.b64decode(salt), base64.b64decode(expected)
        digest = _scrypt(_pepper(password, secret), salt_bytes, n, r, p)
    except (ValueError, TypeError, MemoryError):
        return False
    return hmac.compare_digest(digest, expected_bytes)


def needs_rehash(stored: str) -> bool:
    parts = (stored or "").split("$")
    return len(parts) != 6 or parts[1:4] != [str(SCRYPT_N), str(SCRYPT_R), str(SCRYPT_P)]


def dummy_verify(password: str, secret: str) -> None:
    """Gasta o mesmo tempo de uma verificação real (e-mail inexistente)."""
    _scrypt(_pepper(password, secret), b"\0" * 16, SCRYPT_N, SCRYPT_R, SCRYPT_P)


def check_password_policy(password, email: str = "") -> str | None:
    """Mensagem em português se a senha for recusada; None se estiver ok."""
    if not isinstance(password, str) or not (MIN_PASSWORD <= len(password) <= MAX_PASSWORD):
        return f"A senha deve ter de {MIN_PASSWORD} a {MAX_PASSWORD} caracteres."
    if email and password.strip().lower() == email.lower():
        return "A senha não pode ser igual ao e-mail."
    return None


# ---- e-mail e nome -------------------------------------------------------------------------------------------------

def normalize_email(text) -> str | None:
    email = text.strip().lower() if isinstance(text, str) else ""
    if len(email) > 254 or CONTROL.search(email) or email.count("@") != 1:
        return None
    return email if EMAIL.match(email) else None


def normalize_name(text) -> str | None:
    name = " ".join(text.split()) if isinstance(text, str) else ""
    return name if 1 <= len(name) <= 80 and not CONTROL.search(name) else None


# ---- CSRF ----------------------------------------------------------------------------------------------------------

def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def pre_token(secret: str, cookie_value: str) -> str:
    """Token CSRF antes do login: HMAC do valor do cookie `kstudy_pre`."""
    return hmac.new(secret.encode("utf-8"), b"pre:" + cookie_value.encode("utf-8"), hashlib.sha256).hexdigest()


def tokens_equal(a, b) -> bool:
    return isinstance(a, str) and isinstance(b, str) and bool(a) and hmac.compare_digest(a.encode(), b.encode())


# ---- limite de tentativas ------------------------------------------------------------------------------------------

def attempt_key(secret: str, email: str, ip: str) -> str:
    return hmac.new(secret.encode("utf-8"), f"{email}|{ip}".encode("utf-8"), hashlib.sha256).hexdigest()


def ip_key(secret: str, ip: str) -> str:
    return hmac.new(secret.encode("utf-8"), f"ip|{ip}".encode("utf-8"), hashlib.sha256).hexdigest()


def registration_key(secret: str, ip: str) -> str:
    return hmac.new(secret.encode("utf-8"), f"reg|{ip}".encode("utf-8"), hashlib.sha256).hexdigest()


def _stamp(moment: datetime) -> str:
    return moment.isoformat(timespec="seconds")


def retry_after(db, keys_limits: list[tuple[str, int]]) -> int:
    """Segundos até liberar (0 se ainda há tentativas). Cada item é (chave, limite de falhas na janela)."""
    now = datetime.now(timezone.utc)
    since = _stamp(now - timedelta(seconds=WINDOW_SECONDS))
    wait = 0
    for key, limit in keys_limits:
        rows = db.query("SELECT at FROM login_attempts WHERE key=? AND at>? ORDER BY at", (key, since))
        if len(rows) >= limit:
            oldest = datetime.fromisoformat(rows[len(rows) - limit]["at"])
            wait = max(wait, int(WINDOW_SECONDS - (now - oldest).total_seconds()) + 1)
    return wait


def record_failure(db, *keys: str) -> None:
    now = datetime.now(timezone.utc)
    with db.tx() as conn:
        conn.execute("DELETE FROM login_attempts WHERE at<?", (_stamp(now - timedelta(seconds=WINDOW_SECONDS)),))
        for key in keys:
            conn.execute("INSERT INTO login_attempts(key, at) VALUES(?,?)", (key, _stamp(now)))


def clear_failures(db, key: str) -> None:
    db.run("DELETE FROM login_attempts WHERE key=?", (key,))
