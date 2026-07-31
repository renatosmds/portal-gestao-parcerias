"""Middlewares leves de segurança e auditoria do PGP."""
import logging
import time

from django.conf import settings

logger = logging.getLogger("pgp.audit")


class AuditRequestMiddleware:
    """Registra acessos relevantes sem armazenar conteúdo sensível de formulários."""

    SENSITIVE_PREFIXES = (
        "/admin/",
        "/diligencias/",
        "/documentos/",
        "/lancamentos/",
        "/prestacao/",
        "/relatorios/",
        "/funcionarios/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.monotonic()
        response = self.get_response(request)
        if request.path.startswith(self.SENSITIVE_PREFIXES) or request.method != "GET":
            user = getattr(request, "user", None)
            username = user.get_username() if user and user.is_authenticated else "anonimo"
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            ip = forwarded or request.META.get("REMOTE_ADDR", "-")
            elapsed_ms = round((time.monotonic() - started) * 1000)
            logger.info(
                "usuario=%s ip=%s metodo=%s caminho=%s status=%s duracao_ms=%s",
                username,
                ip,
                request.method,
                request.path,
                response.status_code,
                elapsed_ms,
            )
        return response


class SessionIdleTimeoutMiddleware:
    """Encerra sessões inativas quando PGP_SESSION_IDLE_MINUTES for configurado."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timeout_minutes = getattr(settings, "PGP_SESSION_IDLE_MINUTES", 0)
        if timeout_minutes and getattr(request, "user", None) and request.user.is_authenticated:
            now = int(time.time())
            last = request.session.get("pgp_last_activity", now)
            if now - last > timeout_minutes * 60:
                from django.contrib.auth import logout
                logout(request)
            else:
                request.session["pgp_last_activity"] = now
        return self.get_response(request)
