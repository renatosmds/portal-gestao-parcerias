from django.db import models
from django.urls import reverse

class Curso(models.Model):

    class Meta:
        ordering = ["nomeCurso"]

    CARGA_CHOICES = (u'18', u'18'), (u'20', u'20'), (u'24', u'24')

    MES_CHOICES = (u'01', u'01'), (u'02', u'02'), (u'03', u'03'), (u'04', u'04'), (u'05', u'05'), (u'06', u'06'), \
        (u'07', u'07'), (u'08', u'08'), (u'09', u'09'), (u'10', u'10'), (u'11', u'11'), (u'12', u'12')


    nomeCurso = models.CharField(max_length=100, verbose_name='Nome do Curso')
    anoCurso = models.CharField(max_length=4, verbose_name='Ano do Curso')
    mesCurso = models.CharField(max_length=5, choices=MES_CHOICES, verbose_name='Mês do Curso')
    cronograma = models.CharField(max_length=50, verbose_name='Cronograma')
    horario = models.CharField(max_length=25, verbose_name='Horário')
    carga = models.CharField(max_length=5, choices=CARGA_CHOICES, verbose_name='Carga Horária')
    docente = models.CharField(max_length=100, verbose_name='Docente')
    ementa = models.TextField(verbose_name='Ementa do Curso')
    obs = models.TextField(verbose_name='Observações')
    certificado = models.ImageField(upload_to='imagens/img_curso', null=True, blank=True,
                                    verbose_name='Certificados (.jpg/.jpeg)')
    documento = models.FileField(upload_to='imagens/doc_curso', null=True, blank=True,
                                 verbose_name='Documentos (.pdf/.doc/.xml)')

    def get_absolute_url(self):
        return reverse('list_curso')


    def __str__(self):
        return self.nomeCurso