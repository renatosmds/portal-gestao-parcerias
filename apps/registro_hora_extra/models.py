from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from apps.funcionarios.models import Funcionario
from apps.empresas.models import Empresa



class RegistroHoraExtra(models.Model):

    class Meta:
        ordering = ["motivo"]

    MOTIVO_CHOICES = (

        (u'reunião', u'Reunião'),
        (u'particular', u'Particular'),
        (u'outros', u'Outros'),

    )
    motivo = models.CharField(max_length=100, choices=MOTIVO_CHOICES, null=True, blank=True, verbose_name='Motivo')
    assunto = models.CharField(max_length=100, null=True, blank=True, verbose_name='Assunto')
    funcionario = models.CharField(max_length=100, null=True, blank=True, verbose_name='Assunto')
    horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    utilizada = models.BooleanField(default=False, null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT) #, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('update_hora_extra', args=[self.registro_re.id])

    def __str__(self):
        return str(self.motivo)
