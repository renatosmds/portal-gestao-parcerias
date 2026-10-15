from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.relatorios.catalogo import (
    CATALOGO_RELATORIOS,
)


class RelatoriosGenericosTest(TestCase):

    def setUp(self):

        User = get_user_model()

        self.superuser = (
            User.objects.create_superuser(
                username="relatorios_master",
                email="master@example.com",
                password="senha-forte",
            )
        )

        self.client.force_login(
            self.superuser
        )

    def test_todos_relatorios_abrem(self):

        for slug in CATALOGO_RELATORIOS:

            with self.subTest(
                slug=slug
            ):

                response = self.client.get(
                    reverse(
                        "relatorio_generico",
                        kwargs={
                            "slug": slug
                        },
                    )
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

    def test_todos_csvs_abrem(self):

        for slug in CATALOGO_RELATORIOS:

            with self.subTest(
                slug=slug
            ):

                response = self.client.get(
                    reverse(
                        "relatorio_generico_csv",
                        kwargs={
                            "slug": slug
                        },
                    )
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

                self.assertIn(
                    "text/csv",
                    response[
                        "Content-Type"
                    ],
                )

    def test_relatorio_exige_permissao_da_fonte(self):

        User = get_user_model()

        usuario = User.objects.create_user(
            username="relatorios_empresa",
            password="senha-forte",
        )

        permissao = Permission.objects.get(
            content_type__app_label="empresas",
            codename="view_empresa",
        )

        usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(
            usuario
        )

        response = self.client.get(
            reverse(
                "relatorio_generico",
                kwargs={
                    "slug": "empresas"
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response_sem_permissao = (
            self.client.get(
                reverse(
                    "relatorio_generico",
                    kwargs={
                        "slug": "pareceres"
                    },
                )
            )
        )

        self.assertEqual(
            response_sem_permissao.status_code,
            403,
        )

    def test_catalogo_e_permissoes_do_modulo_estao_alinhados(self):

        from apps.core.permissoes_modulos import MODULOS

        permissoes_modulo = set(
            MODULOS["relatorios"]
        )

        permissoes_catalogo = {
            cfg["permissao"]
            for cfg
            in CATALOGO_RELATORIOS.values()
        }

        self.assertTrue(
            permissoes_catalogo.issubset(
                permissoes_modulo
            )
        )
