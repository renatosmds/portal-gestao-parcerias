from django.db import models


class Teste(models.Model):
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_antiga_teste'

class RegistroUsuarios(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    idade = models.IntegerField()
    salario = models.DecimalField(decimal_places=2, max_digits=7)

    class Meta:
        managed = False
        db_table = 'registro_usuarios'
