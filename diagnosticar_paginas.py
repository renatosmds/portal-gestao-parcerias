import traceback

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.empresas.views import EmpresaList
from apps.curso.views import CursoList


User = get_user_model()

usuario, _ = User.objects.get_or_create(
    username="diagnostico_temporario",
    defaults={
        "email": "diagnostico@localhost",
        "is_staff": True,
        "is_superuser": True,
    },
)

usuario.is_staff = True
usuario.is_superuser = True
usuario.save()

factory = RequestFactory()

testes = [
    ("OSCs / Empresas", "/empresa/", EmpresaList),
    ("Cursos", "/curso/list/", CursoList),
]

for titulo, url, view_class in testes:
    print("\n" + "=" * 70)
    print(titulo)
    print("URL:", url)
    print("VIEW:", view_class.__name__)

    request = factory.get(url)
    request.user = usuario

    try:
        response = view_class.as_view()(request)

        if hasattr(response, "render"):
            response.render()

        print("STATUS:", response.status_code)

    except Exception:
        traceback.print_exc()

usuario.delete()

print("\nDiagnóstico finalizado.")
