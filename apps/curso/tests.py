from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.curso.models import Curso


class CursoPermissoesTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create_user(
            username="usuario_curso",
            password="Teste@123",
        )

        self.curso = Curso.objects.create(
            nomeCurso="Curso de Teste",
            anoCurso="2026",
            mesCurso="01",
            cronograma="Janeiro",
            horario="08:00",
            carga="18",
            docente="Docente Teste",
            ementa="Ementa",
            obs="Observacao",
        )

        self.client.force_login(
            self.user
        )

    def conceder(self, codename):
        permissao = Permission.objects.get(
            content_type__app_label="curso",
            codename=codename,
        )

        self.user.user_permissions.add(
            permissao
        )

        self.user = self.User.objects.get(
            pk=self.user.pk
        )

        self.client.force_login(
            self.user
        )

    def test_listagem_exige_view(self):
        url = reverse("list_curso")

        self.assertEqual(
            self.client.get(url).status_code,
            403,
        )

        self.conceder(
            "view_curso"
        )

        self.assertEqual(
            self.client.get(url).status_code,
            200,
        )

    def test_cadastro_exige_add(self):
        url = reverse("create_curso")

        self.assertEqual(
            self.client.get(url).status_code,
            403,
        )

        self.conceder(
            "add_curso"
        )

        response = self.client.post(
            url,
            {
                "nomeCurso": "Novo Curso",
                "anoCurso": "2026",
                "mesCurso": "02",
                "cronograma": "Fevereiro",
                "horario": "09:00",
                "carga": "18",
                "docente": "Docente",
                "ementa": "Ementa",
                "obs": "Observacao",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_alteracao_exige_change(self):
        url = reverse(
            "update_curso",
            args=[self.curso.pk],
        )

        self.assertEqual(
            self.client.get(url).status_code,
            403,
        )

        self.conceder(
            "change_curso"
        )

        self.assertEqual(
            self.client.get(url).status_code,
            200,
        )

    def test_exclusao_exige_delete(self):
        url = reverse(
            "delete_curso",
            args=[self.curso.pk],
        )

        self.assertEqual(
            self.client.get(url).status_code,
            403,
        )

        self.conceder(
            "delete_curso"
        )

        self.assertEqual(
            self.client.get(url).status_code,
            200,
        )
