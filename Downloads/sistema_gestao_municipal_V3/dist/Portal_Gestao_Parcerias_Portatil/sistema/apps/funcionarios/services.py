from __future__ import annotations

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify


def get_empresa_do_usuario(user):
    """
    Retorna a empresa associada ao funcionário autenticado.

    Em vez de deixar o sistema falhar com AttributeError/RelatedObjectDoesNotExist,
    apresenta uma negação de acesso controlada quando o usuário não possui
    funcionário ou empresa vinculada.
    """
    if not user or not user.is_authenticated:
        raise PermissionDenied("É necessário estar autenticado.")

    try:
        funcionario = user.funcionario
    except Exception as exc:
        raise PermissionDenied(
            "O usuário autenticado não possui funcionário vinculado."
        ) from exc

    if not funcionario.empresa_id:
        raise PermissionDenied(
            "O funcionário autenticado não possui empresa vinculada."
        )

    return funcionario.empresa


def gerar_username_unico(nome_base: str) -> str:
    """
    Gera um username válido e único a partir do campo 'usuario'.

    Exemplos:
        Maria Silva -> maria
        Maria Souza, quando 'maria' já existe -> maria2
    """
    primeiro_nome = (nome_base or "").strip().split(" ")[0]
    base = slugify(primeiro_nome) or "usuario"
    base = base[:140]

    username = base
    contador = 2

    while User.objects.filter(username=username).exists():
        sufixo = str(contador)
        username = f"{base[:150 - len(sufixo)]}{sufixo}"
        contador += 1

    return username


def criar_usuario_para_funcionario(nome_base: str) -> User:
    username = gerar_username_unico(nome_base)
    user = User(username=username)
    user.set_unusable_password()
    user.save()
    return user
