import logging

from django.shortcuts import render


logger = logging.getLogger("django.request")


def bad_request(request, exception=None):
    return render(request, "errors/400.html", status=400)


def permission_denied(request, exception=None):
    return render(request, "errors/403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "errors/404.html", status=404)


def server_error(request):
    logger.exception(
        "Erro interno nao tratado em %s",
        request.path,
    )

    return render(request, "errors/500.html", status=500)