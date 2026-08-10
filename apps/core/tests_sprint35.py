from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PaginasCriticasSprint35Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.usuario = User.objects.create_user(
            username="teste_sprint35",
            password="SenhaTeste123!",
            is_staff=True,
            is_superuser=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def verificar_rota(self, nome, url):
        response = self.client.get(url)

        self.assertNotEqual(
            response.status_code,
            500,
            msg=f"{nome} retornou erro 500 em {url}",
        )

    def test_paginas_criticas(self):
        rotas = [
            ("Home", "/"),
            ("OSCs / Empresas", "/empresa/"),
            ("Cursos", "/curso/list/"),
            ("Funcionarios", "/funcionarios/"),
            ("Departamentos", "/departamentos/"),
            ("Documentos", "/documentos/"),
            ("Diligencias", "/diligencias/"),
            ("Fornecedores", "/fornecedor/"),
            ("Termos", "/termos/"),
            ("Prestacoes", "/prestacao/"),
            ("Receitas", "/receitas/"),
            ("Analise", "/analise/"),
            ("Conciliacao", "/conciliacao/"),
            ("Metas", "/metas/"),
            ("Lancamentos", "/lancamentos/"),
            ("Importacoes", "/importacoes/"),
            ("Parcerias", "/parcerias/"),
        ]

        for nome, url in rotas:
            with self.subTest(nome=nome, url=url):
                self.verificar_rota(nome, url)

    def test_health_check(self):
        response = self.client.get(
            "/health/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "application": "ok",
                "database": "ok",
            },
        )