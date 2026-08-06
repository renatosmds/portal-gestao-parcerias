from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from apps.core.acesso import filtrar_por_empresa, usuario_pode_ver_todas_empresas
from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.termos.models import Termos


class Sprint34IsolamentoTests(TestCase):
    def setUp(self):
        self.e1 = Empresa.objects.create(nome='OSC A')
        self.e2 = Empresa.objects.create(nome='OSC B')
        self.u = get_user_model().objects.create_user('osc_a', password='x')
        self.g, _ = Group.objects.get_or_create(name='Usuário da OSC')
        self.u.groups.add(self.g)
        Funcionario.objects.create(
            nome='Usuário OSC A', usuario='osc_a', endereco='-', bairro='-', cep='-',
            cidade='-', estado='MG', email='a@example.com', Telefone='-', user=self.u,
            empresa=self.e1, imagem='funcionarios_photos/teste.jpg'
        )
        self.t1 = Termos.objects.create(numtermo='1/2026', termo='Termo A', empresa=self.e1)
        self.t2 = Termos.objects.create(numtermo='2/2026', termo='Termo B', empresa=self.e2)

    def test_usuario_osc_nao_tem_visao_global(self):
        self.assertFalse(usuario_pode_ver_todas_empresas(self.u))

    def test_queryset_restringe_a_empresa_do_usuario(self):
        qs = filtrar_por_empresa(Termos.objects.all(), self.u)
        self.assertEqual(list(qs), [self.t1])

    def test_gestor_tem_visao_global(self):
        gestor = get_user_model().objects.create_user('gestor', password='x')
        grupo, _ = Group.objects.get_or_create(name='Gestor Municipal')
        gestor.groups.add(grupo)
        self.assertTrue(usuario_pode_ver_todas_empresas(gestor))
        self.assertEqual(filtrar_por_empresa(Termos.objects.all(), gestor).count(), 2)
