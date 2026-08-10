from django.db import connection
from django.http import JsonResponse


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse(
            {
                "status": "ok",
                "application": "ok",
                "database": "ok",
            },
            status=200,
        )

    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "application": "ok",
                "database": "error",
            },
            status=503,
        )