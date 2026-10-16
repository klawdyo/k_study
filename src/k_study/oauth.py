"""Entrada com o Google (OAuth 2.0 / OpenID Connect, fluxo de código com PKCE). Apenas biblioteca padrão.

O botão só existe quando GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET estão preenchidos no ambiente (.env).
O endereço de retorno é FIXO no sistema (`/auth/oauth/google/callback`): ele não vai no .env; quem configura o Google
informa lá, em "URIs de redirecionamento autorizados", o endereço do servidor + esse caminho.

Segurança: `state` e PKCE guardados num cookie assinado (HMAC com o segredo do servidor) e `nonce` conferido no
id_token; o id_token chega direto do endpoint de token do Google por TLS, e mesmo assim `aud`, `iss`, `exp`,
`nonce` e `email_verified` são conferidos. As únicas requisições de saída vão a endereços fixos do Google.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

CALLBACK_PATH = "/auth/oauth/google/callback"
START_PATH = "/auth/oauth/google/start"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ISSUERS = ("https://accounts.google.com", "accounts.google.com")
STATE_COOKIE = "kstudy_oauth"
STATE_SECONDS = 600
UNUSABLE_HASH = "oauth$google"          # nunca confere como senha e não é "conta sem senha" (não pode ser reivindicada)

MESSAGES = {                              # mensagens fixas: nada vindo da URL é mostrado
    "denied": "Você cancelou a entrada com o Google.",
    "invalid_state": "A entrada com o Google expirou ou foi interrompida. Tente de novo.",
    "failed": "Não foi possível entrar com o Google. Tente de novo ou use e-mail e senha.",
    "unverified": "O Google informa que o e-mail dessa conta não foi verificado.",
    "not_configured": "A entrada com o Google não está configurada neste servidor.",
    "too_many": "Muitas tentativas. Aguarde alguns minutos e tente de novo.",
}


class OAuthError(Exception):
    """Falha na troca ou na validação; `code` é uma chave de MESSAGES."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def google_config(environ=None) -> dict | None:
    """{'client_id', 'client_secret'} se as duas variáveis estiverem preenchidas; senão None (sem botão)."""
    env = os.environ if environ is None else environ
    client_id, client_secret = (env.get("GOOGLE_CLIENT_ID") or "").strip(), (env.get("GOOGLE_CLIENT_SECRET") or "").strip()
    return {"client_id": client_id, "client_secret": client_secret} if client_id and client_secret else None


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def new_flow() -> dict:
    """state, nonce e verificador PKCE de uma tentativa de entrada."""
    return {"state": secrets.token_urlsafe(24), "nonce": secrets.token_urlsafe(24), "verifier": secrets.token_urlsafe(48)}


def sign_flow(flow: dict, secret: str, now: float | None = None) -> str:
    payload = _b64(json.dumps({**flow, "exp": int((now or time.time()) + STATE_SECONDS)}).encode())
    mac = hmac.new(secret.encode("utf-8"), b"oauth:" + payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{mac}"


def read_flow(cookie: str | None, secret: str, now: float | None = None) -> dict | None:
    """O fluxo guardado no cookie, ou None se faltar, estiver adulterado ou vencido."""
    try:
        payload, mac = (cookie or "").split(".")
        good = hmac.new(secret.encode("utf-8"), b"oauth:" + payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, good):
            return None
        flow = json.loads(_unb64(payload))
    except (ValueError, TypeError):
        return None
    if not isinstance(flow, dict) or flow.get("exp", 0) < (now or time.time()):
        return None
    return flow if all(isinstance(flow.get(k), str) for k in ("state", "nonce", "verifier")) else None


def authorization_url(client_id: str, redirect_uri: str, flow: dict) -> str:
    challenge = _b64(hashlib.sha256(flow["verifier"].encode()).digest())
    query = urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code", "scope": "openid email profile",
        "state": flow["state"], "nonce": flow["nonce"], "code_challenge": challenge, "code_challenge_method": "S256",
        "prompt": "select_account"})
    return f"{AUTH_URL}?{query}"


def validate_claims(claims: dict, client_id: str, nonce: str, now: float | None = None) -> dict:
    """Confere o id_token já decodificado. Devolve {'email', 'name'} ou levanta OAuthError."""
    aud = claims.get("aud")
    audiences = aud if isinstance(aud, list) else [aud]
    if client_id not in audiences or claims.get("iss") not in ISSUERS:
        raise OAuthError("failed")
    if not isinstance(claims.get("exp"), (int, float)) or claims["exp"] < (now or time.time()):
        raise OAuthError("failed")
    if not isinstance(claims.get("nonce"), str) or not hmac.compare_digest(claims["nonce"], nonce):
        raise OAuthError("invalid_state")
    if claims.get("email_verified") not in (True, "true"):
        raise OAuthError("unverified")
    email = claims.get("email")
    if not isinstance(email, str) or not email:
        raise OAuthError("failed")
    name = claims.get("name") if isinstance(claims.get("name"), str) else ""
    return {"email": email, "name": name}


def exchange_code(config: dict, code: str, redirect_uri: str, flow: dict) -> dict:
    """Troca o código pelo id_token no endpoint de token do Google (endereço fixo) e valida. Devolve {'email', 'name'}."""
    data = urllib.parse.urlencode({
        "code": code, "client_id": config["client_id"], "client_secret": config["client_secret"], "redirect_uri": redirect_uri,
        "grant_type": "authorization_code", "code_verifier": flow["verifier"]}).encode()
    request = urllib.request.Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read(1_000_000).decode("utf-8"))
        token = body["id_token"]
        claims = json.loads(_unb64(token.split(".")[1]))
    except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError, AttributeError):
        raise OAuthError("failed")
    return validate_claims(claims, config["client_id"], flow["nonce"])
