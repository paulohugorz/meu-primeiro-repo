from __future__ import annotations

import base64
import os
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


_TRUE_VALUES = {"1", "true", "yes", "on"}
_PUBLIC_EXACT_GET = {"/api/status", "/favicon.ico", "/telemetry.js"}
_PUBLIC_GET_PREFIXES = ("/p/",)


def _required() -> bool:
    return os.getenv("PILOT_ACCESS_REQUIRED", "").strip().lower() in _TRUE_VALUES


def _is_public_request(request: Request) -> bool:
    path = request.url.path
    method = request.method.upper()

    if method == "OPTIONS":
        return True

    if method in {"GET", "HEAD"}:
        if path in _PUBLIC_EXACT_GET:
            return True
        if any(path.startswith(prefix) for prefix in _PUBLIC_GET_PREFIXES):
            return True

    if method == "POST" and path == "/events/usage":
        return True

    return False


def _decode_basic_credentials(header: str | None) -> tuple[str, str] | None:
    if not header:
        return None
    try:
        scheme, encoded = header.split(" ", 1)
        if scheme.lower() != "basic":
            return None
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username, password
    except (ValueError, UnicodeDecodeError):
        return None


class PilotAccessMiddleware(BaseHTTPMiddleware):
    """Bloqueio provisório para piloto único; não substitui IAM multi-tenant."""

    async def dispatch(self, request: Request, call_next):
        if not _required() or _is_public_request(request):
            return await call_next(request)

        expected_user = os.getenv("PILOT_ACCESS_USER", "")
        expected_password = os.getenv("PILOT_ACCESS_PASSWORD", "")

        if not expected_user or not expected_password:
            return JSONResponse(
                status_code=503,
                content={"detail": "Acesso do piloto obrigatório, mas credenciais não configuradas."},
                headers={"Cache-Control": "no-store"},
            )

        credentials = _decode_basic_credentials(request.headers.get("Authorization"))
        if credentials:
            username, password = credentials
            if (
                secrets.compare_digest(username, expected_user)
                and secrets.compare_digest(password, expected_password)
            ):
                return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"detail": "Autenticação obrigatória."},
            headers={
                "WWW-Authenticate": 'Basic realm="PHYLLOS Pilot", charset="UTF-8"',
                "Cache-Control": "no-store",
            },
        )
